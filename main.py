import os
import time
import math
import bip39
from address_checker import AddressChecker
import breez_sdk
import cmd
from secrets_loader import load_secrets
from breez_sdk import LnUrlCallbackStatus, LnUrlPayResult, PaymentTypeFilter, ReverseSwapFeesRequest
from info_printer import InfoPrinter

# Name of the directory where the database & logs will be stored
DATA_DIR = 'data'

# SDK events listener
class SDKListener(breez_sdk.EventListener, InfoPrinter):
  def on_event(self, event):
    if isinstance(event, breez_sdk.BreezEvent.INVOICE_PAID):
      self._print_invoice_paid(event)
    elif isinstance(event, breez_sdk.BreezEvent.PAYMENT_SUCCEED):
      self._print_payment_succeeded(event)
    elif isinstance(event, breez_sdk.BreezEvent.PAYMENT_FAILED):
      self._print_payment_failed_data(event)


class Wallet(cmd.Cmd, InfoPrinter, AddressChecker):
  def __init__(self):
    super().__init__()
    InfoPrinter.__init__(self)
    AddressChecker.__init__(self)

    # Load secrets from file
    secrets = load_secrets('secrets.txt')

    # Create the default config
    mnemonic = secrets['phrase']
    invite_code = secrets['invite_code']
    api_key = secrets['api_key']
    seed = bip39.phrase_to_seed(mnemonic)

    config = breez_sdk.default_config(breez_sdk.EnvironmentType.PRODUCTION, api_key,
        breez_sdk.NodeConfig.GREENLIGHT(breez_sdk.GreenlightNodeConfig(None, invite_code)))

    # Creating the data directory if it doesn't exist already
    if not os.path.exists(DATA_DIR):
      os.makedirs(DATA_DIR)
    config.working_dir = os.getcwd() + '/' + DATA_DIR

    # Connect to the Breez SDK make it ready for use
    self.sdk_services = breez_sdk.connect(config, seed, SDKListener())
    self.prompt = 'wallet> '

  def do_info(self, arg):
    """Get node info"""
    try:
      node_info = self.sdk_services.node_info()
      lsp_id = self.sdk_services.lsp_id()
      lsp_info = self.sdk_services.fetch_lsp_info(lsp_id)
      self._print_node_info(node_info)
      self._print_lsp_info(lsp_info)
    except Exception as error:
      print('Error getting LSP info: ', error)

  def do_balance(self, arg):
    """Get balance"""
    # Logic to get balance
    node_info = self.sdk_services.node_info()
    ln_balance = node_info.channels_balance_msat
    onchain_balance = node_info.onchain_balance_msat
    print('*** Balances (msats) ***')
    print('⚡ Lightning : ', ln_balance)
    print('🔗 On-Chain  : ', onchain_balance)

  def do_get_deposit_address(self, arg):
    """Get deposit address (on-chain)"""
    # Logic to get deposit address (on-chain)
    swap_info = self.sdk_services.receive_onchain()
    self._print_swap_info(swap_info)

  def do_swap_progress(self, arg):
    """Get the progress of any in-progress swap"""
    try:
      swap_info = self.sdk_services.in_progress_swap()
      if swap_info:
        self._print_swap_info(swap_info)
      else:
        print('No in-progress swap')
    except Exception as error:
      print('Error getting swap progress: ', error)

  def do_list_refundables(self, arg):
    """List of refundable operations"""
    try:
      refundables = self.sdk_services.list_refundables()
      print(refundables)
    except Exception as error:
      print('Error getting refundables: ', error)

  def do_pay_address(self, arg):
    """Send funds (on-chain)
    Usage: pay_address <address> <amount>
    """
    current_fees = None
    if len(arg.split(' ')) < 3:
      print('Usage: pay_address <address> <amount> <fee_rate>')
      return
    [address, amount, fee_rate] = arg.split(' ')

    # Validate amount as an integer
    if not amount.isdigit() or int(amount) < 0:
      print('Amount must be a non-negative integer')
      return
    # Validate fee rate as an integer
    if not fee_rate.isdigit() or int(fee_rate) < 0:
      print('Fee rate must be a non-negative integer')
      return
    # Validate Bitcoin address
    if not self.is_valid_address(address):
      print(f'"{address}" is not a valid Bitcoin address')
      return
    # Converting amount & fee_rate to numeric values
    amount = int(amount)
    fee_rate = int(fee_rate)

    try:
      current_fees = self.sdk_services.fetch_reverse_swap_fees(ReverseSwapFeesRequest(amount))
      self._print_reverse_swap_pair_info(current_fees)
      if amount < current_fees.min:
        print(f'❌ Amount is less than minimum ({current_fees.min} sats)')
        return
      if amount > current_fees.max:
        print(f'❌ Amount is greater than maximum ({current_fees.max} sats)')
        return
    except Exception as error:
      print('Error getting fees: ', error)

    # Asks user for confirmation
    print('Do you agree to pay the fees detailed above? ☝️')
    print('Type "YES" to proceed, press any other key to cancel')
    user_input = input()
    if user_input.lower() != 'yes':
      print('Operation cancelled by user')
      return
    try:
      self.sdk_services.send_onchain(amount, address, current_fees.fees_hash, fee_rate)
    except Exception as error:
      print('Error sending on-chain: ', error)

  def do_reverse_swap_progress(self, arg):
    """Get the progress of any in-progress reverse swap"""
    try:
      reverse_swaps = self.sdk_services.in_progress_reverse_swaps()
      if len(reverse_swaps) == 0:
        print('🤷‍♂️ No in-progress reverse swaps')
        return
      for reverse_swap in reverse_swaps:
        self._print_reverse_swap_info(reverse_swap)
    except Exception as error:
      print('Error getting reverse swap progress: ', error)

  def do_get_invoice(self, arg):
    """Get lightning invoice (off-chain)
    Usage: get_invoice <amount> [memo]
    """
    memo = ''
    amount = arg.split(' ')[0]
    if not amount.isdigit() or int(amount) < 0:
      print('Amount must be a non-negative integer')
      return
    if len(arg.split(' ')) > 1:
      memo = ' '.join(arg.split(' ')[1:])
    print(f'Getting invoice for amount: {amount}')
    if memo:
        print(f'With memo: {memo}')
    try:
      request = breez_sdk.ReceivePaymentRequest(amount_sats=int(amount), description=memo, preimage=None,
                                                opening_fee_params=None)
      response = self.sdk_services.receive_payment(req_data=request)
      print('⚡️ Pay: ', response.ln_invoice.bolt11)
    except Exception as error:
      # Handle error
      print('error getting invoice: ', error)

  def do_pay_invoice(self, args):
    """Pay lightning invoice (off-chain)
    Usage: pay_invoice <invoice>
    """
    invoice = args.strip()
    print('Please wait... ⏳')
    try:
      self.sdk_services.send_payment(invoice, None)
    except Exception as error:
      # Handle error
      print('error paying invoice: ', error)

  def do_lnurl_withdraw(self, args):
    """Withdraw using LNURL-withdraw (off-chain)
    Usage: lnurl_withdraw <lnurl> <amount>
    """
    if len(args.split(' ')) != 2:
      print('Usage: lnurl_withdraw <lnurl> <amount>')
      return
    [lnurl, amount] = args.split(' ')[:2]
    print('\n=== Withdrawing using LNURL-withdraw ===')
    print(f'LNURL: {lnurl}')
    print('========================================')
    try:
      parsed_input = breez_sdk.parse_input(lnurl)
      if isinstance(parsed_input, breez_sdk.InputType.LN_URL_WITHDRAW):
        self.print_ln_url_withdraw_request_data(parsed_input.data)
        minimum = parsed_input.data.min_withdrawable
        maximum = parsed_input.data.max_withdrawable
        if amount is None:
          print(f'Please chose an amount in the range [{minimum} - {maximum}] msats')
          return
        amount_sats = int(amount)
        amount_msats = int(amount) * 1E3
        if amount_msats < minimum:
          print('Amount is less than minimum')
          return
        if amount_msats > maximum:
          print('Amount is greater than maximum')
          return
        print(f'⏳ *** Requesting a withdrawal of {amount_sats} sats ***')
        result = self.sdk_services.withdraw_lnurl(parsed_input.data, amount_sats, "withdrawing using lnurl")
        if isinstance(result, LnUrlCallbackStatus.OK):
          print(f'🎉 You successfully withdrew {amount_sats} sats!')
        elif isinstance(result, LnUrlCallbackStatus.ERROR):
          print('😔 Withdraw error: ', result)
      else:
        print('Invalid lnurl')
    except Exception as error:
      print('❌ Error withdrawing using lnurl: ', error)

  def do_lnurl_pay(self, args):
    """Pay using LNURL-pay (off-chain)
    Usage: lnurl_pay <url|ln_address> <amount> [memo]
    """
    [url, amount] = args.split(' ')[:2]
    memo = ' '.join(args.split(' ')[2:])
    print('\n=== Paying using LNURL-pay ===')
    print(f'URL.....: {url}')
    print(f'Amount..: {amount}')
    print(f'Memo....: {memo}')
    print('==============================')
    try:
      parsed_input = breez_sdk.parse_input(url)
      if isinstance(parsed_input, breez_sdk.InputType.LN_URL_PAY):
        min_sendable = parsed_input.data.min_sendable
        max_sendable = parsed_input.data.max_sendable
        sats_amount = int(amount)
        if sats_amount > max_sendable or sats_amount < min_sendable:
          print(f'Amount is out of range, make sure it is between {min_sendable} and {max_sendable}')
          return
        result = self.sdk_services.pay_lnurl(parsed_input.data, sats_amount, memo)
        if isinstance(result, LnUrlPayResult.ENDPOINT_SUCCESS):
          print('🎉 Payment successful!')
        elif isinstance(result, LnUrlPayResult.ENDPOINT_ERROR):
          print('😢 Payment failed!')
        else:
          print('Unknown result: ', result)
    except Exception as error:
      print('error paying lnurl-pay: ', error)

  def do_send(self, args):
    """Makes a spontaneous payment (off-chain) to a node
    Usage: send <node_id> <amount>
    """
    [node_id, _amount] = args.split(' ')
    amount = math.floor(float(_amount))
    try:
      self.sdk_services.send_spontaneous_payment(node_id, amount)
    except Exception as error:
      print('error sending payment: ', error)

  def do_txs(self, arg):
    """List transactions"""
    # Logic to list payments
    now = time.time()
    payments = self.sdk_services.list_payments(PaymentTypeFilter.ALL, 0, now)
    self._print_payments(payments)

  def do_exit(self, arg):
    """Exit the application."""
    print("Goodbye!")
    return True

if __name__ == '__main__':
  cli = Wallet()
  cli.cmdloop('Welcome to the Breez SDK Wallet!\n\nType `help` or `?` to list commands.')

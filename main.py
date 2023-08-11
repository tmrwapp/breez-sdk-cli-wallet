import os
import time
import math
import bip39
import breez_sdk
import cmd
from secrets_loader import load_secrets
from breez_sdk import PaymentTypeFilter, NodeState, LspInformation
from info_printer import InfoPrinter

# SDK events listener
class SDKListener(breez_sdk.EventListener):
   def on_event(self, event):
      pass
      # print(event)

class Wallet(cmd.Cmd, InfoPrinter):
  def __init__(self):
    super().__init__()

    # Load secrets from file
    secrets = load_secrets('secrets.txt')

    # Create the default config
    mnemonic = secrets['phrase']
    invite_code = secrets['invite_code']
    api_key = secrets['api_key']
    seed = bip39.phrase_to_seed(mnemonic)

    config = breez_sdk.default_config(breez_sdk.EnvironmentType.PRODUCTION, api_key,
        breez_sdk.NodeConfig.GREENLIGHT(breez_sdk.GreenlightNodeConfig(None, invite_code)))

    # Customize the config object according to your needs
    config.working_dir = os.getcwd()

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

  def do_get_balance(self, arg):
    """Get balance"""
    # Logic to get balance
    node_info = self.sdk_services.node_info()
    ln_balance = node_info.channels_balance_msat
    onchain_balance = node_info.onchain_balance_msat
    print('Lightning balance: ', ln_balance, ' millisatoshis, On-chain balance: ', onchain_balance, ' millisatoshis')

  def do_get_deposit_address(self, arg):
    """Get deposit address (on-chain)"""
    # Logic to get deposit address (on-chain)
    swap_info = self.sdk_services.receive_onchain()
    print('Bitcoin Address:', swap_info.bitcoin_address)
    print('Payment Hash:', bytes(swap_info.payment_hash).hex())
    print('Preimage:', bytes(swap_info.preimage).hex())
    print('Private Key:', bytes(swap_info.private_key).hex())
    print('Public Key:', bytes(swap_info.public_key).hex())
    print('Script:', bytes(swap_info.script).hex())
    print('Paid Satoshis:', swap_info.paid_sats)
    print('Unconfirmed Satoshis:', swap_info.unconfirmed_sats)
    print('Confirmed Satoshis:', swap_info.confirmed_sats)
    print('Status:', swap_info.status)
    print('Refund Transaction IDs:')
    for tx_id in swap_info.refund_tx_ids:
      print('  -', bytes(tx_id).hex())

    print('Unconfirmed Transaction IDs:')
    for tx_id in swap_info.unconfirmed_tx_ids:
      print('  -', bytes(tx_id).hex())

    print('Confirmed Transaction IDs:')
    for tx_id in swap_info.confirmed_tx_ids:
      print('  -', bytes(tx_id).hex())

  def do_send_funds(self, arg):
    # Logic to send funds (on-chain)
    pass

  def do_get_lightning_invoice(self, arg):
    """Get lightning invoice (off-chain)"""
    [amount, memo] = arg.split(' ')
    print(f'Getting invoice for amount: {amount}')
    if memo:
        print(f'With memo: {memo}')
    try:
      invoice = self.sdk_services.receive_payment(amount, f'Invoice for {amount} sats')
      print('pay: ', invoice.bolt11)
    except Exception as error:
      # Handle error
      print('error getting invoice: ', error)

  def do_pay_invoice(self, args):
    """Pay lightning invoice (off-chain)
    Usage: pay_invoice <invoice>
    """
    invoice = args.strip()
    print('\nPaying invoice.....: ', invoice)
    try:
      self.sdk_services.send_payment(invoice, None)
    except Exception as error:
      # Handle error
      print('error paying invoice: ', error)

  def do_send(self, args):
    """Makes a spontaneous payment to a node
    Usage: send <node_id> <amount>
    """
    [node_id, _amount] = args.split(' ')
    amount = math.floor(float(_amount))
    try:
      self.sdk_services.send_spontaneous_payment(node_id, amount)
    except Exception as error:
      print('error sending payment: ', error)

  def do_list_txs(self, arg):
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
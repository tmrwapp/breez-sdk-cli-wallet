import os
import time
import math
import bip39
import breez_sdk
import cmd
from secrets_loader import load_secrets
from breez_sdk import PaymentTypeFilter, NodeState, LspInformation

# SDK events listener
class SDKListener(breez_sdk.EventListener):
   def on_event(self, event):
      pass
      # print(event)

class Wallet(cmd.Cmd):
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

  def _print_node_info(self, node: NodeState) -> None:
    fmt_node_info = f"""
    === Node Information ===
    🆔 Node ID: {node.id}
    🏗️  Block Height: {node.block_height}
    💰 Channels Balance (msat): {node.channels_balance_msat}
    🧳 Onchain Balance (msat): {node.onchain_balance_msat}
    🪙 UTXOs: {node.utxos}
    💸 Max Payable (msat): {node.max_payable_msat}
    🧾 Max Receivable (msat): {node.max_receivable_msat}
    📦 Max Single Payment Amount (msat): {node.max_single_payment_amount_msat}
    🏦 Max Channel Reserve (msats): {node.max_chan_reserve_msats}
    👥 Connected Peers: {node.connected_peers}
    🌊 Inbound Liquidity (msats): {node.inbound_liquidity_msats}
    """
    print(fmt_node_info)

  def _print_lsp_info(self, lsp: LspInformation) -> None:
    lsp_pubkey_hex = bytes(lsp.lsp_pubkey).hex()
    lsp_info = f"""
    === LSP Information ===
    🆔  ID: {lsp.id}
    📛  Name: {lsp.name}
    🌐  Widget URL: {lsp.widget_url}
    🔑  Public Key: {lsp.pubkey}
    🏠  Host: {lsp.host}
    🎛️   Channel Capacity: {lsp.channel_capacity}
    🎯  Target Confirmation: {lsp.target_conf}
    💰  Base Fee (msat): {lsp.base_fee_msat}
    📈  Fee Rate: {lsp.fee_rate}
    ⏲️   Time Lock Delta: {lsp.time_lock_delta}
    📦  Min HTLC (msat): {lsp.min_htlc_msat}
    💸  Channel Fee per Myriad: {lsp.channel_fee_permyriad}
    🗝️   LSP Public Key: {lsp_pubkey_hex}
    🕒  Max Inactive Duration: {lsp.max_inactive_duration}
    💳  Channel Minimum Fee (msat): {lsp.channel_minimum_fee_msat}
    """
    print(lsp_info)

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

  def _print_payments(self, payments):
    # Print the headers
    print("ID\t\t\t\t\t\t\t\t  Type\t\t\t Time\t     [Amount & Fee](msat) Pending Description")
    print("="*150)

    # Print the details of each payment
    for payment in payments:
      print(f"{payment.id} | {payment.payment_type} | {payment.payment_time} | [{payment.amount_msat} {payment.fee_msat}] | {payment.pending} | {payment.description}")

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
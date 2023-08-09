import os
import time
import argparse
import bip39
import breez_sdk
from secrets_loader import load_secrets
from breez_sdk import PaymentTypeFilter

# Load secrets from file
secrets = load_secrets('secrets.txt')

# Global variable to hold the SDK services
sdk_services = None

def sync():
  # Logic to sync node
  sdk_services.sync()

def get_node_info():
  # Logic to get node info
  node_info = sdk_services.node_info()
  print(node_info)
  try: 
    lsp_id = sdk_services.lsp_id()
    lsp_info = sdk_services.fetch_lsp_info(lsp_id)
    print('LSP info: ', lsp_info)
  except Exception as error:
    print('Error getting LSP info: ', error)

def get_balance():
  # Logic to get balance
  node_info = sdk_services.node_info()
  ln_balance = node_info.channels_balance_msat
  onchain_balance = node_info.onchain_balance_msat
  print('Lightning balance: ', ln_balance, ' millisatoshis, On-chain balance: ', onchain_balance, ' millisatoshis')

def get_deposit_address():
  # Logic to get deposit address (on-chain)
  swap_info = sdk_services.receive_onchain()
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

def send_funds():
  # Logic to send funds (on-chain)
  pass

def get_lightning_invoice(amount, memo=None):
  print(f'Getting invoice for amount: {amount}')
  if memo:
      print(f'With memo: {memo}')
  try:
    invoice = sdk_services.receive_payment(amount, f'Invoice for {amount} sats')
    print('pay: ', invoice.bolt11)
  except Exception as error:
    # Handle error
    print('error getting invoice: ', error)

def pay_lightning_invoice():
  # Logic to pay a lightning invoice (off-chain)
  pass

def list_payments():
  # Logic to list payments
  now = time.time()
  payments = sdk_services.list_payments(PaymentTypeFilter.ALL, 0, now)
  print('txs: ', payments)

parser = argparse.ArgumentParser(description='Manage Greenlight node via Breez SDK.')
parser.add_argument('--sync', action='store_true', help='Sync node')
parser.add_argument('--info', action='store_true', help='Get node info')
parser.add_argument('--balance', action='store_true', help='Get balance')
parser.add_argument('--deposit-address', action='store_true', help='Get deposit address (on-chain)')
parser.add_argument('--send-funds', action='store_true', help='Send funds (on-chain)')
parser.add_argument('--get-invoice', action='store_true', help='Get a lightning invoice (off-chain)')
parser.add_argument('--amount', type=int, help='Amount for getting an invoice (required with --get-invoice)')
parser.add_argument('--memo', type=str, help='Optional memo for getting an invoice (used with --get-invoice)')
parser.add_argument('--pay-invoice', action='store_true', help='Pay a lightning invoice (off-chain)')
parser.add_argument('--list-payments', action='store_true', help='List payments')

args = parser.parse_args()

# SDK events listener
class SDKListener(breez_sdk.EventListener):
   def on_event(self, event):
      print(event)

def setup():
  global sdk_services
  global args
  # Create the default config
  mnemonic = secrets['phrase']
  invite_code = secrets['invite_code']
  api_key = secrets['api_key']
  seed = bip39.phrase_to_seed(mnemonic)

  config = breez_sdk.default_config(breez_sdk.EnvironmentType.PRODUCTION, api_key,
      breez_sdk.NodeConfig.GREENLIGHT(breez_sdk.GreenlightNodeConfig(None, invite_code)))

  # Customize the config object according to your needs
  config.working_dir = os.getcwd()

  try:
    # Connect to the Breez SDK make it ready for use
    sdk_services = breez_sdk.connect(config, seed, SDKListener())
  except Exception as error:
    # Handle error
    print('error: ', error)

  # Run the requested command
  if args.info:
    get_node_info()
  elif args.balance:
    get_balance()
  elif args.deposit_address:
    get_deposit_address()
  elif args.send_funds:
    send_funds()
  elif args.get_invoice:
    if args.amount is None:
      parser.error('--get-invoice requires --amount to be specified.')
    get_lightning_invoice(args.amount, args.memo)
  elif args.pay_invoice:
    pay_lightning_invoice()
  elif args.list_payments:
    list_payments()
  elif args.sync:
    sync()
  else:
    parser.print_help()


if __name__ == '__main__':
  setup()
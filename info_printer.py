from breez_sdk import NodeState, LspInformation, PaymentType
from flextable.table import FlexTable

class InfoPrinter():

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

  def _print_payments(self, payments):
    # Print the headers
    table = FlexTable(['ID', 'Type', 'Time', 'Amount (msat)', 'Fee (msat)','Pending', 'Description'])
    rows = []
    # Print the details of each payment
    for payment in payments:
      payment_type = 'Sent' if payment.payment_type == PaymentType.SENT else ('Received' if payment.payment_type == PaymentType.RECEIVED else 'Closed Channel')
      rows.append([payment.id, payment_type, payment.payment_time, f"{payment.amount_msat}", f"{payment.fee_msat}", payment.pending, payment.description])
    table.add_rows(rows)
    print(table.render())

  def print_ln_url_withdraw_request_data(self, data):
    print(f'🔗 Callback: {data.callback}')
    print(f'🔑 k1: {data.k1}')
    print(f'📄 Description: {data.default_description}')
    print(f'💰 Range: [{data.min_withdrawable} - {data.max_withdrawable}] msats')

  def _print_swap_info(self, swap_info):
    print('🔗 Swap Information:')
    print(f'  🏷️ Bitcoin Address: {swap_info.bitcoin_address}')
    print(f'  🗓️ Created At: {swap_info.created_at}')
    print(f'  🔒 Lock Height: {swap_info.lock_height}')
    print(f'  📦 Payment Hash: {bytes(swap_info.payment_hash).hex()}')
    print(f'  🔑 Preimage: {bytes(swap_info.preimage).hex()}')
    print(f'  🧊 Private Key: {bytes(swap_info.private_key).hex()}')
    print(f'  📝 Public Key: {bytes(swap_info.public_key).hex()}')
    print(f'  🔄 Swapper Public Key: {bytes(swap_info.swapper_public_key).hex()}')
    print(f'  📜 Script: {bytes(swap_info.script).hex()}')
    print(f'  ⚡ Bolt11: {swap_info.bolt11}')
    print(f'  💸 Paid Sats: {swap_info.paid_sats}')
    print(f'  🔄 Unconfirmed Sats: {swap_info.unconfirmed_sats}')
    print(f'  ✅ Confirmed Sats: {swap_info.confirmed_sats}')
    print(f'  🚦 Status: {swap_info.status}')
    print(f'  📑 Refund TX IDs')
    for tx_id in swap_info.refund_tx_ids:
      print('    -', tx_id)
    print(f'  🔄 Unconfirmed TX IDs')
    for tx_id in swap_info.unconfirmed_tx_ids:
      print('    -', tx_id)
    print(f'  ✅ Confirmed TX IDs')
    for tx_id in swap_info.confirmed_tx_ids:
      print('    -', tx_id)
    print(f'  ⬇️  Min Allowed Deposit: {swap_info.min_allowed_deposit}')
    print(f'  ⬆️  Max Allowed Deposit: {swap_info.max_allowed_deposit}')
    print(f'  ⚠️  Last Redeem Error: {swap_info.last_redeem_error}')

  def _print_reverse_swap_pair_info(self, info):
    print('🔄 Reverse Swap Pair Information:')
    print(f'⬇️  Min: {info.min} sats')
    print(f'⬆️  Max: {info.max} sats')
    print(f'🔑 Fees Hash: {info.fees_hash}')
    print(f'📊 Fees Percentage: {info.fees_percentage}')
    print(f'🔒 Fees Lockup: {info.fees_lockup}')
    print(f'🏷️  Fees Claim: {info.fees_claim}')

  def _print_reverse_swap_info(self, info):
    print('🔄 Reverse Swap Information:')
    print(f'🆔 ID: {info.id}')
    print(f'🔑 Claim Public Key: {info.claim_pubkey}')
    print(f'💰 On-chain Amount (Sat): {info.onchain_amount_sat}')
    print(f'🚦 Status: {info.status}')

  def _print_invoice_paid(self, invoice_paid):
    print('✅ Invoice Paid')
    # TODO: Parse the bolt11 invoice and obtain the amount
    # print(f'📦 Payment Hash: {invoice_paid.details.payment_hash}')
    # print(f'⚡ Bolt 11: {invoice_paid.details.bolt11}')
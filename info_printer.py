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
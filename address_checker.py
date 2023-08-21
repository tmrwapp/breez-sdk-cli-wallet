from bitcoinutils.setup import setup
from bitcoinutils.keys import P2pkhAddress, P2shAddress, P2wshAddress, P2wpkhAddress

class AddressChecker:
  def __init__(self):
    setup('mainnet')
  
  def is_valid_address(self, address):
    # Try parsing as different address types
    try:
      P2pkhAddress(address)
      return True
    except:
        pass
    try:
      P2shAddress(address)
      return True
    except:
      pass
    try:
      P2wshAddress(address)
      return True
    except:
      pass
    try:
      P2wpkhAddress(address)
      return True
    except:
      pass
    return False
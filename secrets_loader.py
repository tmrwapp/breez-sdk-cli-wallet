
def load_secrets(filename):
  secrets = {}
  with open(filename, 'r') as file:
    for line in file:
      if 'seed:' in line:
        secrets['seed'] = bytes.fromhex(line.split(':')[1].strip())
      elif 'invite_code:' in line:
        secrets['invite_code'] = line.split(':')[1].strip()
      elif 'phrase:' in line:
        secrets['phrase'] = line.split(':')[1].strip()
      elif 'api_key' in line:
        secrets['api_key'] = line.split(':')[1].strip()
  return secrets

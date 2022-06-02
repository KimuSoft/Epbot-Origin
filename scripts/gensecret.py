import secrets

with open('.env', 'a') as f:
    f.writelines([f'IMAGE_GENERATOR_TOKEN={secrets.token_hex(24)}', '\n'])

import configparser

config = configparser.ConfigParser()
config.read('config.ini')

secret_key = config.get('DEFAULT','SECRET_KEY') # 'secret-key-of-myapp'
ci_hook_url = config.get('CI','HOOK_URL')

print(secret_key, ci_hook_url)
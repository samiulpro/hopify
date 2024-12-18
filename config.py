import os
import json

CONFIG_PATH = os.path.expanduser("~/.hopify_config.json")

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return None
    with open(CONFIG_PATH, "r") as file:
        return json.load(file)

def save_config(config):
    with open(CONFIG_PATH, "w") as file:
        json.dump(config, file, indent=4)

def setup_config():
    print("It looks like this is your first time using hopify!")
    private_key_path = input("Enter the full path to your private key (e.g., ~/.ssh/id_rsa): ").strip()
    default_remote_dir = input("Enter a default remote directory (optional): ").strip()
    config = {
        "private_key_path": private_key_path,
        "default_remote_dir": default_remote_dir or "/"
    }
    save_config(config)
    print(f"Configuration saved to {CONFIG_PATH}")
    return config

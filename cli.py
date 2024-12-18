import os

import argparse
from connection import ConnectionHandler
from file_handler import FileHandler
from file_sender import FileSender
from utils import log
from config import load_config, setup_config

## The CLI functionality
# configuration setup
config = load_config()
if not config:
    config = setup_config()

parser = argparse.ArgumentParser(
                    prog='hopify',
                    description='It transfers files over SSH',
                    epilog='Just make sure your public, private keys are properly configured both on local and the remote machines.')


parser.add_argument("username", help="Username for the remote server")
parser.add_argument("remote_ip", help="Remote machine IP")
parser.add_argument("file_path", help="Path to the file or directory to upload")
parser.add_argument("--remote_path", default=config.get("default_remote_dir", "/"), help="Remote directory to upload files to")


args = parser.parse_args()

connection = None  # Initialize the connection variable
sftp_client = None  # Initialize the SFTP client variable

try:
    # Establish SSH connection
    connection = ConnectionHandler(machine=args.remote_ip, username=args.username, key=config["private_key_path"])
    connection.connect()
    connection.check_connection()
    sftp_client = connection.get_sftp_client()

    # Handle local files
    local_path = args.file_path
    if not os.path.exists(local_path):
        raise ValueError("The provided local path does not exist.")

    file_handler = FileHandler(path=local_path)
    file_list = file_handler.get_all_files()
    if not file_list:
        log("No files to upload. Exiting.")
        raise ValueError("No files found in the specified path.")
    
    log(f"Files to upload: {file_list}")

    # Send files to the remote server
    file_sender = FileSender(sftp_client=sftp_client, file_list=file_list, remote_path=args.remote_path)
    file_sender.send_files()

except Exception as e:
    log(f"Error: {e}")

finally:
    if sftp_client:
        sftp_client.close()
    if connection and connection.ssh:
        connection.ssh.close()

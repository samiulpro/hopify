import paramiko
import os
import json
from tqdm import tqdm
import datetime
import posixpath

# Constants
SESSION_FILE = "hopify_session.json"

def log(message):
    print(f"{datetime.datetime.now().isoformat()} - {message}")

def load_session():
    """Load session credentials from a JSON file."""
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as file:
            return json.load(file)
    return {}

def save_session(credentials):
    """Save session credentials to a JSON file."""
    with open(SESSION_FILE, "w") as file:
        json.dump(credentials, file, indent=4)

class ConnectionHandler:
    def __init__(self, machine, username, password):
        self.machine = machine
        self.username = username
        self.password = password
        self.ssh = None

    def connect(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname=self.machine, username=self.username, password=self.password)
        log("SSH connection established")

    def check_connection(self):
        stdin, stdout, stderr = self.ssh.exec_command("whoami")
        if (stdout.read().decode()).strip() == f"samiul\\{self.username}":
            log("CONNECTION ESTABLISHED --- CHECKING PASSED")
        else:
            self.ssh.close()
            raise ConnectionError("Username mismatch. Connection verification failed")

    def get_sftp_client(self):
        if self.ssh is None:
            raise Exception("SSH connection is not established.")
        return self.ssh.open_sftp()

class FileHandler:
    def __init__(self, path):
        self.path = path

    def get_all_files(self, file_list=None):
        if file_list is None:
            file_list = []

        if os.path.isdir(self.path):
            for root, _, files in os.walk(self.path):
                for file in files:
                    file_list.append(os.path.join(root, file))
        elif os.path.isfile(self.path):
            file_list.append(self.path)
        else:
            raise ValueError("Provided path is neither a file nor a directory.")

        return file_list

def ensure_remote_directory(sftp, remote_path):
    directories = remote_path.strip("/").split("/")
    current_path = ""
    for directory in directories:
        current_path = posixpath.join(current_path, directory) if current_path else directory
        try:
            sftp.stat(current_path)
        except FileNotFoundError:
            log(f"Remote directory '{current_path}' does not exist. Creating it...")
            sftp.mkdir(current_path)

class FileSender:
    def __init__(self, sftp_client, file_list, remote_path):
        self.sftp = sftp_client
        self.file_list = file_list
        self.remote_path = remote_path

    def _progress_callback(self, transferred, total, pbar):
        """Callback to update the progress bar during file upload."""
        pbar.update(transferred - pbar.n)

    def send_files(self):
        if not self.remote_path.endswith("/"):
            self.remote_path += "/"
            
        for local_file in self.file_list:
            remote_file = posixpath.join(self.remote_path, os.path.basename(local_file))
            file_size = os.path.getsize(local_file)
            ensure_remote_directory(self.sftp, remote_path=self.remote_path)

            log(f"Uploading {local_file} to {remote_file}")
            with tqdm(total=file_size, unit="B", unit_scale=True, desc=f"Uploading {os.path.basename(local_file)}", ascii=True) as pbar:
                self.sftp.put(local_file, remote_file, callback=lambda transferred, total: self._progress_callback(transferred, total, pbar))

        print("All files uploaded successfully!")

# Main script
def main():
    session = load_session()

    if session:
        use_saved = input("Use saved session? (y/n): ").strip().lower() == "y"
    else:
        use_saved = False

    if use_saved:
        machine = session["machine"]
        username = session["username"]
        password = session["password"]
        remote_path = session["remote_path"]
    else:
        machine = input("Enter the remote machine IP: ").strip()
        username = input("Enter the username: ").strip()
        password = input("Enter the password: ").strip()
        remote_path = input("Enter the remote directory path: ").strip()
        session = {"machine": machine, "username": username, "password": password, "remote_path": remote_path}
        save_session(session)

    try:
        connection = ConnectionHandler(machine=machine, username=username, password=password)
        connection.connect()
        connection.check_connection()
        sftp_client = connection.get_sftp_client()

        local_path = input("Enter the path to a file or directory: ").strip()
        if not os.path.exists(local_path):
            raise ValueError("The provided local path does not exist.")

        file_handler = FileHandler(path=local_path)
        file_list = file_handler.get_all_files()

        if not file_list:
            log("No files to upload. Exiting.")
            return

        log(f"Files to upload: {file_list}")

        file_sender = FileSender(sftp_client=sftp_client, file_list=file_list, remote_path=remote_path)
        file_sender.send_files()

    except Exception as e:
        log(f"Error: {e}")
    finally:
        if "sftp_client" in locals() and sftp_client:
            sftp_client.close()
        if "connection" in locals() and connection.ssh:
            connection.ssh.close()

if __name__ == "__main__":
    main()

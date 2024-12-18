import datetime

def log(message):
    print(f"{datetime.datetime.now().isoformat()} - {message}")
    

def ensure_remote_directory(sftp, remote_path):
    try:
        sftp.stat(remote_path)
    except:
        log(f"Remote directory '{remote_path}' does not exist. Creating it...")
        sftp.mkdir(remote_path)
from utils import ensure_remote_directory, log
from tqdm import tqdm
import os

class FileSender:
    def __init__(self, sftp_client, file_list, remote_path):
        self.sftp = sftp_client
        self.file_list = file_list
        self.remote_path = remote_path

    def _progress_callback(self, transferred, total, pbar):
        """Callback to update the progress bar during file upload."""
        pbar.update(transferred - pbar.n)  # Update the progress bar

    def send_files(self):
        # To avoid unexpected path concatenation issues.
        if not self.remote_path.endswith("/"):
            self.remote_path += "/"
            
        for local_file in self.file_list:
            remote_file = os.path.join(self.remote_path, os.path.basename(local_file))
            file_size = os.path.getsize(local_file)
            print("Testing the remote path...")
            ensure_remote_directory(self.sftp, remote_path=self.remote_path)

            log(f"Uploading {local_file} to {remote_file}")

            # Create a tqdm progress bar
            with tqdm(total=file_size, unit="B", unit_scale=True, desc=f"Uploading {os.path.basename(local_file)}", ascii=True) as pbar:
                # Upload the file with a progress callback
                self.sftp.put(local_file, remote_file, callback=lambda transferred, total: self._progress_callback(transferred, total, pbar))

        print("All files uploaded successfully!")
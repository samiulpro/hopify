import paramiko
from getpass import getpass
from utils import log

class ConnectionHandler:
    def __init__(self, machine, username, key):
        self.machine = machine
        self.username = username
        self.key = key
        self.password = input("password: ")
        self.ssh = None
        
    def connect(self):
        """
        Establish an SSH connection using either a private key or a password.
        """
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            if self.key:
                log("Attempting private key authentication...")
                private_key = paramiko.RSAKey.from_private_key_file(self.key)
                self.ssh.connect(
                    hostname=self.machine,
                    username=self.username,
                    pkey=private_key
                )
                log("SSH connection established with private key.")
            elif self.password:
                log("Attempting password authentication...")
                self.ssh.connect(
                    hostname=self.machine,
                    username=self.username,
                    password=self.password
                )
                log("SSH connection established with password.")
            else:
                raise ValueError("Either a private key or password must be provided.")
        except paramiko.AuthenticationException:
            log("Authentication failed. Please check your credentials.")
            raise

    def connecta(self):
        private_key = paramiko.RSAKey.from_private_key_file(self.key)
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname=self.machine, username=self.username, pkey=private_key)
        log("SSH connection established")

    def check_connection(self):
        stdin, stdout, stderr = self.ssh.exec_command("whoami")
        if (stdout.read().decode()).strip() == self.username:
            log("CONNECTION ESTABLISHED --- CHECKING PASSED")
        else:
            self.ssh.close()
            raise ConnectionError("Username mismatch. Connection verification failed")

    def get_sftp_client(self):
        if self.ssh is None:
            raise Exception("SSH connection is not established.")
        return self.ssh.open_sftp()
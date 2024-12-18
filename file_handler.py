import os

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
import base64
import hashlib
import os
import json
from datetime import datetime


class HandleFile:
    def create_file(self, file_path):
        if not os.path.exists(file_path):
            file = open(file_path, 'w')
            if file_path.endswith('.json'):
                json.dump({}, file, indent=4)

    def read_JSON_file(self, JSON_file):
        file = open(JSON_file, 'r')
        file_data = json.load(file)
        return file_data

    def write_JSON_file(self, JSON_file, data):
        file = open(JSON_file, 'w')
        json.dump(data, file, indent=4)

    def add_JSON_data(self, JSON_file, filename, data):
        file_data = self.read_JSON_file(JSON_file)
        file_data[filename] = data
        self.write_JSON_file(JSON_file, file_data)

    def append_user_details(self, users_file, username):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        file = open(users_file, 'a')
        file.write(f"{timestamp} {username}\n")

    def get_tracked_files(self, add_file):
        file = open(add_file, 'r')
        files_data = json.load(file)
        return list(files_data.keys())

    def get_untracked_files(self, added_file):
        tracked_files_data = self.read_JSON_file(added_file)
        untracked_files = []

        for root, dirs, files in os.walk(os.getcwd()):
            dirs[:] = [d for d in dirs if d not in [
                '.krups', 'Classes', '__pycache__', '.git']]
            # print("dirs: ", dirs)
            for file in files:
                file_path = os.path.join(root, file)
                hash = self.compute_MD5_file(file_path)
                rel_path = os.path.relpath(file_path, os.getcwd())

                if not (rel_path in tracked_files_data.keys() and tracked_files_data[rel_path] == hash):
                    untracked_files.append(rel_path)

        return untracked_files

    def compute_MD5_file(self, file_path):
        BUF_SIZE = 65536
        md5 = hashlib.md5()

        file = open(file_path, 'rb')
        while True:
            data = file.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)

        return md5.hexdigest()

    def compute_MD5_str(self, string):
        return hashlib.md5(json.dumps(string).encode()).hexdigest()

    def encode_base64_file(self, file_path):
        file = open(file_path, 'rb')
        data = file.read()
        return base64.b64encode(data).decode('utf-8')

    def decode_base64_file(self, encoded_data):
        return base64.b64decode(encoded_data)

    def is_change_to_commit(self, added_file):
        file = open(added_file, 'r')
        added_files = json.load(file)

        return bool(added_files)

    def get_last_commit(self, head_file_path):
        head_content = open(head_file_path).read()
        head_lines = head_content.split('\n')

        last_line = None
        for line in reversed(head_lines):
            if line.strip():
                last_line = line.strip()
                break

        return last_line

    def remove_last_line(self, HEAD_path):
        lines = open(HEAD_path, 'r').readlines()
        if lines:
            lines = lines[:-1]
        open(HEAD_path, 'w').writelines(lines)

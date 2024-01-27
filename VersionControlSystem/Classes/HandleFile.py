import base64
import hashlib
import os
import json
from datetime import datetime


class HandleFile:
    def create_file(self, file_path):
        try:
            if not os.path.exists(file_path):
                file = open(file_path, 'w')
                if file_path.endswith('.json'):
                    json.dump({}, file, indent=4)
        except Exception as e:
            print(f"Error creating file {file_path}: {e}")

    def read_JSON_file(self, JSON_file):
        try:
            with open(JSON_file, 'r') as file:
                file_data = json.load(file)
            return file_data
        except Exception as e:
            print(f"Error reading from {JSON_file}: {e}")
            return {}

    def write_JSON_file(self, JSON_file, data):
        try:
            with open(JSON_file, 'w') as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            print(f"Error writing to {JSON_file}: {e}")

    def add_JSON_data(self, JSON_file, filename, data):
        try:
            file_data = self.read_JSON_file(JSON_file)
            file_data[filename] = data
            self.write_JSON_file(JSON_file, file_data)
        except Exception as e:
            print(f"Error adding data to {JSON_file}: {e}")

        except Exception as e:
            print(f"Error removing data from {JSON_file}: {e}")

    def append_user_details(self, users_file, username):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            file = open(users_file, 'a')
            file.write(f"{timestamp} {username}\n")
        except Exception as e:
            print(f"Error appending user details to {users_file}: {e}")

    def get_tracked_files(self, add_file):
        try:
            file = open(add_file, 'r')
            files_data = json.load(file)
            return list(files_data.keys())
        except Exception as e:
            print(f"Error getting tracked files from {add_file}: {e}")
            return []

    def get_untracked_files(self, added_file):
        try:
            tracked_files_data = self.read_JSON_file(added_file)
        except Exception as e:
            print(f"Error reading {added_file}: {e}")
            return []

        untracked_files = []

        try:
            for root, dirs, files in os.walk(os.getcwd()):
                dirs[:] = [d for d in dirs if d not in [
                    '.krups', 'Classes', '__pycache__', '.git']]
                files[:] = [f for f in files if f not in ['VCS.py']]
                # print("dirs: ", dirs)
                for file in files:
                    file_path = os.path.join(root, file)
                    hash = self.compute_MD5_file(file_path)
                    rel_path = os.path.relpath(file_path, os.getcwd())

                    if not (rel_path in tracked_files_data.keys() and tracked_files_data[rel_path] == hash):
                        untracked_files.append(rel_path)
        except Exception as e:
            print(f"Error getting untracked files: {e}")
            return []

        return untracked_files

    def compute_MD5_file(self, file_path):
        BUF_SIZE = 65536
        md5 = hashlib.md5()

        try:
            file = open(file_path, 'rb')
            while True:
                data = file.read(BUF_SIZE)
                if not data:
                    break
                md5.update(data)
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None
        finally:
            file.close()

        return md5.hexdigest()

    def compute_MD5_str(self, string):
        try:
            return hashlib.md5(json.dumps(string).encode()).hexdigest()
        except Exception as e:
            print(f"Error computing MD5 hash: {e}")
            return None

    def encode_base64_file(self, file_path):
        try:
            file = open(file_path, 'rb')
            data = file.read()
            return base64.b64encode(data).decode('utf-8')
        except Exception as e:
            print(f"Error encoding file {file_path}: {e}")
            return None

    def decode_base64_file(self, encoded_data):
        try:
            return base64.b64decode(encoded_data)
        except Exception as e:
            print(f"Error decoding base64 data: {e}")
            return None

    def is_change_to_commit(self, added_file):
        try:
            file = open(added_file, 'r')
            added_files = json.load(file)
            return bool(added_files)
        except Exception as e:
            print(f"Error reading file {added_file}: {e}")
            return None

    def get_last_commit(self, head_file_path):
        try:
            head_content = open(head_file_path).read()
            head_lines = head_content.split('\n')

            last_line = None
            for line in reversed(head_lines):
                if line.strip():
                    last_line = line.strip()
                    break

            return last_line
        except Exception as e:
            print(f"Error reading file {head_file_path}: {e}")
            return None

    def remove_last_line(self, HEAD_path):
        try:
            lines = open(HEAD_path, 'r').readlines()
            if lines:
                lines = lines[:-1]
            open(HEAD_path, 'w').writelines(lines)
        except Exception as e:
            print(f"Error removing last line from file {HEAD_path}: {e}")

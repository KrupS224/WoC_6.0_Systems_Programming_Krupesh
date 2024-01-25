import hashlib
import os
import json
from datetime import datetime


class HandleFile:
    def create_file(self, file_path):
        if not os.path.exists(file_path):
            with open(file_path, 'w') as file:
                if file_path.endswith('.json'):
                    json.dump({}, file, indent=4)

    def add_JSON_data(self, JSON_file, filename, data):
        with open(JSON_file, 'r') as file:
            file_data = json.load(file)

        file_data[filename] = data

        with open(JSON_file, 'w') as file:
            json.dump(file_data, file, indent=4)

    def append_user_details(self, users_file, username):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(users_file, 'a') as file:
            file.write(f"{timestamp} {username}\n")

    def get_tracked_files(self, index_file):
        with open(index_file, 'r') as file:
            files_data = json.load(file)
            return list(files_data.keys())

    def compute_MD5(self, file_path):
        BUF_SIZE = 65536
        md5 = hashlib.md5()

        with open(file_path, 'rb') as file:
            while True:
                data = file.read(BUF_SIZE)
                if not data:
                    break
                md5.update(data)

        return md5.hexdigest()

    def is_change_to_commit(self, added_file):
        with open(added_file, 'r') as file:
            added_files = json.load(file)

        return bool(added_files)

    def create_commit(self, username, commit_file, message):
        commit_data = {
            'author': username,
            'message': message,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        commit_hash = hashlib.md5(json.dumps(
            commit_data, sort_keys=True).encode()).hexdigest()

        filename = os.path.basename(commit_file)
        with open(commit_file, 'r') as file:
            committed_data = json.load(file)

        committed_data[filename] = commit_data

        with open(commit_file, 'w') as file:
            json.dump(committed_data, file, indent=4)

        return commit_hash

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

    def get_tracked_files(self, index_file):
        file = open(index_file, 'r')
        files_data = json.load(file)
        return list(files_data.keys())

    def compute_MD5(self, file_path):
        BUF_SIZE = 65536
        md5 = hashlib.md5()

        file = open(file_path, 'rb')
        while True:
            data = file.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)

        return md5.hexdigest()

    def is_change_to_commit(self, added_file):
        file = open(added_file, 'r')
        added_files = json.load(file)

        return bool(added_files)

    def get_latest_commit_filenames(self, commit_file):
        file = open(commit_file, 'r')
        commit_data = json.load(file)

        sorted_commit_data = sorted(
            commit_data.values(), key=lambda x: json.loads(x)['timestamp'], reverse=True)

        latest_commit_filenames = [entry['filename']
                                   for entry in sorted_commit_data]

        return latest_commit_filenames

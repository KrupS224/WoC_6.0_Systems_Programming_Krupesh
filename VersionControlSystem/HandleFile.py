import base64
import hashlib
import os
import json
from datetime import datetime
import shutil


class HandleFile:
    def create_file(self, file_path):
        try:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as file:
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

    def remove_JSON_data(self, JSON_file, file_path_relative):
        try:
            file_data = self.read_JSON_file(JSON_file)
            if file_path_relative in file_data.keys():
                file_data.pop(file_path_relative)
                self.write_JSON_file(JSON_file, file_data)
        except Exception as e:
            print(f"Error removing data from {JSON_file}: {e}")

    def append_user_details(self, users_file, username):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            with open(users_file, 'a') as file:
                file.write(f"{timestamp} {username}\n")
        except Exception as e:
            print(f"Error appending user details to {users_file}: {e}")

    def get_added_files(self, add_file):
        try:
            with open(add_file, 'r') as file:
                files_data = json.load(file)
                return list(files_data.keys())
        except Exception as e:
            print(f"Error getting tracked files from {add_file}: {e}")
            return []

    def get_untracked_files(self, tracked_files_data):
        untracked_files = []

        try:
            for root, dirs, files in os.walk(os.getcwd()):
                dirs[:] = [d for d in dirs if d not in [
                    '.krups', '__pycache__', '.git']]
                files[:] = [f for f in files if f not in [
                    'VCS.py', 'HandleFile.py', '.gitignore']]
                # print("dirs: ", dirs)
                for file in files:
                    file_path = os.path.join(root, file)
                    hash = self.compute_MD5_file(file_path)
                    rel_path = os.path.relpath(file_path, os.getcwd())

                    if not (rel_path in tracked_files_data and tracked_files_data[rel_path] == hash):
                        untracked_files.append(rel_path)
        except Exception as e:
            print(f"Error getting untracked files: {e}")
            return []

        return untracked_files

    def compute_MD5_file(self, file_path):
        BUF_SIZE = 65536
        md5 = hashlib.md5()

        try:
            with open(file_path, 'rb') as file:
                while True:
                    data = file.read(BUF_SIZE)
                    if not data:
                        break
                    md5.update(data)
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None

        return md5.hexdigest()

    def compute_MD5_str(self, string):
        try:
            return hashlib.md5(json.dumps(string).encode()).hexdigest()
        except Exception as e:
            print(f"Error computing MD5 hash: {e}")
            return None

    def encode_base64_file(self, file_path):
        try:
            with open(file_path, 'rb') as file:
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
            with open(added_file, 'r') as file:
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

    def read_all_lines(self, file_path):
        try:
            with open(file_path) as file:
                content = file.read()
                lines = [line.strip()
                         for line in content.split('\n') if line.strip()]
                return lines
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return []

    def get_second_last_commit(self, head_file_path):
        try:
            with open(head_file_path) as file:
                head_content = file.read()
                head_lines = head_content.split('\n')

                commit_lines = [line.strip()
                                for line in reversed(head_lines) if line.strip()]

                if len(commit_lines) >= 2:
                    return commit_lines[1]
                else:
                    return None
        except Exception as e:
            print(f"Error reading file {head_file_path}: {e}")
            return None

    def remove_last_line(self, HEAD_path):
        try:
            with open(HEAD_path, 'r') as file:
                lines = file.readlines()
                if lines:
                    lines = lines[:-1]
            with open(HEAD_path, 'w') as file:
                file.writelines(lines)
        except Exception as e:
            print(f"Error removing last line from file {HEAD_path}: {e}")

    def get_committed_files(self, commits_dir, last_commit, key):
        try:
            commit_file_path = os.path.join(commits_dir, last_commit)
            with open(commit_file_path, 'rb') as commit_file:
                commit_file_encoded_data = commit_file.read()
                commit_file_decoded_data = base64.b64decode(
                    commit_file_encoded_data).decode('utf-8')
                commit_file_decoded_data = json.loads(commit_file_decoded_data)
                committed_files = commit_file_decoded_data[key]

                return committed_files
        except Exception as e:
            print(f"Error reading committed files from {
                  commit_file_path}: {e}")
            return []

    def get_tracked_files(self, branches_dir, branch, commits_dir):
        HEAD_path = os.path.join(branches_dir, branch, 'HEAD')
        last_commit = self.get_last_commit(HEAD_path)

        if not last_commit:
            return {}, {}

        committed_files = self.get_committed_files(
            commits_dir, last_commit, 'index')
        # print(committed_files)

        tracked_files_data = {}
        try:
            for root, dirs, files in os.walk(os.getcwd()):
                dirs[:] = [d for d in dirs if d not in [
                    '.krups', '__pycache__', '.git']]
                files[:] = [f for f in files if f not in [
                    'VCS.py', 'HandleFile.py', '.gitignore']]
                # print("dirs: ", dirs)
                for file in files:
                    file_path = os.path.join(root, file)
                    hash = self.compute_MD5_file(file_path)
                    rel_path = os.path.relpath(file_path, os.getcwd())

                    if rel_path in committed_files.keys() and committed_files[rel_path] == hash:
                        tracked_files_data[rel_path] = hash
        except Exception as e:
            print(f"Error getting tracked files: {e}")
            return {}, {}

        all_committed_files = self.get_committed_files(
            commits_dir, last_commit, 'index')

        return tracked_files_data, all_committed_files

    def clear_current_dir(self, dir_path):
        try:
            for root, dirs, files in os.walk(dir_path):
                dirs[:] = [d for d in dirs if d not in [
                    '.krups', '__pycache__', '.git']]
                files[:] = [f for f in files if f not in [
                    'VCS.py', 'HandleFile.py', '.gitignore']]

                for file in files:
                    file_path_full = os.path.normpath(
                        os.path.join(root, file))
                    os.remove(file_path_full)

            for root, dirs, files in os.walk(dir_path):
                dirs[:] = [d for d in dirs if d not in [
                    '.krups', '__pycache__', '.git']]
                files[:] = [f for f in files if f not in [
                    'VCS.py', 'HandleFile.py', '.gitignore']]

                for dir in dirs:
                    dir_path_full = os.path.normpath(
                        os.path.join(root, dir))
                    shutil.rmtree(dir_path_full)
        except Exception as e:
            print(f"Error removing file(s) or directory: {e}")
            return

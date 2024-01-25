import hashlib
import os
import sys
import shutil
import json
from datetime import datetime
from HandleFileClass import HandleFile


class VersionControlSystem:
    def __init__(self, vcs_name=".tico"):
        self.vcs_name = vcs_name
        self.username = None
        self.branches_dir = os.path.join(vcs_name, "branches")
        self.objects_dir = os.path.join(vcs_name, "objects")
        self.main_dir = os.path.join(self.branches_dir, "main")
        self.added_file = os.path.join(vcs_name, "added.json")
        self.index_file = os.path.join(vcs_name, "index.json")
        self.users_file = os.path.join(vcs_name, "users.txt")
        self.commit_file = os.path.join(self.objects_dir, "commit.json")

        # initialize the file handler
        self.file_handler = HandleFile()

    def init(self):
        username = input("Enter your username: ")
        self.username = username

        # Create all directories
        os.makedirs(self.vcs_name, exist_ok=True)
        os.makedirs(self.branches_dir, exist_ok=True)
        os.makedirs(self.objects_dir, exist_ok=True)
        os.makedirs(self.main_dir, exist_ok=True)

        # Create files
        self.file_handler.create_file(self.added_file)
        self.file_handler.create_file(self.index_file)
        self.file_handler.create_file(self.users_file)
        self.file_handler.create_file(self.commit_file)

        # Append user details
        self.file_handler.append_user_details(self.users_file, username)

        print("New Empty .tico repository created.")

    def status(self):
        all_files = [f for f in os.listdir('.')if os.path.isfile(f)]
        tracked_files_data = self.file_handler.read_JSON_file(self.added_file)

        untracked_files = {}
        for file in all_files:
            hash = self.file_handler.compute_MD5(
                os.path.join(os.getcwd(), file))
            if file in tracked_files_data.keys() and tracked_files_data[file] == hash:
                untracked_files[file] = 'Tracked'
            else:
                untracked_files[file] = 'Untracked'

        for file in untracked_files:
            print(f"{untracked_files[file]}: {file}")

    def add(self, filename):
        file_path = os.path.join(os.getcwd(), filename)
        # file_path = os.path.abspath(filename)

        if not os.path.exists(file_path):
            print(f"Error: file {filename} does not exists.")
            return

        file_hash_MD5 = self.file_handler.compute_MD5(file_path)
        self.file_handler.add_JSON_data(
            self.added_file, filename, file_hash_MD5)
        self.file_handler.add_JSON_data(
            self.index_file, filename, file_hash_MD5)

    def commit(self):
        if len(sys.argv) < 4 or sys.argv[2] != '-m':
            print("Usage: python VCS.py commit -m <message>")
            return

        if not self.file_handler.is_change_to_commit(self.added_file):
            print("No changes to commit.")
            return

        message = sys.argv[3]
        added_files = self.file_handler.get_tracked_files(self.added_file)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        JSON_data = self.file_handler.read_JSON_file(self.commit_file)

        for filename in added_files:
            commit_data = {
                'filename': filename,
                'message': message,
                'author': self.username,
                'timestamp': timestamp
            }

            file_hash = hashlib.md5(json.dumps(
                commit_data, sort_keys=True).encode()).hexdigest()
            JSON_data[filename] = file_hash

        self.file_handler.write_JSON_file(self.commit_file, JSON_data)
        self.file_handler.write_JSON_file(self.added_file, {})

    def rmcommit(self):
        latest_commit_filenames = self.file_handler.get_latest_commit_filenames(
            self.commit_file)

        if not latest_commit_filenames:
            print("No commits to remove")
            return

        for filename in latest_commit_filenames:
            self.add(filename)

    def help(self):
        print("Tico - A Version Control System.")
        print("tico init - Initialize a new Tico repository")
        print("tico add <file> - Add a file to the index")
        print("tico commit -m <message> - Commit changes with a message")
        print("tico rmadd <file> - remove a file from the index")
        print("tico rmcommit - remove last commit")
        print("tico log - Display commit log")
        print("tico checkout <commit> - Checkout a specific commit")
        print("tico help - to see this usage help")
        print("tico status - to see status")
        print("tico user show - to see present user")
        print("tico user set <username> - to change user")
        print("tico push <path> - to push your file to another folder")
        print("Created by - Krupesh Parmar")


vcs = VersionControlSystem()

if len(sys.argv) < 2:
    vcs.help()
    sys.exit(1)

command = sys.argv[1]

commands = {
    "init": vcs.init,
    "status": vcs.status,
    "add": lambda: vcs.add(sys.argv[2]) if len(sys.argv) > 2 else print("File argument missing"),
    "help": vcs.help,
    "rmcommit": vcs.rmcommit,
    "commit": vcs.commit,
}

commands.get(command, lambda: print("Not a valid command"))()

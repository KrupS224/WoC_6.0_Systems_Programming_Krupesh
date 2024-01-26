import hashlib
import os
import sys
import shutil
import json
from datetime import datetime
from Classes.HandleFile import HandleFile
from Classes.Stack import Stack


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
        self.stack = Stack()

    def notInitialized(self, dir_path):
        files_and_dirs = os.listdir(dir_path)
        if '.krups' not in files_and_dirs:
            return True
        return False

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
        if self.notInitialized('.'):
            print("'.krups' folder is not initialized...")
            print("Run: 'tico init' command to initialize tico repository")
            return

        tracked_files_data = self.file_handler.read_JSON_file(self.added_file)

        def is_subdirectory(parent, child):
            relative_path = os.path.relpath(child, parent)
            return not relative_path.startswith('..') and not os.path.isabs(relative_path)

        for root, dirs, files in os.walk(os.getcwd()):
            dirs[:] = [d for d in dirs if d not in [
                '.krups', 'Classes', '__pycache__', '.git']]
            # print("dirs: ", dirs)
            for file in files:
                file_path = os.path.join(root, file)
                hash = self.file_handler.compute_MD5(file_path)
                rel_path = os.path.relpath(file_path, os.getcwd())

                if rel_path in tracked_files_data.keys() and tracked_files_data[rel_path] == hash:
                    status = 'Tracked'
                else:
                    status = 'Untracked'

                print(f"{status}: {rel_path}")

    def add(self, file_path_full, file_path_relative=None):
        if not os.path.exists(file_path_full):
            print(f"Error: File '{file_path_relative}' does not exist.")
            return

        file_hash_MD5 = self.file_handler.compute_MD5(file_path_full)
        file_path_relative = file_path_relative if file_path_relative else os.path.normpath(
            file_path_full)
        self.file_handler.add_JSON_data(
            self.added_file, file_path_relative, file_hash_MD5)
        self.file_handler.add_JSON_data(
            self.index_file, file_path_relative, file_hash_MD5)

    def add_with_subdirs(self, dir_path):
        if self.notInitialized('.'):
            print("'.krups' folder is not initialized...")
            print("Run: 'tico init' command to initialize tico repository")
            return

        if not os.path.isdir(dir_path):
            self.add(dir_path)
            return

        for root, dirs, files in os.walk(dir_path):
            dirs[:] = [d for d in dirs if d not in [
                '.krups', 'Classes', '__pycache__', '.git']]

            for file in files:
                file_path_full = os.path.normpath(os.path.join(root, file))
                file_path_relative = os.path.normpath(
                    file_path_full)
                self.add(file_path_full, file_path_relative)

    def commit(self):
        if len(sys.argv) < 4 or sys.argv[2] != '-m':
            print("Usage: python VCS.py commit -m <message>")
            return

        if self.notInitialized('.'):
            print("'.krups' folder is not initialized...")
            print("Run: 'tico init' command to initialize tico repository")
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
        if self.notInitialized('.'):
            print("'.krups' folder is not initialized...")
            print("Run: 'tico init' command to initialize tico repository")
            return

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


vcs = VersionControlSystem('.krups')

if len(sys.argv) < 2:
    vcs.help()
    sys.exit(1)

command = sys.argv[1]

commands = {
    "init": vcs.init,
    "status": vcs.status,
    "add": lambda: vcs.add_with_subdirs(sys.argv[2]) if len(sys.argv) > 2 else print("File argument missing"),
    "help": vcs.help,
    "rmcommit": vcs.rmcommit,
    "commit": vcs.commit,
}

commands.get(command, lambda: print("Not a valid command"))()

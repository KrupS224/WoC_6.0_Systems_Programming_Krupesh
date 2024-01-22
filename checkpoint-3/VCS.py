import hashlib
import os
import sys
import shutil
import json
from datetime import datetime


class VersionControlSystem:
    def __init__(self, vcs_name=".tico"):
        self.vcs_name = vcs_name
        self.branches_dir = os.path.join(vcs_name, "branches")
        self.objects_dir = os.path.join(vcs_name, "objects")
        self.main_dir = os.path.join(self.branches_dir, "main")
        self.added_file = os.path.join(self.main_dir, "added.json")
        self.index_file = os.path.join(self.main_dir, "index.json")
        self.users_file = os.path.join(self.main_dir, "users.txt")

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

    def append_user_details(self, username):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.users_file, 'a') as file:
            file.write(f"{timestamp} {username}\n")

    def get_tracked_files(self):
        with open(self.index_file, 'r') as file:
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

    def init(self):
        username = input("Enter your username: ")

        # Create all directories
        os.makedirs(self.vcs_name, exist_ok=True)
        os.makedirs(self.branches_dir, exist_ok=True)
        os.makedirs(self.objects_dir, exist_ok=True)
        os.makedirs(self.main_dir, exist_ok=True)

        # Create files
        self.create_file(self.added_file)
        self.create_file(self.index_file)
        self.create_file(self.users_file)

        # Append user details
        self.append_user_details(username)

        print("Initialization successful.")

    def status(self):
        all_files = [f for f in os.listdir('.')if os.path.isfile(f)]
        tracked_files = self.get_tracked_files()
        untracked_files = set(all_files) - set(tracked_files)

        if untracked_files:
            print("Untracked files: ", end='')
            for file in untracked_files:
                print(f"{file} ", end='')
        else:
            print("No untracked files.")

    def add(self, filename):
        file_path = os.path.join(os.getcwd(), filename)

        if not os.path.exists(file_path):
            print(f"Error: file {filename} does not exists.")
            return

        file_hash_MD5 = self.compute_MD5(file_path)
        self.add_JSON_data(self.added_file, filename, file_hash_MD5)
        self.add_JSON_data(self.index_file, filename, file_hash_MD5)

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

if command == "init":
    vcs.init()
elif command == "status":
    vcs.status()
elif command == "add":
    file = sys.argv[2]
    vcs.add(file)
else:
    print("Not valid command")

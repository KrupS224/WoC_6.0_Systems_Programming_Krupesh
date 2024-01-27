import base64
import hashlib
import json
import os
import sys
from datetime import datetime
from Classes.HandleFile import HandleFile
from Classes.Stack import Stack


class VersionControlSystem:
    def __init__(self, vcs_name=".tico"):
        self.vcs_name = vcs_name
        self.branch = "main"
        self.username = None
        self.branches_dir = os.path.join(vcs_name, "branches")
        self.objects_dir = os.path.join(vcs_name, "objects")
        self.main_branch = os.path.join(self.branches_dir, "main")
        self.added_file = os.path.join(vcs_name, "added.json")
        self.index_file = os.path.join(vcs_name, "index.json")
        self.users_file = os.path.join(vcs_name, "users.txt")
        self.commits_dir = os.path.join(self.objects_dir, "commits")
        self.content_dir = os.path.join(self.objects_dir, "content")

        # initialize helper classes
        self.file_handler = HandleFile()
        self.stack = Stack()

    def create_branch(self, branch_name):
        try:
            branch_path = os.path.join(self.branches_dir, branch_name)
            if not os.path.exists(branch_path):
                os.makedirs(branch_path)
                print(f"Branch {branch_name} created successfully.")

            self.file_handler.create_file(os.path.join(branch_path, "HEAD"))
        except Exception as e:
            print(f"Error creating branch: {e}")

    def notInitialized(self, dir_path):
        files_and_dirs = os.listdir(dir_path)
        if '.krups' not in files_and_dirs:
            return True
        return False

    def init(self):
        username = input("Enter your username: ")
        self.username = username

        # Create all directories
        try:
            os.makedirs(self.vcs_name, exist_ok=True)
            os.makedirs(self.branches_dir, exist_ok=True)
            os.makedirs(self.objects_dir, exist_ok=True)
            os.makedirs(self.content_dir, exist_ok=True)
            os.makedirs(self.commits_dir, exist_ok=True)
        except Exception as e:
            print(f"Error creating directories: {e}")
            return

        self.create_branch("main")

        # Create files
        try:
            self.file_handler.create_file(self.added_file)
            self.file_handler.create_file(self.index_file)
            self.file_handler.create_file(self.users_file)
        except Exception as e:
            print(f"Error creating files: {e}")
            return

        # Append user details
        self.file_handler.append_user_details(self.users_file, username)

        print("New Empty .krups repository created.")

    def status(self):
        try:
            if self.notInitialized('.'):
                print("'.krups' folder is not initialized...")
                print("Run: 'tico init' command to initialize tico repository")
                return

            tracked_files_data = self.file_handler.read_JSON_file(
                self.added_file)

            if not tracked_files_data:
                HEAD_path = os.path.join(
                    self.branches_dir, self.branch, 'HEAD')
                last_commit = self.file_handler.get_last_commit(HEAD_path)

                if last_commit:
                    commit_file = self.file_handler.read_JSON_file(
                        os.path.join(self.commits_dir, f"{last_commit}.json"))
                    committed_files = commit_file['change']
                    all_commited = True

                    for root, dirs, files in os.walk(os.getcwd()):
                        dirs[:] = [d for d in dirs if d not in [
                            '.krups', 'Classes', '__pycache__', '.git']]
                        files[:] = [f for f in files if f not in ['VCS.py']]
                        # print("dirs: ", dirs)
                        for file in files:
                            file_path = os.path.join(root, file)
                            hash = self.file_handler.compute_MD5_file(
                                file_path)
                            rel_path = os.path.relpath(file_path, os.getcwd())

                            if not (rel_path in committed_files.keys() and committed_files[rel_path] == hash):
                                all_commited = False
                                tracked_files_data = committed_files

                    if all_commited:
                        print("All files committed...")
                        return

            for root, dirs, files in os.walk(os.getcwd()):
                dirs[:] = [d for d in dirs if d not in [
                    '.krups', 'Classes', '__pycache__', '.git']]
                files[:] = [f for f in files if f not in ['VCS.py']]

                # print("dirs: ", dirs)
                for file in files:
                    file_path = os.path.join(root, file)
                    hash = self.file_handler.compute_MD5_file(file_path)
                    rel_path = os.path.relpath(file_path, os.getcwd())

                    if rel_path in tracked_files_data.keys() and tracked_files_data[rel_path] == hash:
                        status = 'Tracked'
                    else:
                        status = 'Untracked'

                    print(f"{status}: {rel_path}")
        except Exception as e:
            print(f"Error in status: {e}")

    def add(self, file_path_full, file_path_relative=None):
        try:
            if not os.path.exists(file_path_full):
                print(f"Error: File '{file_path_relative}' does not exist.")
                return

            file_path_hash = self.file_handler.compute_MD5_file(file_path_full)
            file_path_relative = file_path_relative if file_path_relative else os.path.normpath(
                file_path_full)
            self.file_handler.add_JSON_data(
                self.added_file, file_path_relative, file_path_hash)
            self.file_handler.add_JSON_data(
                self.index_file, file_path_relative, file_path_hash)
        except Exception as e:
            print(f"Error adding file {file_path_relative}: {str(e)}")

    def add_with_subdirs(self, dir_path):
        if self.notInitialized('.'):
            print("'.krups' folder is not initialized...")
            print("Run: 'tico init' command to initialize tico repository")
            return

        if not os.path.isdir(dir_path):
            self.add(dir_path)
            return

        try:
            for root, dirs, files in os.walk(dir_path):
                dirs[:] = [d for d in dirs if d not in [
                    '.krups', 'Classes', '__pycache__', '.git']]
                files[:] = [f for f in files if f not in ['VCS.py']]

                for file in files:
                    file_path_full = os.path.normpath(os.path.join(root, file))
                    file_path_relative = os.path.normpath(
                        file_path_full)
                    self.add(file_path_full, file_path_relative)
        except Exception as e:
            print(f"Error adding directory {dir_path}: {e}")

    def commit(self, message="New commit"):
        if self.notInitialized('.'):
            print("'.krups' folder is not initialized...")
            print("Run: 'tico init' command to initialize tico repository")
            return

        # if not self.file_handler.is_change_to_commit(self.added_file):
        #     print("No changes to commit.")
        #     return

        tracked_files = self.file_handler.get_tracked_files(self.added_file)

        untracked_files = self.file_handler.get_untracked_files(
            self.added_file)

        if untracked_files:
            print("\nUntracked files present.")
            for file in untracked_files:
                print("Untracked: ", file)
            print()
            ans = input("Do you want to commit untracked files? (y/n): ")
            if ans.lower() == 'y':
                for file in untracked_files:
                    self.add_with_subdirs(file)
        elif not tracked_files:
            print("No changes to commit")
            return

        tracked_files = self.file_handler.get_tracked_files(self.added_file)

        try:
            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            changes = {}
            for file_path in tracked_files:
                file_path_full = os.path.normpath(
                    os.path.join(os.getcwd(), file_path))
                changes[file_path] = self.file_handler.compute_MD5_file(
                    file_path_full)

            commit_data = {
                "message": message,
                "timestamp": timestamp,
                "change": changes,
                "branch": self.branch
            }

            commit_message_hash = self.file_handler.compute_MD5_str(message)
            head_file = open(os.path.join(
                self.branches_dir, self.branch, 'HEAD'), 'a')
            head_file.write(commit_message_hash + '\n')

            try:
                commit_data_encoded = base64.b64encode(
                    json.dumps(commit_data).encode('utf-8'))
            except Exception as e:
                print(f"Error encoding commit data: {e}")
                return

            commit_file_path = os.path.join(
                self.commits_dir, commit_message_hash)
            open(commit_file_path, 'wb').write(commit_data_encoded)

            for file_path, file_hash in changes.items():
                file_data_encrypted = self.file_handler.encode_base64_file(os.path.normpath(
                    os.path.join(os.getcwd(), file_path)))
                open(os.path.join(self.content_dir,
                                  file_hash), 'w').write(file_data_encrypted)

            self.file_handler.write_JSON_file(self.added_file, {})
        except Exception as e:
            print(f"Error in commit: {e}")

    def rmcommit(self):
        if self.notInitialized('.'):
            print("'.krups' folder is not initialized...")
            print("Run: 'tico init' command to initialize tico repository")
            return

        HEAD_path = os.path.join(self.branches_dir, self.branch, 'HEAD')
        last_commit = self.file_handler.get_last_commit(HEAD_path)

        if not last_commit:
            print("No commits done...")
            return

        commit_file_path = os.path.join(self.commits_dir, last_commit)
        commit_file_encoded_data = open(commit_file_path, 'rb').read()
        commit_file_decoded_data = base64.b64decode(
            commit_file_encoded_data).decode('utf-8')
        commit_file_decoded_data = json.loads(commit_file_decoded_data)
        committed_files = commit_file_decoded_data['change']

        try:
            for file_path, file_hash in committed_files.items():
                file_path_encoded_data = os.path.join(
                    self.content_dir, file_hash)
                file_path_decoded_data = os.path.normpath(
                    os.path.join(os.getcwd(), file_path))

                file_data_encoded = open(file_path_encoded_data, 'r').read()
                file_data_decoded = self.file_handler.decode_base64_file(
                    file_data_encoded)
                open(file_path_decoded_data, 'wb').write(file_data_decoded)

                os.remove(file_path_encoded_data)

            commit_file_path = os.path.join(
                self.commits_dir, last_commit)
            os.remove(commit_file_path)
            self.file_handler.remove_last_line(HEAD_path)
        except Exception as e:
            print(f"Error in rmcommit: {e}")

    def rmadd(self, file_path_full, file_path_relative=None):
        try:
            if not os.path.exists(file_path_full):
                print(f"Error: File '{file_path_relative}' does not exist.")
                return

            file_path_relative = file_path_relative if file_path_relative else os.path.normpath(
                file_path_full)
            self.file_handler.remove_JSON_data(
                self.added_file, file_path_relative)
            self.file_handler.remove_JSON_data(
                self.index_file, file_path_relative)
        except Exception as e:
            print(f"Error removing {file_path_relative}: {str(e)}")

    def rmadd_with_subdirs(self, dir_path):
        if self.notInitialized('.'):
            print("'.krups' folder is not initialized...")
            print("Run: 'tico init' command to initialize tico repository")
            return

        if not os.path.isdir(dir_path):
            self.rmadd(dir_path)
            return

        try:
            for root, dirs, files in os.walk(dir_path):
                dirs[:] = [d for d in dirs if d not in [
                    '.krups', 'Classes', '__pycache__', '.git']]
                files[:] = [f for f in files if f not in ['VCS.py']]

                for file in files:
                    file_path_full = os.path.normpath(os.path.join(root, file))
                    file_path_relative = os.path.normpath(
                        file_path_full)
                    self.rmadd(file_path_full, file_path_relative)
        except Exception as e:
            print(f"Error adding directory {dir_path}: {e}")

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

if command == "init":
    if os.path.exists('.krups'):
        print(f"'.krups' alerady initialized...")
        sys.exit()

    vcs.init()
    sys.exit()

elif command == "status":
    if len(sys.argv) < 2 or len(sys.argv) > 2:
        print("Usage: krups status")
        sys.exit()

    vcs.status()


elif command == "add":
    if len(sys.argv) < 3:
        print("Usage: krups add <files>")
        sys.exit()

    for arg in sys.argv[2:]:
        vcs.add_with_subdirs(arg)
    sys.exit()

elif command == "rmadd":
    if len(sys.argv) < 3:
        print("Usage: krups rmadd <files>")
        sys.exit()

    for arg in sys.argv[2:]:
        vcs.rmadd_with_subdirs(arg)
    sys.exit()

elif command == "commit":
    if len(sys.argv) == 3 and sys.argv[2] == '-m':
        vcs.commit()
    elif len(sys.argv) == 4 and sys.argv[2] == '-m':
        vcs.commit(sys.argv[3])
    else:
        print("Usage: krups commit -m <message>")

    sys.exit()

elif command == "rmcommit":
    if len(sys.argv) < 2 or len(sys.argv) > 2:
        vcs.help()
        sys.exit()

    vcs.rmcommit()

elif command == 'help':
    if len(sys.argv) < 2 or len(sys.argv) > 2:
        print("Usage: krups help")
        sys.exit()

    vcs.help()
    sys.exit()

else:
    print(f"krups: '{command}' is not a krups command. See 'krups help'")
    sys.exit()

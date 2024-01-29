import base64
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime
from HandleFile import HandleFile


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

            added = self.file_handler.read_JSON_file(
                self.index_file)
            # print(added)

            tracked_files_data = None
            all_committed_files = None
            tracked_files_data, all_committed_files = self.file_handler.get_tracked_files(
                self.branches_dir, self.branch, self.commits_dir)

            if tracked_files_data and all_committed_files and tracked_files_data == all_committed_files:
                print("Your directory is up to date...")
                return

            tracked_files_data = tracked_files_data if tracked_files_data else added
            # print(tracked_files_data)

            for root, dirs, files in os.walk(os.getcwd()):
                dirs[:] = [d for d in dirs if d not in [
                    '.krups', '__pycache__', '.git']]
                files[:] = [f for f in files if f not in [
                    'VCS.py', 'HandleFile.py', '.gitignore']]

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
                    '.krups', '__pycache__', '.git']]
                files[:] = [f for f in files if f not in [
                    'VCS.py', 'HandleFile.py', '.gitignore']]

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

        added = self.file_handler.read_JSON_file(self.added_file)
        # print(added)
        tracked_files, all_committed_files = self.file_handler.get_tracked_files(
            self.branches_dir, self.branch, self.commits_dir)
        # print(tracked_files)

        untracked_files = self.file_handler.get_untracked_files(tracked_files)

        if untracked_files:
            print("\nUntracked file(s) present.")
            for file in untracked_files:
                print("Untracked: ", file)
            print()
            ans = input("Do you want to commit untracked file(s)? (y/n): ")
            if ans.lower() == 'y':
                for file in untracked_files:
                    self.add_with_subdirs(file)
        elif not tracked_files:
            print("No changes to commit")
            return

        added = self.file_handler.read_JSON_file(self.added_file)

        changes = {}
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")[:-3]

        last_commit = self.file_handler.get_last_commit(os.path.join(
            self.branches_dir, self.branch, 'HEAD'))

        committed_files = None

        if last_commit:
            commit_file_path = os.path.join(self.commits_dir, last_commit)
            commit_file_encoded_data = open(commit_file_path, 'rb').read()
            commit_file_decoded_data = base64.b64decode(
                commit_file_encoded_data).decode('utf-8')
            commit_file_decoded_data = json.loads(commit_file_decoded_data)
            committed_files = commit_file_decoded_data['index']

        for file_path in added:
            if (not committed_files) or (file_path not in committed_files.keys() or committed_files[file_path] != added[file_path]):
                file_path_full = os.path.normpath(
                    os.path.join(os.getcwd(), file_path))
                changes[file_path] = self.file_handler.compute_MD5_file(
                    file_path_full)

        index = self.file_handler.read_JSON_file(self.index_file)

        commit_data = {
            "message": message,
            "timestamp": timestamp,
            "added": changes,
            "index": index,
            "branch": self.branch
        }

        commit_data_hash = self.file_handler.compute_MD5_str(
            commit_data)
        head_file = open(os.path.join(
            self.branches_dir, self.branch, 'HEAD'), 'a')
        head_file.write(commit_data_hash + '\n')

        try:
            commit_data_encoded = base64.b64encode(
                json.dumps(commit_data).encode('utf-8'))
        except Exception as e:
            print(f"Error encoding commit data: {e}")
            return

        commit_file_path = os.path.join(
            self.commits_dir, commit_data_hash)
        open(commit_file_path, 'wb').write(commit_data_encoded)

        for file_path, file_hash in changes.items():
            file_data_encrypted = self.file_handler.encode_base64_file(os.path.normpath(
                os.path.join(os.getcwd(), file_path)))
            open(os.path.join(self.content_dir,
                              file_hash), 'w').write(file_data_encrypted)
            # print(file_path, file_hash)

        self.file_handler.write_JSON_file(self.added_file, {})

    def rmcommit(self):
        if self.notInitialized('.'):
            print("'.krups' folder is not initialized...")
            print("Run: 'tico init' command to initialize tico repository")
            return

        HEAD_path = os.path.join(self.branches_dir, self.branch, 'HEAD')
        last_commit = self.file_handler.get_last_commit(HEAD_path)
        second_last_commit = self.file_handler.get_second_last_commit(
            HEAD_path)

        if not last_commit:
            print("No commits done...")
            return

        if last_commit and not second_last_commit:
            try:
                for root, dirs, files in os.walk(os.getcwd()):
                    dirs[:] = [d for d in dirs if d not in [
                        '.krups', '__pycache__', '.git']]
                    files[:] = [f for f in files if f not in [
                        'VCS.py', 'HandleFile.py', '.gitignore']]

                    for file in files:
                        file_path_full = os.path.normpath(
                            os.path.join(root, file))
                        os.remove(file_path_full)

                for root, dirs, files in os.walk(os.getcwd()):
                    dirs[:] = [d for d in dirs if d not in [
                        '.krups', '__pycache__', '.git']]
                    files[:] = [f for f in files if f not in [
                        'VCS.py', 'HandleFile.py', '.gitignore']]

                    for dir in dirs:
                        dir_path_full = os.path.normpath(
                            os.path.join(root, dir))
                        shutil.rmtree(dir_path_full)

                commit_file_path = os.path.join(
                    self.commits_dir, last_commit)
                os.remove(commit_file_path)
                self.file_handler.remove_last_line(HEAD_path)

                self.file_handler.write_JSON_file(self.added_file, {})
                self.file_handler.write_JSON_file(self.index_file, {})
            except Exception as e:
                print(f"Error removing file: {e}")

            return

        try:
            committed_files = self.file_handler.get_committed_files(
                self.commits_dir, second_last_commit, 'added')
            # print(committed_files)

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

            # accessing 2nd last line
            last_commit = self.file_handler.get_last_commit(HEAD_path)
            # print(last_commit)
            added = {} if not last_commit else self.file_handler.get_committed_files(
                self.commits_dir, last_commit, 'added')
            index = {} if not last_commit else self.file_handler.get_committed_files(
                self.commits_dir, last_commit, 'index')
            # print(added, index)

            self.file_handler.write_JSON_file(self.added_file, added)
            self.file_handler.write_JSON_file(self.index_file, index)

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
                    '.krups', '__pycache__', '.git']]
                files[:] = [f for f in files if f not in [
                    'VCS.py', 'HandleFile.py', '.gitignore']]

                for file in files:
                    file_path_full = os.path.normpath(os.path.join(root, file))
                    file_path_relative = os.path.normpath(
                        file_path_full)
                    self.rmadd(file_path_full, file_path_relative)
        except Exception as e:
            print(f"Error adding directory {dir_path}: {e}")

    def checkout(self, message):
        pass

    def push(self, push_dir_full_path):
        if self.notInitialized('.'):
            print("'.krups' folder is not initialized...")
            print("Run: 'tico init' command to initialize tico repository")
            return

        if os.path.isfile(push_dir_full_path):
            print("Error: Path is not a directory")
            return

        if not os.path.exists(push_dir_full_path):
            os.makedirs(push_dir_full_path)

        HEAD_path = os.path.join(self.branches_dir, self.branch, 'HEAD')
        last_commit = self.file_handler.get_last_commit(HEAD_path)

        if not last_commit:
            print("No commits done...")
            return

        try:
            commit_file_path = os.path.join(self.commits_dir, last_commit)
            commit_file_encoded_data = open(commit_file_path, 'rb').read()
            commit_file_decoded_data = base64.b64decode(
                commit_file_encoded_data).decode('utf-8')
            commit_file_decoded_data = json.loads(commit_file_decoded_data)
            committed_files = commit_file_decoded_data['added']
        except Exception as e:
            print(f"Error in opening files: {e}")
            return

        try:
            for relative_path, file_hash in committed_files.items():
                file_path = os.path.join(push_dir_full_path, relative_path)

                dir_name = os.path.dirname(file_path)
                if not os.path.exists(dir_name):
                    os.makedirs(dir_name)

                self.file_handler.create_file(file_path)

                file_path_encoded_data = os.path.join(
                    self.content_dir, file_hash)

                file_data_encoded = open(file_path_encoded_data, 'r').read()
                file_data_decoded = self.file_handler.decode_base64_file(
                    file_data_encoded)
                open(file_path, 'wb').write(file_data_decoded)
        except Exception as e:
            print(f"Error in push: {e}")
            return

        print("Pushed successfully...")

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
    if len(sys.argv) != 2:
        print("Usage: krups init")
        sys.exit()

    if os.path.exists('.krups'):
        print(f"'.krups' alerady initialized...")
        sys.exit()

    vcs.init()
    sys.exit()

elif command == "status":
    if len(sys.argv) != 2:
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
    if len(sys.argv) != 2:
        print("Usage: krups rmcommit")
        sys.exit()

    vcs.rmcommit()

elif command == "checkout":
    message = " ".join(sys.argv[2:])
    if len(sys.argv) < 3:
        print("Usage: krups checkout <commit>")
        sys.exit()
    vcs.checkout(message)
    sys.exit()

elif command == "push":
    if len(sys.argv) != 3:
        print("Usage: krups push <dir_path>")
        sys.exit()

    vcs.push(sys.argv[2])
    sys.exit()

elif command == 'help':
    if len(sys.argv) != 2:
        print("Usage: krups help")
        sys.exit()

    vcs.help()
    sys.exit()

else:
    print(f"krups: '{command}' is not a krups command. See 'krups help'")
    sys.exit()

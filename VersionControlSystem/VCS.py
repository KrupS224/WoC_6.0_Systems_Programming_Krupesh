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
        self.branches_dir = os.path.join(vcs_name, "branches")
        self.objects_dir = os.path.join(vcs_name, "objects")
        self.main_branch = os.path.join(self.branches_dir, "main")
        self.added_file = os.path.join(vcs_name, "added.json")
        self.index_file = os.path.join(vcs_name, "index.json")
        self.users_file = os.path.join(vcs_name, "users.txt")
        self.commits_dir = os.path.join(self.objects_dir, "commits")
        self.rmcommits_dir = os.path.join(self.objects_dir, "rmcommits")
        self.content_dir = os.path.join(self.objects_dir, "content")

        # initialize helper classes
        self.file_handler = HandleFile()

        # set username
        self.username = self.set_username()

    def set_username(self):
        if self.notInitialized('.'):
            return None

        get_last_user = self.file_handler.get_last_commit(self.users_file)
        if not get_last_user:
            return None

        user = get_last_user.split()[2]
        return user

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
            os.makedirs(self.rmcommits_dir, exist_ok=True)
        except Exception as e:
            print(f"Error creating directories: {e}")
            return

        # Create files
        try:
            self.file_handler.create_file(self.added_file)
            self.file_handler.create_file(self.index_file)
            self.file_handler.create_file(self.users_file)
        except Exception as e:
            print(f"Error creating files: {e}")
            return

        print("New Empty .krups repository created.")

        # Append user details
        self.file_handler.append_user_details(self.users_file, username)
        self.create_branch("main")

    def create_branch(self, branch_name):
        if self.notInitialized('.'):
            print("'.krups' folder is not initialized...")
            print("Run: 'tico init' command to initialize tico repository")
            return

        try:
            branch_path = os.path.join(self.branches_dir, branch_name)
            if not os.path.exists(branch_path):
                os.makedirs(branch_path)
                print(f"Branch {branch_name} created successfully.")
                self.file_handler.create_file(
                    os.path.join(branch_path, "HEAD"))
        except Exception as e:
            print(f"Error creating branch: {e}")

        self.branch = branch_name
        HEAD_path = os.path.join(self.branches_dir, self.branch, 'HEAD')
        last_commit = self.file_handler.get_last_commit(HEAD_path)

        try:
            if not last_commit and self.branch != 'main':
                self.file_handler.clear_current_dir(os.getcwd())
                self.file_handler.write_JSON_file(self.added_file, {})
                self.file_handler.write_JSON_file(self.index_file, {})
                return
        except Exception as e:
            print(f"Error in clearing directory: {e}")

        if last_commit:
            self.checkout(last_commit)
        print("Switched to branch ", branch_name)

    def status(self):
        try:
            if self.notInitialized('.'):
                print("'.krups' folder is not initialized...")
                print("Run: 'tico init' command to initialize tico repository")
                return

            added = self.file_handler.read_JSON_file(
                self.added_file)

            tracked_files_data = None
            all_committed_files = None
            tracked_files_data, all_committed_files = self.file_handler.get_tracked_files(
                self.branches_dir, self.branch, self.commits_dir)

            untracked_files = self.file_handler.get_untracked_files(
                tracked_files_data)

            if not untracked_files and tracked_files_data and all_committed_files and tracked_files_data == all_committed_files:
                print("Your directory is up to date...")
                return

            for file_name, file_hash in tracked_files_data.items():
                tracked_files_data[file_name] = file_hash
            for file_name, file_hash in added.items():
                tracked_files_data[file_name] = file_hash

            for root, dirs, files in os.walk(os.getcwd()):
                dirs[:] = [d for d in dirs if d not in [
                    '.krups', '__pycache__', '.git']]
                files[:] = [f for f in files if f not in [
                    'VCS.py', 'HandleFile.py', '.gitignore']]

                # print("dirs: ", dirs)
                for file in files:
                    # print(file)
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
        print(added)
        tracked_files, all_committed_files = self.file_handler.get_tracked_files(
            self.branches_dir, self.branch, self.commits_dir)
        print("1st: ", tracked_files)
        tracked_files = {file_name: file_hash for file_name, file_hash in tracked_files.items(
        )} or {file_name: file_hash for file_name, file_hash in added.items()}
        print("2nd: ", tracked_files)

        untracked_files = self.file_handler.get_untracked_files(
            tracked_files)

        if not untracked_files and tracked_files and all_committed_files and tracked_files == all_committed_files:
            print("Your directory is up to date...")
            return

        untracked_files = self.file_handler.get_untracked_files(tracked_files)
        untracked_files = [
            file for file in untracked_files if file not in added.keys()]
        print(untracked_files)

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

        changes = {}
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")[:-6]

        last_commit = self.file_handler.get_last_commit(os.path.join(
            self.branches_dir, self.branch, 'HEAD'))

        committed_files = None

        if last_commit:
            committed_files = self.file_handler.get_committed_files(
                self.commits_dir, last_commit, 'index')

        added = self.file_handler.read_JSON_file(self.added_file)

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
            "branch": self.branch,
            "author": self.username
        }

        try:
            commit_data_hash = self.file_handler.compute_MD5_str(
                commit_data)
            HEAD_path = os.path.join(self.branches_dir, self.branch, 'HEAD')
            with open(HEAD_path, 'a') as head_file:
                head_file.write(commit_data_hash + '\n')
        except Exception as e:
            print(f"Error writing commit data to HEAD file: {e}")

        try:
            commit_data_encoded = base64.b64encode(
                json.dumps(commit_data).encode('utf-8'))
        except Exception as e:
            print(f"Error encoding commit data: {e}")
            return

        try:
            commit_file_path = os.path.join(self.commits_dir, commit_data_hash)
            with open(commit_file_path, 'wb') as commit_file:
                commit_file.write(commit_data_encoded)
        except Exception as e:
            print(f"Error writing commit data to file: {e}")

        for file_path, file_hash in changes.items():
            file_data_encrypted = self.file_handler.encode_base64_file(os.path.normpath(
                os.path.join(os.getcwd(), file_path)))
            with open(os.path.join(self.content_dir, file_hash), 'w') as file:
                file.write(file_data_encrypted)

        self.file_handler.write_JSON_file(self.added_file, {})

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

        second_last_commit = self.file_handler.get_second_last_commit(
            HEAD_path)

        # remove every file and directory once
        self.file_handler.clear_current_dir(os.getcwd())

        # if there was only one commit, remove that commit file too and update added.json and index.json
        if last_commit and not second_last_commit:
            try:
                commit_file_path = os.path.join(
                    self.commits_dir, last_commit)

                committed_files_last_commit = self.file_handler.get_committed_files(
                    self.commits_dir, last_commit, 'added')
                for file_path, file_hash in committed_files_last_commit.items():
                    os.remove(os.path.join(self.content_dir, file_hash))

                self.file_handler.write_JSON_file(self.added_file, {})
                self.file_handler.write_JSON_file(self.index_file, {})

                self.file_handler.remove_last_line(HEAD_path)
                # os.remove(commit_file_path)
                move_commit_file_path = os.path.join(
                    self.rmcommits_dir, last_commit)
                shutil.move(commit_file_path, move_commit_file_path)
            except Exception as e:
                print(f"Error in rmcommit: {e}")
            return

        # get all the files and directories from 2nd last commit and add them to the current directory
        committed_files = self.file_handler.get_committed_files(
            self.commits_dir, second_last_commit, 'index')
        # print(committed_files)

        try:
            for file_path, file_hash in committed_files.items():
                file_path = os.path.join(os.getcwd(), file_path)

                dir_name = os.path.dirname(file_path)
                if not os.path.exists(dir_name):
                    os.makedirs(dir_name)
        except Exception as e:
            print(f"Error in making directories: {e}")
            return

        try:
            for file_path, file_hash in committed_files.items():
                file_path_encoded_data = os.path.join(
                    self.content_dir, file_hash)
                file_path_decoded_data = os.path.normpath(file_path)

                with open(file_path_encoded_data, 'r') as encoded_file:
                    file_data_encoded = encoded_file.read()
                    file_data_decoded = self.file_handler.decode_base64_file(
                        file_data_encoded)

                with open(file_path_decoded_data, 'wb') as file:
                    file.write(file_data_decoded)
        except Exception as e:
            print(f"Error decoding and writing file: {e}")
            return

        committed_files_last_commit = self.file_handler.get_committed_files(
            self.commits_dir, last_commit, 'added')
        try:
            for file_path, file_hash in committed_files_last_commit.items():
                os.remove(os.path.join(self.content_dir, file_hash))
        except Exception as e:
            print(f"Error in removing files: {e}")

        try:
            commit_file_path = os.path.join(
                self.commits_dir, last_commit)
            move_commit_file_path = os.path.join(
                self.rmcommits_dir, last_commit)
            shutil.move(commit_file_path, move_commit_file_path)
        except Exception as e:
            print(f"Error in moving commit file: {e}")
        # os.remove(commit_file_path)

        self.file_handler.remove_last_line(HEAD_path)

        # accessing 2nd last line
        last_commit = self.file_handler.get_last_commit(HEAD_path)
        added = {} if not last_commit else self.file_handler.get_committed_files(
            self.commits_dir, last_commit, 'added')
        index = {} if not last_commit else self.file_handler.get_committed_files(
            self.commits_dir, last_commit, 'index')

        self.file_handler.write_JSON_file(self.added_file, added)
        self.file_handler.write_JSON_file(self.index_file, index)

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

    def checkout(self, hash):
        HEAD_path = os.path.join(self.branches_dir, self.branch, 'HEAD')
        all_commits = self.file_handler.read_all_lines(
            os.path.normpath(HEAD_path))

        if hash not in all_commits:
            print("Invalid commit hash...")
            return

        # removing commits after the checkout commit
        index = all_commits.index(hash)

        try:
            removing_commits = []
            for i in range(index+1, len(all_commits)):
                removing_commits.append(all_commits[i])

            for commit in removing_commits:
                commit_files = self.file_handler.get_committed_files(
                    self.commits_dir, commit, 'added')
                for file_name, file_hash in commit_files.items():
                    if os.path.exists(os.path.join(self.content_dir, file_hash)):
                        os.remove(os.path.join(self.content_dir, file_hash))

                # moving commit file
                try:
                    commit_file_path = os.path.join(self.commits_dir, commit)
                    move_commit_file_path = os.path.join(
                        self.rmcommits_dir, commit)
                    shutil.move(commit_file_path, move_commit_file_path)
                except Exception as e:
                    print(f"Error in moving commit file: {e}")
        except Exception as e:
            print(f"Error removing commits: {e}")

        # updating HEAD file
        try:
            earlier_commits = ""

            for i in range(0, index+1):
                earlier_commits += all_commits[i] + '\n'

            with open(HEAD_path, 'w') as head_file:
                head_file.write(earlier_commits)
                head_file.close()
        except Exception as e:
            print(f"Error updating HEAD file: {e}")

        # remove all the files and directories
        self.file_handler.clear_current_dir(os.getcwd())

        added_files = self.file_handler.get_committed_files(
            self.commits_dir, hash, 'added')
        index_files = self.file_handler.get_committed_files(
            self.commits_dir, hash, 'index')

        # make files and dirs
        try:
            for file_path, file_hash in index_files.items():
                file_path = os.path.join(os.getcwd(), file_path)

                dir_name = os.path.dirname(file_path)
                if not os.path.exists(dir_name):
                    os.makedirs(dir_name)
        except Exception as e:
            print(f"Error creating directories: {e}")

        try:
            for file_path, file_hash in index_files.items():
                file_path_encoded_data = os.path.join(
                    self.content_dir, file_hash)
                file_path_decoded_data = os.path.normpath(file_path)

                file_data_encoded = open(file_path_encoded_data, 'r').read()
                file_data_decoded = self.file_handler.decode_base64_file(
                    file_data_encoded)

                with open(file_path_decoded_data, 'wb') as file:
                    file.write(file_data_decoded)

            # updating added.json and index.json
            self.file_handler.write_JSON_file(self.added_file, added_files)
            self.file_handler.write_JSON_file(self.index_file, index_files)

        except Exception as e:
            print(f"Error decoding and writing file: {e}")

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

        committed_files = self.file_handler.get_committed_files(
            self.commits_dir, last_commit, 'index')

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

    def log(self):
        if self.notInitialized('.'):
            print("'.krups' folder is not initialized...")
            print("Run: 'tico init' command to initialize tico repository")
            return

        HEAD_path = os.path.join(self.branches_dir, self.branch, 'HEAD')
        all_commits = self.file_handler.read_all_lines(HEAD_path)
        removed_commits = os.listdir(self.rmcommits_dir)

        if not all_commits and not removed_commits:
            print("No logs available...")
            return

        print()
        print("*"*34, " Commits ", "*"*34)
        print()

        for commit_file in all_commits:
            commit_file_path = os.path.join(self.commits_dir, commit_file)
            commit_file_encoded_data = open(commit_file_path, 'rb').read()
            commit_file_decoded_data = base64.b64decode(
                commit_file_encoded_data).decode('utf-8')
            commit_file_decoded_data = json.loads(commit_file_decoded_data)

            print(f"Commit: {commit_file}")
            print(f"Author: {commit_file_decoded_data['author']}")
            print(f"Message: {commit_file_decoded_data['message']}")
            print(f"Timestamp: {commit_file_decoded_data['timestamp']}")
            print(f"Branch: {commit_file_decoded_data['branch']}")
            print("-"*60)
            print("Added / Modified files:")
            for file_path, file_hash in commit_file_decoded_data['added'].items():
                print(f"\t{file_path}: {file_hash}")
            print("-"*60)
            print("All files:")
            for file_path, file_hash in commit_file_decoded_data['index'].items():
                print(f"\t{file_path}: {file_hash}")

            print()
            print("*"*79)
            print()

        if not all_commits:
            print("No commit data available......\n")
            print("*"*79)
            print()

        print()
        print("*"*30, " Removed commits ", "*"*30)
        print()

        for rmcommit in removed_commits:
            rmcommit_file_path = os.path.join(self.rmcommits_dir, rmcommit)
            rmcommit_file_encoded_data = open(rmcommit_file_path, 'rb').read()
            rmcommit_file_decoded_data = base64.b64decode(
                rmcommit_file_encoded_data).decode('utf-8')
            rmcommit_file_decoded_data = json.loads(rmcommit_file_decoded_data)

            print(f"Removed commit: {rmcommit}")
            print(f"Author: {rmcommit_file_decoded_data['author']}")
            print(f"Message: {rmcommit_file_decoded_data['message']}")
            print(f"Timestamp: {rmcommit_file_decoded_data['timestamp']}")
            print(f"Branch: {rmcommit_file_decoded_data['branch']}")
            print("-"*60)
            print("Added / Modified files:")
            for file_path, file_hash in rmcommit_file_decoded_data['added'].items():
                print(f"\t{file_path}: {file_hash}")
            print("-"*60)
            print("All files:")
            for file_path, file_hash in rmcommit_file_decoded_data['index'].items():
                print(f"\t{file_path}: {file_hash}")

            print()
            print("*"*79)
            print()

        if not removed_commits:
            print("No commits removed......\n")
            print("*"*79)
            print()

    def user_set(self, newUsername):
        try:
            lines = self.file_handler.read_all_lines(self.users_file)
            userIdx = -1
            for line in lines:
                words = line.split()
                if newUsername in words:
                    print("Username already exists...")
                    return
                if self.username in words:
                    userIdx = lines.index(line)
                    break

            del lines[userIdx]

            with open(self.users_file, 'w') as users_file:
                for line in lines:
                    users_file.write(line + '\n')

            self.file_handler.append_user_details(self.users_file, newUsername)
            self.username = self.set_username()
        except Exception as e:
            print("Error in updating username:", e)

    def user_show(self):
        print(self.username)

    def user_add(self, username):
        lines = self.file_handler.read_all_lines(self.users_file)
        # print(lines)
        for line in lines:
            words = line.split()
            if username in words:
                print("Username already exists...")
                return

        self.file_handler.append_user_details(self.users_file, username)
        self.username = username

    def user_remove(self, username):
        try:
            lines = self.file_handler.read_all_lines(self.users_file)
            present = False
            for index, line in enumerate(lines):
                words = line.split()
                if username in words:
                    del lines[index]
                    present = True
                    break

            if not present:
                print("Username not found...")
                return

            with open(self.users_file, 'w') as users_file:
                for line in lines:
                    users_file.write(line + '\n')

            if self.username == username:
                self.username = self.set_username()
        except Exception as e:
            print("Error in removing username:", e)

    def user_change(self, username):
        try:
            lines = self.file_handler.read_all_lines(self.users_file)
            present = False
            for index, line in enumerate(lines):
                words = line.split()
                if username in words:
                    line = line.replace(words[2], username)
                    present = True
                    break

            if not present:
                print("Username not found...")
                return

            with open(self.users_file, 'w') as users_file:
                for line in lines:
                    users_file.write(line + '\n')
            self.username = username
        except Exception as e:
            print("Error in changing username:", e)

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
        print("tico user add <username> - to add new user")
        print("tico user remove <username> - to remove user")
        print("tico user change <username> - to change user")
        print("tico push <path> - to push your file to another folder")
        print(
            "tico branch <branch_name> - to create a new branch or switch to another branch")
        print("Created by - Krupesh Parmar")


vcs = VersionControlSystem('.krups')


while True:
    args = input(
        "\nEnter command (enter 'exit' to exit the program): ").split()
    command = args[0]

    if command == "init":
        if len(args) != 1:
            print("Usage: init")
            continue

        if os.path.exists('.krups'):
            print(f"'.krups' already initialized...")
            continue

        vcs.init()

    elif command == "status":
        if len(args) != 1:
            print("Usage: status")
            continue

        vcs.status()

    elif command == "add":
        if len(args) < 2:
            print("Usage: add <files>")
            continue

        for arg in args[1:]:
            vcs.add_with_subdirs(arg)

    elif command == "rmadd":
        if len(args) < 2:
            print("Usage: rmadd <files>")
            continue

        for arg in args[1:]:
            vcs.rmadd_with_subdirs(arg)

    elif command == "commit":
        if len(args) == 1:
            vcs.commit()
        elif len(args) >= 3 and args[1] == '-m':
            message = ' '.join(args[2:])[1:-1]
            vcs.commit(message)
        else:
            print("Usage: commit -m \"<message>\"")

    elif command == "rmcommit":
        if len(args) != 1:
            print("Usage: rmcommit")
            continue

        vcs.rmcommit()

    elif command == "checkout":
        if len(args) < 2:
            print("Usage: checkout <commit hash>")
            continue

        hash = args[1]
        vcs.checkout(hash)

    elif command == "push":
        if len(args) != 2:
            print("Usage: push <dir_path>")
            continue

        vcs.push(args[1])

    elif command == "branch":
        if len(args) != 2:
            print("Usage: branch <branch_name>")
            continue

        vcs.create_branch(args[1])

    elif command == "log":
        if len(args) != 1:
            print("Usage: log")
            continue

        vcs.log()

    elif command == "user":
        if vcs.notInitialized('.'):
            print("'.krups' folder is not initialized...")
            print("Run: 'tico init' command to initialize tico repository")
            continue

        if len(args) < 2:
            print("Usage: user show")
            print("Usage: user set <username>")
            print("Usage: user add <username>")
            print("Usage: user remove <username>")
            print("Usage: user change <username>")
            continue

        sub_command = args[1]
        if sub_command == 'set':
            vcs.user_set(args[2])
        elif sub_command == 'show':
            vcs.user_show()
        elif sub_command == 'add':
            vcs.user_add(args[2])
        elif sub_command == 'remove':
            vcs.user_remove(args[2])
        elif sub_command == 'change':
            vcs.user_change(args[2])
        else:
            print("Usage: user show")
            print("Usage: user set <username>")
            print("Usage: user add <username>")
            print("Usage: user remove <username>")
            print("Usage: user change <username>")
            continue

    elif command == 'help':
        if len(args) != 1:
            print("Usage: help")
            continue

        vcs.help()

    elif command == 'exit':
        if len(args) != 1:
            print("Usage: exit")
            continue

        print("Exiting...")
        # vcs.create_branch("main")
        sys.exit()

    else:
        print(f"krups: '{command}' is not a valid command. See 'help'")
        continue

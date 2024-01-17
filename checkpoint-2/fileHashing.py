import shutil
import sys
import hashlib
import os
import json


def compute_MD5(file_path):
    BUF_SIZE = 65536
    md5 = hashlib.md5()

    with open(file_path, 'rb') as file:
        while True:
            data = file.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)

    return md5.hexdigest()


def handle_copying():
    new_directory_path = input("Enter the new directory path: ")
    if not os.path.exists(new_directory_path):
        os.makedirs(new_directory_path, exist_ok=True)

    with open("files_info.json", "r") as file:
        files_info_JSON = json.load(file)

    for file in files_info_JSON:
        # file_path = files_info_JSON[file]["path"]
        new_file_path = os.path.join(new_directory_path, file)
        shutil.copy(files_info_JSON[file]["path"], new_file_path)
        files_info_JSON[file]["path"] = os.path.abspath(new_file_path)
        # print(files_info_JSON[file]["path"], new_file_path)

    with open("files_info.json", "w") as file:
        json.dump(files_info_JSON, file, indent=4)

    print("File copying successful.")
    print(f"Files copied to {os.path.abspath(new_directory_path)}")


def organize_directory(directory_path):
    directory_path = os.path.abspath(directory_path)
    if not os.path.exists(directory_path):
        print(f"The specified directory path does not exist: {directory_path}")

    files_info_JSON = dict()
    files = [f for f in os.listdir(directory_path) if os.path.isfile(
        os.path.join(directory_path, f))]
    # print(files)

    for file in files:
        # print(file)
        file_path = os.path.join(directory_path, file)
        file_size = os.path.getsize(file_path)
        file_hash_MD5 = compute_MD5(file_path)
        # print(file_path, file_size, file_hash_MD5)

        files_info_JSON[file] = {
            "size": file_size,
            "path": file_path,
            "hash": file_hash_MD5,
        }

    with open("files_info.json", "w") as file:
        json.dump(files_info_JSON, file, indent=4)

    print("File hashing successful.")
    print(f"File information stored in {os.path.abspath('files_info.json')}")

# Bonus Task: Implement a function to copy all files from the specified directory to a new directory, keeping the
#             same file structure. Update the JSON file with the new file paths in the copied directory

    ans = input("Do you want to copy the files to a new directory? (y/n): ")
    if ans.lower() == 'y':
        handle_copying()


if len(sys.argv) < 2:
    print("Usage: python fileHashing.py <directory_path>")
    sys.exit(1)

directory_path = sys.argv[1]

organize_directory(directory_path)

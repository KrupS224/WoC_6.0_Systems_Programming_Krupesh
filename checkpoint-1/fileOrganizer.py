import os
import shutil


def organize_files(directory_path):
    if not os.path.exists(directory_path):
        print("The specified directory path does not exist.")
        print(f"Path: {directory_path}")
        print("Please enter a valid directory path.")
        return

    files = [f for f in os.listdir(directory_path) if os.path.isfile(
        os.path.join(directory_path, f))]
    # print(files)

    for file in files:
        if os.path.isfile(os.path.join(directory_path, file)):
            file_extension = os.path.splitext(
                file)[1][1:]
            # print(file_extension)
            if not file_extension:
                file_extension = 'Other'

            subdirectory_path = os.path.join(directory_path, file_extension)
            os.makedirs(subdirectory_path, exist_ok=True)

            current_file_path = os.path.join(directory_path, file)
            new_file_path = os.path.join(subdirectory_path, file)
            # print(new_file_path)
            shutil.move(current_file_path, new_file_path)

    print("File organization successful.")


dir_path = input("Enter the directory path: ")
organize_files(dir_path)

import os

def count_all_files(folder_path):
    file_count = 0
    for root, dirs, files in os.walk(folder_path):
        file_count += len(files)
    print(f"Total number of files in '{folder_path}' and its subfolders: {file_count}")
    return file_count

# Example usage
folder_path = '../downloaded_images'
count_all_files(folder_path)

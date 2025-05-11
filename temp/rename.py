import os

def rename_all_files_recursive(base_dir):
    count = 1
    for root, _, files in os.walk(base_dir):
        files.sort()  # Optional: sort alphabetically within each folder
        for filename in files:
            ext = os.path.splitext(filename)[1]
            new_name = f"{count}{ext}"
            old_path = os.path.join(root, filename)
            new_path = os.path.join(root, new_name)

            # Ensure no overwrite
            while os.path.exists(new_path):
                count += 1
                new_name = f"{count}{ext}"
                new_path = os.path.join(root, new_name)

            os.rename(old_path, new_path)
            print(f"Renamed: {old_path} -> {new_path}")
            count += 1

# 🔧 Replace with your folder path
rename_all_files_recursive("../downloaded_images - Copy")

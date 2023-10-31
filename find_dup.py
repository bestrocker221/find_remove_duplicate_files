import os
import hashlib
import argparse
from concurrent.futures import ThreadPoolExecutor
import time

def hash_file(file_path, block_size=512000, max_retries=300, retry_interval=0.1):
    """Generate the hash of a file with error handling and retry logic."""
    for i in range(max_retries):
        try:
            with open(file_path, 'rb') as file:
                hasher = hashlib.md5()
                buffer = file.read(block_size)
                while len(buffer) > 0:
                    hasher.update(buffer)
                    buffer = file.read(block_size)
                return hasher.hexdigest()
        except OSError as e:
            if i < max_retries - 1:
                print(f"Encountered error: {e}. Retrying...")
                time.sleep(retry_interval * (2 ** i))
            else:
                print(f"Failed to read file: {file_path} after {max_retries} retries. Error: {e}")
                return None

def find_duplicate_files_helper(args):
    dirpath, filename, hash_dict, log_file_path = args
    file_path = os.path.join(dirpath, filename)
    file_hash = hash_file(file_path)
    if file_hash in hash_dict:
        print(f"Duplicate found: {file_path}\n")
        print(f"Original: {hash_dict[file_hash]}\n")
        with open(log_file_path, "a") as log_file:
            # todo: add file lock mechanism
            log_file.write(f"Duplicate found: {file_path}\n")
            log_file.write(f"Original: {hash_dict[file_hash]}\n")
        return file_path
    else:
        hash_dict[file_hash] = file_path
        return None

def find_duplicate_files(directory, log_file_path):
    """Find duplicate files in a directory and log the paths to a file."""
    hash_dict = {}
    duplicates = []
    total_files = 0
    with ThreadPoolExecutor(max_workers=60) as executor:
        print("Walking dirs..")
        for dirpath, _, filenames in os.walk(directory):
            #print("dirs walked.")
            #print(f"Dir {dirpath} walked.")
            args_list = [(dirpath, filename, hash_dict, log_file_path) for filename in filenames]
            results = executor.map(find_duplicate_files_helper, args_list)
            for result in results:
                total_files += 1
                if result is not None:
                    duplicates.append(result)
    return total_files, duplicates

def calculate_total_space_from_file(file_path):
    """Calculate the total amount of space used by the files listed in a file."""
    total_space = 0
    with open(file_path, 'r') as file:
        file_paths = file.read().splitlines()
        file_paths_duponly = [line for line in file_paths if "Duplicate found" in line]
        path_list = [line[line.find("./"):] for line in file_paths_duponly]
        for path in path_list:
            if os.path.exists(path):
                total_space += os.path.getsize(path)
            else:
                print(f"File not found: {path}")
    return total_space

def delete_duplicates(file_path):
    """Delete the files listed in a file."""
    with open(file_path, 'r') as file:
        file_paths = file.read().splitlines()
        file_paths_duponly = [line for line in file_paths if "Duplicate found" in line]
        path_list = [line[line.find("./"):] for line in file_paths_duponly]
        for path in path_list:
            if os.path.exists(path):
                try:
                    os.remove(path)
                    print(f"Deleted file: {path}")
                except OSError as e:
                    print(f"Error deleting file: {path}. {e}")
            else:
                print(f"File not found: {path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Find duplicate files in a directory.')
    parser.add_argument('--delete-duplicated', action='store_true', help='Delete duplicates if this flag is set')
    parser.add_argument('path', type=str, help='Path to examine for duplicate files')

    args = parser.parse_args()

    directory_path = args.path
    log_file_path = "duplicates.txt"
    total_files, duplicate_files = find_duplicate_files(directory_path, log_file_path)
    if duplicate_files:
        print(f"Duplicates found. Total files scanned: {total_files}, Total duplicates: {len(duplicate_files)}.")
        print("Duplicate files:")
        for file in duplicate_files:
            print(file)
    else:
        print(f"No duplicates found. Total files scanned: {total_files}.")

    total_space_used = calculate_total_space_from_file(log_file_path)
    # in MB
    size_in_megabytes = total_space_used / (1024 * 1024)

    print(f"Total space used by the files: {size_in_megabytes} Megabytes")

    if args.delete_duplicated:
        delete_duplicates(log_file_path)


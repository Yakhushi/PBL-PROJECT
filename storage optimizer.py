import os
import hashlib
import random

# -------------------------------
# CONFIGURATION
# -------------------------------
LARGE_FILE_THRESHOLD_MB = 5  # Files larger than 5 MB considered large

# Simulated cloud storage (in MB)
clouds = [
    {"name": "Google Drive", "free_space": 1500},
    {"name": "OneDrive", "free_space": 5000},
    {"name": "Dropbox", "free_space": 2000}
]


# -------------------------------
# STORAGE SCANNING
# -------------------------------
def get_file_hash(file_path):
    """Generate MD5 hash of file"""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(4096):
            hasher.update(chunk)
    return hasher.hexdigest()


def scan_storage(folder_path):
    large_files = []
    duplicates = []
    seen_hashes = {}

    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)

            try:
                size_mb = os.path.getsize(file_path) / (1024 * 1024)

                # Check for large files
                if size_mb > LARGE_FILE_THRESHOLD_MB:
                    large_files.append((file_path, round(size_mb, 2)))

                # Check for duplicates
                file_hash = get_file_hash(file_path)
                if file_hash in seen_hashes:
                    duplicates.append(file_path)
                else:
                    seen_hashes[file_hash] = file_path

            except Exception as e:
                print("Error reading file:", file_path)

    return large_files, duplicates


# -------------------------------
# CLOUD SELECTION
# -------------------------------
def select_best_cloud(cloud_list):
    best = max(cloud_list, key=lambda x: x["free_space"])
    return best


# -------------------------------
# UPLOAD SIMULATION
# -------------------------------
def upload_file(file_path, cloud):
    print(f"Uploading {file_path} to {cloud['name']}...")
    # Simulate upload delay
    print("Upload successful.\n")


# -------------------------------
# MAIN WORKFLOW
# -------------------------------
def main():
    folder_to_scan = input("Enter folder path to scan: ")

    print("\nScanning storage...\n")
    large_files, duplicate_files = scan_storage(folder_to_scan)

    print("Large Files Detected:")
    for file, size in large_files:
        print(f"{file} - {size} MB")

    print("\nDuplicate Files Detected:")
    for file in duplicate_files:
        print(file)

    # Combine files suggested for offloading
    suggested_files = [f[0] for f in large_files] + duplicate_files

    if not suggested_files:
        print("\nNo files suggested for offloading.")
        return

    best_cloud = select_best_cloud(clouds)
    print(f"\nBest Cloud Selected: {best_cloud['name']}")
    print(f"Available Free Space: {best_cloud['free_space']} MB\n")

    for file in suggested_files:
        upload_file(file, best_cloud)


if __name__ == "__main__":
    main()

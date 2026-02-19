import os
import hashlib

def file_hash(path):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()

def scan_storage(folder, size_limit_mb=5):
    seen = {}
    large_files = []
    duplicates = []

    for root, _, files in os.walk(folder):
        for file in files:
            path = os.path.join(root, file)
            try:
                size_mb = os.path.getsize(path) / (1024 * 1024)
                if size_mb > size_limit_mb:
                    large_files.append(path)

                h = file_hash(path)
                if h in seen:
                    duplicates.append(path)
                else:
                    seen[h] = path
            except:
                pass

    return large_files, duplicates

large, dup = scan_storage("test_folder")
print("Large Files:", large)
print("Duplicate Files:", dup)

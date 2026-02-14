import os
import hashlib
import time
import streamlit as st

# -------------------------------
# CONFIGURATION
# -------------------------------
LARGE_FILE_THRESHOLD_MB = 5
clouds = [
    {"name": "Google Drive", "free_space": 1500},
    {"name": "OneDrive", "free_space": 5000},
    {"name": "Dropbox", "free_space": 2000}
]

# -------------------------------
# FUNCTIONS
# -------------------------------
def get_file_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(4096):
            hasher.update(chunk)
    return hasher.hexdigest()

def scan_storage(folder):
    large_files = []
    duplicates = []
    seen_hashes = {}
    for root, _, files in os.walk(folder):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                size_mb = os.path.getsize(file_path) / (1024*1024)
                if size_mb > LARGE_FILE_THRESHOLD_MB:
                    large_files.append((file_path, round(size_mb, 2)))
                file_hash = get_file_hash(file_path)
                if file_hash in seen_hashes:
                    duplicates.append(file_path)
                else:
                    seen_hashes[file_hash] = file_path
            except:
                pass
    return large_files, duplicates

def select_best_cloud(cloud_list):
    return max(cloud_list, key=lambda x: x["free_space"])

# -------------------------------
# STREAMLIT APP
# -------------------------------
st.title("📁 Storage Scanner & Cloud Upload Demo")

folder_to_scan = st.text_input("Enter folder path to scan:", "")

if st.button("Scan Storage") and folder_to_scan:
    if not os.path.exists(folder_to_scan):
        st.error("Folder path does not exist!")
    else:
        st.info("Scanning storage...")
        large_files, duplicate_files = scan_storage(folder_to_scan)

        st.subheader("🗂 Large Files Detected")
        if large_files:
            for file, size in large_files:
                st.write(f"{file} - {size} MB")
        else:
            st.write("No large files found.")

        st.subheader("📑 Duplicate Files Detected")
        if duplicate_files:
            for file in duplicate_files:
                st.write(file)
        else:
            st.write("No duplicate files found.")

        suggested_files = [f[0] for f in large_files] + duplicate_files
        if suggested_files:
            best_cloud = select_best_cloud(clouds)
            st.success(f"Best Cloud Selected: {best_cloud['name']} ({best_cloud['free_space']} MB free)")

            st.subheader("⬆ Uploading Suggested Files")
            for file in suggested_files:
                st.write(f"Uploading {file}...")
                progress = st.progress(0)
                for i in range(1, 101):
                    progress.progress(i)
                    time.sleep(0.01)
                st.success(f"Upload of {file} complete ✅\n")
        else:
            st.info("No files suggested for offloading.")

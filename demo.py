# demo.py
import streamlit as st
import os
import hashlib
import time

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
    """Generate MD5 hash of a file."""
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
                st.warning(f"Error reading file: {file_path}")
    return large_files, duplicates

# -------------------------------
# CLOUD SELECTION
# -------------------------------
def select_best_cloud(cloud_list):
    return max(cloud_list, key=lambda x: x["free_space"])

# -------------------------------
# UPLOAD SIMULATION
# -------------------------------
def upload_file(file_path, cloud):
    st.write(f"Uploading **{file_path}** to {cloud['name']}...")
    progress_bar = st.progress(0)
    for i in range(1, 101):
        progress_bar.progress(i)
        time.sleep(0.01)  # Simulate upload delay
    st.success(f"Upload of {file_path} complete ✅")

# -------------------------------
# STREAMLIT INTERFACE
# -------------------------------
st.title("📁 Storage Scanner & Cloud Upload Demo")

folder = st.text_input("Enter folder path to scan:", "test_folder")

if st.button("Scan Storage"):
    if not os.path.exists(folder):
        st.error("Folder path does not exist!")
    else:
        st.info("Scanning storage...")
        large_files, duplicate_files = scan_storage(folder)

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

        # Combine files suggested for offloading
        suggested_files = [f[0] for f in large_files] + duplicate_files
        if suggested_files:
            best_cloud = select_best_cloud(clouds)
            st.success(f"Best Cloud Selected: {best_cloud['name']} with {best_cloud['free_space']} MB free space\n")

            st.subheader("⬆ Uploading Suggested Files")
            for file in suggested_files:
                upload_file(file, best_cloud)
        else:
            st.info("No files suggested for offloading.")

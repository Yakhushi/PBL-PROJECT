# demo_gui.py
import os
import hashlib
import time
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

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

def scan_storage(folder_path):
    large_files = []
    duplicates = []
    seen_hashes = {}

    for root, _, files in os.walk(folder_path):
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

def upload_file(file_path, cloud, text_widget):
    text_widget.insert(tk.END, f"Uploading {file_path} to {cloud['name']}...\n")
    text_widget.see(tk.END)
    # simulate upload delay
    for i in range(1, 6):
        text_widget.insert(tk.END, f"{'.'*i}\n")
        text_widget.see(tk.END)
        time.sleep(0.2)
    text_widget.insert(tk.END, f"Upload of {file_path} complete ✅\n\n")
    text_widget.see(tk.END)

# -------------------------------
# GUI SETUP
# -------------------------------
def start_demo():
    folder = filedialog.askdirectory(title="Select Folder to Scan")
    if not folder:
        return

    text_area.delete("1.0", tk.END)
    text_area.insert(tk.END, f"Scanning folder: {folder}\n\n")

    large_files, duplicates = scan_storage(folder)

    text_area.insert(tk.END, "Large Files Detected:\n")
    if large_files:
        for file, size in large_files:
            text_area.insert(tk.END, f"{file} - {size} MB\n")
    else:
        text_area.insert(tk.END, "No large files found.\n")

    text_area.insert(tk.END, "\nDuplicate Files Detected:\n")
    if duplicates:
        for file in duplicates:
            text_area.insert(tk.END, f"{file}\n")
    else:
        text_area.insert(tk.END, "No duplicate files found.\n")

    # Suggested files to upload
    suggested_files = [f[0] for f in large_files] + duplicates
    if suggested_files:
        best_cloud = select_best_cloud(clouds)
        text_area.insert(tk.END, f"\nBest Cloud Selected: {best_cloud['name']} ({best_cloud['free_space']} MB free)\n\n")
        text_area.insert(tk.END, "Uploading suggested files:\n\n")
        for file in suggested_files:
            upload_file(file, best_cloud, text_area)
    else:
        text_area.insert(tk.END, "\nNo files suggested for offloading.\n")

# -------------------------------
# MAIN WINDOW
# -------------------------------
root = tk.Tk()
root.title("Storage Scanner Demo")

btn_scan = tk.Button(root, text="Select Folder & Scan", command=start_demo)
btn_scan.pack(pady=10)

text_area = scrolledtext.ScrolledText(root, width=80, height=25)
text_area.pack(padx=10, pady=10)

root.mainloop()

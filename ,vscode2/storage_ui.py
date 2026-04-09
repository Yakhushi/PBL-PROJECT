
import os
import hashlib
import time
from pathlib import Path
import streamlit as st
import pandas as pd

st.set_page_config(page_title="StorageMind", page_icon="🗄️", layout="wide")

# -----------------------------
# DETECT CLOUD / LOCAL
# -----------------------------
RUNNING_ON_CLOUD = os.getenv("STREAMLIT_SHARING_MODE") is not None

# -----------------------------
# CONFIG
# -----------------------------
SENSITIVE_EXTENSIONS = {'.pdf', '.docx', '.xlsx', '.txt', '.csv'}
MEDIA_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.mp4', '.mov'}
TEMP_EXTENSIONS = {'.tmp', '.log', '.cache', '.bak'}

# -----------------------------
# HASH FUNCTIONS
# -----------------------------
def get_hash_bytes(data):
    return hashlib.md5(data).hexdigest()

def get_file_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path,'rb') as f:
        while chunk := f.read(4096):
            hasher.update(chunk)
    return hasher.hexdigest()

# -----------------------------
# SCAN LOCAL FOLDER
# -----------------------------
def scan_folder(folder):

    files_data=[]
    seen_hashes={}
    now=time.time()

    for root,_,files in os.walk(folder):

        for file in files:

            path=os.path.join(root,file)

            try:
                size_kb=os.path.getsize(path)/1024
                modified=os.path.getmtime(path)
                days_old=(now-modified)/86400
                ext=Path(file).suffix.lower()

                file_hash=get_file_hash(path)

                is_dupe=False
                if file_hash in seen_hashes:
                    is_dupe=True
                else:
                    seen_hashes[file_hash]=path

                files_data.append({
                    "name":file,
                    "path":path,
                    "size_kb":round(size_kb,2),
                    "days_old":round(days_old),
                    "ext":ext,
                    "is_dupe":is_dupe
                })

            except:
                pass

    return files_data

# -----------------------------
# SCAN UPLOADED FILES
# -----------------------------
def scan_uploads(uploaded_files):

    files_data=[]
    seen_hashes={}

    for file in uploaded_files:

        data=file.read()
        size_kb=len(data)/1024
        ext=Path(file.name).suffix.lower()

        file_hash=get_hash_bytes(data)

        is_dupe=False
        if file_hash in seen_hashes:
            is_dupe=True
        else:
            seen_hashes[file_hash]=file.name

        files_data.append({
            "name":file.name,
            "path":file.name,
            "size_kb":round(size_kb,2),
            "days_old":0,
            "ext":ext,
            "is_dupe":is_dupe
        })

    return files_data

# -----------------------------
# SCORING ENGINE
# -----------------------------
def score_file(f):

    score=0

    score+=min(f["size_kb"]/200,4)
    score+=min(f["days_old"]/45,3)

    if f["is_dupe"]:
        score+=2

    if f["ext"] in TEMP_EXTENSIONS:
        score+=1

    return round(min(score,10),1)

# -----------------------------
# ROUTING ENGINE
# -----------------------------
def route_file(f,score):

    if f["is_dupe"]:
        return "Duplicate → Delete"

    if f["ext"] in SENSITIVE_EXTENSIONS:
        return "USB Backup"

    if score>=7:
        return "Permanent Cloud"

    if score>=3:
        return "Temp Cloud"

    return "Keep Local"

# -----------------------------
# UI
# -----------------------------
st.title("🗄️ StorageMind")
st.caption("AI Inspired Storage Optimization Engine")

st.success("Smart file analysis using hashing, storage scoring, and intelligent routing.")

st.divider()

st.subheader("Choose Input Method")

# Different UI for cloud vs local
if RUNNING_ON_CLOUD:

    st.info("🌐 Web version detected — upload files to scan")

    folder_path=""
    uploaded_files=st.file_uploader(
        "Upload files",
        accept_multiple_files=True
    )

else:

    st.info("💻 Local version — folder scanning available")

    folder_path=st.text_input("Scan Folder Path")
    uploaded_files=st.file_uploader(
        "OR Upload files",
        accept_multiple_files=True
    )

scan=st.button("🚀 Scan Storage")

# -----------------------------
# PROCESS
# -----------------------------
if scan:

    files_data=[]

    if folder_path:

        folder=Path(folder_path)

        if not folder.exists():
            st.error("❌ Folder not found.")
            st.stop()

        files_data=scan_folder(folder)

    elif uploaded_files:

        files_data=scan_uploads(uploaded_files)

    else:

        st.warning("Please provide folder path OR upload files.")
        st.stop()

    # scoring
    for f in files_data:
        f["score"]=score_file(f)
        f["destination"]=route_file(f,f["score"])

    # -----------------------------
    # SUMMARY
    # -----------------------------
    total=len(files_data)
    dupes=sum(1 for f in files_data if f["is_dupe"])
    total_size=sum(f["size_kb"] for f in files_data)

    col1,col2,col3=st.columns(3)

    col1.metric("📁 Files Scanned",total)
    col2.metric("🔁 Duplicates",dupes)
    col3.metric("💾 Total Size (KB)",round(total_size,2))

    st.divider()

    # -----------------------------
    # TABLE VIEW
    # -----------------------------
    df=pd.DataFrame(files_data)

    def highlight_rows(row):

        if row["is_dupe"]:
            return ["background-color:#ffcccc"]*len(row)

        if row["size_kb"]>500:
            return ["background-color:#ccffcc"]*len(row)

        return [""]*len(row)

    st.subheader("📊 File Decisions")

    styled_df=df.style.apply(highlight_rows,axis=1)

    st.dataframe(styled_df,use_container_width=True)

    # -----------------------------
    # LEGEND
    # -----------------------------
    st.divider()

    st.markdown("### Legend")

    st.markdown("🔴 **Red rows → Duplicate files (recommended deletion)**")
    st.markdown("🟢 **Green rows → Large files (better suited for cloud storage)**")

import os
import hashlib
import time
from pathlib import Path
import streamlit as st

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="StorageMind",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Mono', monospace;
    background-color: #0c0c0f;
    color: #e2e2e8;
}

h1, h2, h3 {
    font-family: 'Syne', sans-serif;
}

/* Main container bg */
.stApp {
    background: #0c0c0f;
}

/* Metric cards */
.metric-card {
    background: #16161d;
    border: 1px solid #2a2a38;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 12px;
}

.metric-label {
    font-size: 11px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #6b6b80;
    margin-bottom: 6px;
}

.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 28px;
    font-weight: 700;
    color: #e2e2e8;
}

/* File row cards */
.file-row {
    background: #13131a;
    border: 1px solid #22222f;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 12px;
}

/* Destination badges */
.badge {
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 10px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-weight: 500;
}
.badge-temp    { background: #2a1f00; color: #f0a500; border: 1px solid #3d2c00; }
.badge-perm    { background: #001a2e; color: #4da6ff; border: 1px solid #003052; }
.badge-usb     { background: #1a0015; color: #d966ff; border: 1px solid #2e0028; }
.badge-keep    { background: #0d1f0d; color: #4caf50; border: 1px solid #1a3a1a; }
.badge-dupe    { background: #1f1000; color: #ff7a00; border: 1px solid #3a1e00; }

/* Section headers */
.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #6b6b80;
    padding: 18px 0 8px 0;
    border-bottom: 1px solid #1e1e2a;
    margin-bottom: 12px;
}

/* Progress bar custom */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #4da6ff, #a855f7);
}

/* Button style */
.stButton > button {
    background: #1a1a27;
    color: #e2e2e8;
    border: 1px solid #3a3a52;
    border-radius: 8px;
    font-family: 'DM Mono', monospace;
    font-size: 13px;
    padding: 10px 24px;
    transition: all 0.15s ease;
}
.stButton > button:hover {
    background: #22223a;
    border-color: #4da6ff;
    color: #4da6ff;
}

/* Input style */
.stTextInput > div > div > input {
    background: #13131a;
    border: 1px solid #2a2a38;
    border-radius: 8px;
    color: #e2e2e8;
    font-family: 'DM Mono', monospace;
    font-size: 13px;
}

/* Divider */
hr { border-color: #1e1e2a; }

/* Score bar container */
.score-bar-wrap {
    background: #1e1e2a;
    border-radius: 4px;
    height: 6px;
    width: 80px;
    display: inline-block;
    vertical-align: middle;
    margin-left: 8px;
}
.score-bar-fill {
    height: 6px;
    border-radius: 4px;
    background: linear-gradient(90deg, #4da6ff, #a855f7);
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
LARGE_FILE_THRESHOLD_KB = 6

SENSITIVE_EXTENSIONS = {'.pdf', '.docx', '.xlsx', '.txt', '.csv', '.pptx', '.doc'}
MEDIA_EXTENSIONS     = {'.jpg', '.jpeg', '.png', '.mp4', '.mov', '.avi', '.mkv', '.gif', '.heic'}
TEMP_EXTENSIONS      = {'.tmp', '.log', '.cache', '.bak', '.temp'}

CLOUDS = [
    {"name": "Google Drive", "free_mb": 1500,  "type": "temp"},
    {"name": "OneDrive",     "free_mb": 5000,  "type": "perm"},
    {"name": "Dropbox",      "free_mb": 2000,  "type": "temp"},
]

# ─────────────────────────────────────────────
# CORE FUNCTIONS
# ─────────────────────────────────────────────
def get_file_hash(file_path):
    hasher = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(4096):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return None


def scan_storage(folder):
    """Scan and return enriched file metadata"""
    files_data = []
    seen_hashes = {}
    now = time.time()

    for root, _, files in os.walk(folder):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                size_kb       = os.path.getsize(file_path) / 1024
                last_modified = os.path.getmtime(file_path)
                days_old      = (now - last_modified) / 86400
                ext           = Path(file_path).suffix.lower()
                file_hash     = get_file_hash(file_path)

                is_dupe = False
                if file_hash:
                    if file_hash in seen_hashes:
                        is_dupe = True
                    else:
                        seen_hashes[file_hash] = file_path

                files_data.append({
                    "path":     file_path,
                    "name":     file,
                    "size_kb":  round(size_kb, 2),
                    "days_old": round(days_old),
                    "ext":      ext,
                    "is_dupe":  is_dupe,
                    "hash":     file_hash,
                })
            except Exception:
                continue

    return files_data


def score_file(f):
    """Score 0–10: higher = more urgent to offload"""
    score = 0
    score += min(f["size_kb"] / 200, 4)       # up to 4 pts — size
    score += min(f["days_old"] / 45, 3)        # up to 3 pts — age
    if f["is_dupe"]:        score += 2         # duplicate penalty
    if f["ext"] in TEMP_EXTENSIONS: score += 1 # temp file bonus
    return round(min(score, 10), 1)


def route_file(f, score):
    """Decide destination based on score, type, sensitivity"""
    if f["is_dupe"]:
        return "dupe"
    if f["ext"] in SENSITIVE_EXTENSIONS:
        return "usb"
    if score >= 7:
        return "perm_cloud"
    if score >= 3:
        return "temp_cloud"
    return "keep"


def select_cloud(cloud_type):
    filtered = [c for c in CLOUDS if c["type"] == cloud_type]
    if not filtered:
        filtered = CLOUDS
    return max(filtered, key=lambda x: x["free_mb"])


DESTINATION_META = {
    "dupe":       {"label": "Duplicate → Delete", "badge": "badge-dupe", "emoji": "🗑"},
    "usb":        {"label": "USB / Local",         "badge": "badge-usb",  "emoji": "💾"},
    "perm_cloud": {"label": "Permanent Cloud",     "badge": "badge-perm", "emoji": "☁️"},
    "temp_cloud": {"label": "Temp Cloud",          "badge": "badge-temp", "emoji": "⏳"},
    "keep":       {"label": "Keep on device",      "badge": "badge-keep", "emoji": "✅"},
}

# ─────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────
st.markdown("""
<div style="padding: 32px 0 8px 0;">
  <div style="font-family:'Syne',sans-serif; font-size:36px; font-weight:800; letter-spacing:-0.5px; color:#e2e2e8;">
    StorageMind
  </div>
  <div style="font-size:12px; color:#6b6b80; letter-spacing:0.1em; margin-top:4px;">
    INTELLIGENT STORAGE OPTIMIZATION ENGINE
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

col_input, col_btn = st.columns([4, 1])
with col_input:
    folder_input = st.text_input(
        "Folder path",
        value="./demo_images",
        label_visibility="collapsed",
        placeholder="Enter folder path to scan..."
    )
with col_btn:
    scan_clicked = st.button("▶  Scan", use_container_width=True)

# ─────────────────────────────────────────────
# SCAN + PROCESS
# ─────────────────────────────────────────────
if scan_clicked and folder_input:
    folder_path = Path(folder_input.strip().replace("\\", "/")).resolve()

    if not folder_path.exists() or not folder_path.is_dir():
        st.error("❌ Folder not found. Check your path.")
        st.stop()

    with st.spinner("Scanning and analyzing..."):
        files_data = scan_storage(folder_path)

    if not files_data:
        st.warning("No files found in this folder.")
        st.stop()

    # Score + route every file
    for f in files_data:
        f["score"]       = score_file(f)
        f["destination"] = route_file(f, f["score"])

    # Aggregate stats
    large_files   = [f for f in files_data if f["size_kb"] > LARGE_FILE_THRESHOLD_KB]
    dupes         = [f for f in files_data if f["is_dupe"]]
    to_offload    = [f for f in files_data if f["destination"] != "keep"]
    total_size_kb = sum(f["size_kb"] for f in files_data)
    saveable_kb   = sum(f["size_kb"] for f in to_offload)

    # ── Summary metrics ──
    st.markdown('<div class="section-header">Summary</div>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.markdown(f"""
        <div class="metric-card">
          <div class="metric-label">Files scanned</div>
          <div class="metric-value">{len(files_data)}</div>
        </div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-card">
          <div class="metric-label">Total size</div>
          <div class="metric-value">{round(total_size_kb/1024, 2) if total_size_kb > 1024 else str(round(total_size_kb, 1))+' KB'}</div>
        </div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="metric-card">
          <div class="metric-label">Reclaimable</div>
          <div class="metric-value" style="color:#4da6ff;">{round(saveable_kb/1024, 2) if saveable_kb > 1024 else str(round(saveable_kb,1))+' KB'}</div>
        </div>""", unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="metric-card">
          <div class="metric-label">Duplicates</div>
          <div class="metric-value" style="color:#ff7a00;">{len(dupes)}</div>
        </div>""", unsafe_allow_html=True)

    # ── Destination breakdown ──
    st.markdown('<div class="section-header">Decision Breakdown</div>', unsafe_allow_html=True)

    dest_counts = {}
    dest_sizes  = {}
    for f in files_data:
        d = f["destination"]
        dest_counts[d] = dest_counts.get(d, 0) + 1
        dest_sizes[d]  = dest_sizes.get(d, 0) + f["size_kb"]

    d1, d2, d3, d4, d5 = st.columns(5)
    cols_map = {"dupe": d1, "usb": d2, "perm_cloud": d3, "temp_cloud": d4, "keep": d5}

    for dest, col in cols_map.items():
        meta  = DESTINATION_META[dest]
        count = dest_counts.get(dest, 0)
        size  = round(dest_sizes.get(dest, 0), 1)
        with col:
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;">
              <div style="font-size:22px; margin-bottom:6px;">{meta['emoji']}</div>
              <div class="metric-label" style="text-align:center;">{meta['label']}</div>
              <div class="metric-value" style="font-size:22px; text-align:center;">{count}</div>
              <div style="font-size:11px; color:#6b6b80; margin-top:4px;">{size} KB</div>
            </div>""", unsafe_allow_html=True)

    # ── File list ──
    st.markdown('<div class="section-header">File Analysis</div>', unsafe_allow_html=True)

    # Filter controls
    fc1, fc2 = st.columns([2, 1])
    with fc1:
        dest_filter = st.multiselect(
            "Filter by destination",
            options=list(DESTINATION_META.keys()),
            default=list(DESTINATION_META.keys()),
            format_func=lambda x: DESTINATION_META[x]["label"],
            label_visibility="collapsed"
        )
    with fc2:
        sort_by = st.selectbox(
            "Sort",
            ["Score (high→low)", "Size (large→small)", "Age (oldest first)"],
            label_visibility="collapsed"
        )

    filtered = [f for f in files_data if f["destination"] in dest_filter]

    if sort_by == "Score (high→low)":
        filtered.sort(key=lambda x: x["score"], reverse=True)
    elif sort_by == "Size (large→small)":
        filtered.sort(key=lambda x: x["size_kb"], reverse=True)
    else:
        filtered.sort(key=lambda x: x["days_old"], reverse=True)

    for f in filtered:
        meta       = DESTINATION_META[f["destination"]]
        score_pct  = int((f["score"] / 10) * 100)
        short_path = f["path"] if len(f["path"]) < 60 else "..." + f["path"][-57:]

        st.markdown(f"""
        <div class="file-row">
          <div style="flex:1; min-width:0;">
            <div style="color:#e2e2e8; font-size:12px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
              {short_path}
            </div>
            <div style="color:#6b6b80; font-size:11px; margin-top:3px;">
              {f['size_kb']} KB &nbsp;·&nbsp; {f['days_old']}d old &nbsp;·&nbsp; {f['ext'] or 'no ext'}
              {'&nbsp;·&nbsp; <span style="color:#ff7a00;">duplicate</span>' if f['is_dupe'] else ''}
            </div>
          </div>
          <div style="display:flex; align-items:center; gap:12px; flex-shrink:0; margin-left:16px;">
            <div style="font-size:11px; color:#6b6b80;">
              score {f['score']}
              <span class="score-bar-wrap">
                <span class="score-bar-fill" style="width:{score_pct}%;"></span>
              </span>
            </div>
            <span class="badge {meta['badge']}">{meta['label']}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Simulated execution ──
    if to_offload:
        st.markdown('<div class="section-header">Execute Optimization</div>', unsafe_allow_html=True)

        best_temp = select_cloud("temp")
        best_perm = select_cloud("perm")

        st.markdown(f"""
        <div style="display:flex; gap:12px; margin-bottom:16px;">
          <div class="metric-card" style="flex:1;">
            <div class="metric-label">Temp cloud target</div>
            <div style="font-family:'Syne',sans-serif; font-size:16px; font-weight:700; margin-top:4px;">
              {best_temp['name']} <span style="font-size:12px; color:#6b6b80;">({best_temp['free_mb']} MB free)</span>
            </div>
          </div>
          <div class="metric-card" style="flex:1;">
            <div class="metric-label">Perm cloud target</div>
            <div style="font-family:'Syne',sans-serif; font-size:16px; font-weight:700; margin-top:4px;">
              {best_perm['name']} <span style="font-size:12px; color:#6b6b80;">({best_perm['free_mb']} MB free)</span>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("⚡  Run Optimization (Simulated)", use_container_width=True):
            results = {"dupe": 0, "usb": 0, "perm_cloud": 0, "temp_cloud": 0}
            total   = len(to_offload)
            prog    = st.progress(0)
            status  = st.empty()

            for i, f in enumerate(to_offload):
                dest = f["destination"]
                meta = DESTINATION_META[dest]
                status.markdown(
                    f'<div style="font-size:12px; color:#6b6b80;">{meta["emoji"]} {f["name"]} → {meta["label"]}</div>',
                    unsafe_allow_html=True
                )
                prog.progress((i + 1) / total)
                time.sleep(0.04)
                results[dest] = results.get(dest, 0) + 1

            status.empty()
            st.success(f"✅ Optimization complete — {round(saveable_kb/1024, 2) if saveable_kb > 1024 else str(round(saveable_kb,1))+' KB'} reclaimed")

            r1, r2, r3, r4 = st.columns(4)
            for col, (dest, count) in zip([r1, r2, r3, r4], results.items()):
                meta = DESTINATION_META[dest]
                with col:
                    st.markdown(f"""
                    <div class="metric-card" style="text-align:center;">
                      <div style="font-size:18px;">{meta['emoji']}</div>
                      <div class="metric-label" style="text-align:center;">{meta['label']}</div>
                      <div class="metric-value" style="font-size:20px; text-align:center;">{count}</div>
                    </div>""", unsafe_allow_html=True)
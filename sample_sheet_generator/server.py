from flask import Flask, request, send_from_directory, jsonify
from pathlib import Path
import csv
import datetime
import re

app = Flask(__name__, static_folder="static", static_url_path="/static")
BASE_DIR = Path(__file__).resolve().parent
MAP_FILE = BASE_DIR / "udp_index_map.csv"

# Load UDP→(Index, Index2) map once
UDP_MAP = {}
with MAP_FILE.open(newline="", encoding="utf-8") as f:
    r = csv.DictReader(f)
    for row in r:
        idx_id = row["Index_ID"].strip().upper()
        UDP_MAP[idx_id] = (row["Index"].strip(), row["Index2"].strip())

SAMPLE_RE = re.compile(r"^[A-Za-z\-_]+$")
UDP_RE = re.compile(r"^UDP0*(\d{1,4})$")

def valid_sample_id(s: str) -> bool:
    return bool(SAMPLE_RE.fullmatch(s))

def parse_udp(u: str) -> int | None:
    m = UDP_RE.fullmatch(u.upper())
    if not m:
        return None
    return int(m.group(1))

@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.post("/save_samplesheet")
def save_samplesheet():
    data = request.get_json(force=True)
    rows = data.get("rows", [])
    # Header fields from the UI (with safe defaults)
    run_name = (data.get("run_name") or "RUNNAME_PLACEHOLDER").strip()

    # Validate rows
    problems = []
    normalized = []
    for i, row in enumerate(rows, start=1):
        sample = (row.get("sample_id") or "").strip()
        udp = (row.get("udp") or "").strip().upper()
        if not sample or not valid_sample_id(sample):
            problems.append(f"Row {i}: invalid Sample_ID '{sample}'")
        n = parse_udp(udp)
        if n is None or not (1 <= n <= 192):
            problems.append(f"Row {i}: UDP must be UDP0001–UDP0192, got '{udp}'")
        udp_norm = f"UDP{n:04d}" if n else udp
        # Check mapping
        if n and f"UDP{n:04d}" not in UDP_MAP:
            problems.append(f"Row {i}: {udp_norm} not found in udp_index_map.csv")
        normalized.append((sample, udp_norm))

    if problems:
        return jsonify({"ok": False, "errors": problems}), 400

    # Build SampleSheet_Analysis.csv content
    # Static values match your example; adjust if needed.
    reads_r1 = "151"
    reads_r2 = "151"
    i1 = "10"
    i2 = "10"

    header = []
    header += ["[Header],,,,"]
    header += ["FileFormatVersion,2,,,",
               f"RunName,{run_name},,,",
               "InstrumentPlatform,NovaSeq,,,",
               "IndexOrientation,Forward,,,",
               ",,,,"]
    header += ["[Reads],,,,"]
    header += [f"Read1Cycles,{reads_r1},,,",
               f"Read2Cycles,{reads_r2},,,",
               f"Index1Cycles,{i1},,,",
               f"Index2Cycles,{i2},,,",
               ",,,,"]
    header += ["[Sequencing_Settings],,,,"]
    header += ["LibraryPrepKits,TSO500ctDNA_v2,,,",
               ",,,,"]
    header += ["[BCLConvert_Settings],,,,"]
    header += ["SoftwareVersion,02.01.2001,,,",
               "AdapterRead1,CTGTCTCTTATACACATCT,,,",
               "AdapterRead2,CTGTCTCTTATACACATCT,,,",
               "MaskShortReads,35,,,",
               "OverrideCycles,U7N1Y143,I10,I10,U7N1Y143",
               "AdapterBehavior,trim,,,",
               "MinimumTrimmedReadLength,35,,,",
               ",,,,"]
    header += ["[BCLConvert_Data],,,,"]
    header += ["Sample_ID,index,index2,,"]

    # BCLConvert_Data rows
    for sample, udp_norm in normalized:
        idx, idx2 = UDP_MAP[udp_norm]
        header.append(f"{sample},{idx},{idx2},,")

    header += [",,,,"]
    header += ["[TSO500L_Settings],,,,"]
    header += ["SoftwareVersion,02.01.2001,,,",
               "StartsFromFastq,0,,,",
               ",,,,"]
    header += ["[TSO500L_Data],,,,"]
    header += ["Sample_ID,Sample_Type,Index_ID,Index,Index2"]

    # TSO500L_Data rows
    for sample, udp_norm in normalized:
        idx, idx2 = UDP_MAP[udp_norm]
        header.append(f"{sample},DNA,{udp_norm},{idx},{idx2}")

    content = "\n".join(header) + "\n"

    # Save file next to server.py as SampleSheet_Analysis_{stamp}.csv
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_name = f"SampleSheet_Analysis_{stamp}.csv"
    out_path = BASE_DIR / out_name
    out_path.write_text(content, encoding="utf-8")

    return jsonify({"ok": True, "saved_to": str(out_path)})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

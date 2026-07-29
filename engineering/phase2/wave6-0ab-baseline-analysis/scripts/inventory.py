#!/usr/bin/env python3
"""Phase A: Approved source file inventory generator. Read-only."""
import csv
import hashlib
import os
import sys
from datetime import datetime, timezone

try:
    from PIL import Image
except ImportError:
    Image = None

ROOT = "/Users/mac/mac_Project/minecraft_points_festivals/temp/screen_renew"
OUT_CSV = sys.argv[1] if len(sys.argv) > 1 else "/tmp/mongle-wave6-0ab/6.0A/approved_source_file_inventory.csv"
MANIFEST_OUT = sys.argv[2] if len(sys.argv) > 2 else None

def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

rows = []
manifest_lines = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames.sort()
    for fn in sorted(filenames):
        full = os.path.join(dirpath, fn)
        rel = os.path.relpath(full, ROOT)
        try:
            size = os.path.getsize(full)
            mtime = datetime.fromtimestamp(os.path.getmtime(full), tz=timezone.utc).isoformat()
            digest = sha256_of(full)
        except OSError as e:
            rows.append({"rel_path": rel, "error": str(e)})
            continue
        ext = os.path.splitext(fn)[1].lower().lstrip(".")
        img_w = img_h = img_mode = img_alpha = ""
        if ext in ("png", "jpg", "jpeg", "webp", "gif", "bmp") and Image is not None:
            try:
                with Image.open(full) as im:
                    img_w, img_h = im.size
                    img_mode = im.mode
                    img_alpha = "yes" if (im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)) else "no"
            except Exception as e:
                img_mode = f"ERROR:{e}"
        rows.append({
            "rel_path": rel,
            "filename": fn,
            "ext": ext,
            "bytes": size,
            "sha256": digest,
            "mtime_utc": mtime,
            "img_width": img_w,
            "img_height": img_h,
            "img_mode": img_mode,
            "img_has_alpha": img_alpha,
        })
        manifest_lines.append(f"{digest}  {rel}")

os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
with open(OUT_CSV, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["rel_path", "filename", "ext", "bytes", "sha256", "mtime_utc", "img_width", "img_height", "img_mode", "img_has_alpha"])
    writer.writeheader()
    for r in rows:
        writer.writerow({k: r.get(k, "") for k in writer.fieldnames})

print(f"Wrote {len(rows)} rows to {OUT_CSV}")

if MANIFEST_OUT:
    with open(MANIFEST_OUT, "w") as f:
        f.write("\n".join(sorted(manifest_lines)) + "\n")
    print(f"Wrote manifest with {len(manifest_lines)} entries to {MANIFEST_OUT}")

#!/usr/bin/env python3
"""Phase A Section 12: PNG vs rendered-HTML visual delta, no new deps (PIL only)."""
import json
from PIL import Image, ImageChops

RENDER_DIR = "/tmp/mongle-wave6-0ab/evidence/approved-html-render"
APPROVED_DIR = "/Users/mac/mac_Project/minecraft_points_festivals/temp/screen_renew/uploads"

# Mapping: screen_id -> (rendered crop filename, approved PNG filename or None)
PAIRS = {
    "1a": ("screen_1a.png", "screen_login_approved.png"),
    "1a-1": ("screen_1a_1.png", None),  # no dedicated approved PNG for pure-login variant
    "1b": ("screen_1b.png", "screen_family_home_approved.png"),
    "1c": ("screen_1c.png", "screen_point_festival_approved.png"),
    "1d": ("screen_1d.png", "screen_family_chat_approved.png"),
    "1e": ("screen_1e.png", "screen_admin_point_approved.png"),
    "1f": ("screen_1f.png", None),
    "1g": ("screen_1g.png", None),
    "1h": ("screen_1h.png", None),
    "1i": ("screen_1i.png", None),
}

results = {}
for sid, (render_fn, approved_fn) in PAIRS.items():
    render_path = f"{RENDER_DIR}/{render_fn}"
    entry = {"rendered_file": render_path}
    if approved_fn is None:
        entry["approved_file"] = None
        entry["comparable"] = False
        entry["classification"] = "NOT_COMPARABLE"
        entry["reason"] = "SOURCE_MISSING: no dedicated approved PNG for this screen id"
        results[sid] = entry
        continue
    approved_path = f"{APPROVED_DIR}/{approved_fn}"
    entry["approved_file"] = approved_path
    try:
        im_r = Image.open(render_path).convert("RGB")
        im_a = Image.open(approved_path).convert("RGB")
    except Exception as e:
        entry["comparable"] = False
        entry["classification"] = "NOT_COMPARABLE"
        entry["reason"] = f"open error: {e}"
        results[sid] = entry
        continue

    entry["rendered_size"] = im_r.size
    entry["approved_size"] = im_a.size

    # Resize rendered to approved size (approved PNGs are device-scale screenshots,
    # rendered crops are CSS px at 1x) for pixel-level comparison. Aspect ratio note recorded.
    ar_r = im_r.size[0] / im_r.size[1]
    ar_a = im_a.size[0] / im_a.size[1]
    entry["aspect_ratio_rendered"] = round(ar_r, 4)
    entry["aspect_ratio_approved"] = round(ar_a, 4)
    entry["aspect_ratio_delta_pct"] = round(abs(ar_r - ar_a) / ar_a * 100, 2)

    im_r_resized = im_r.resize(im_a.size)
    diff = ImageChops.difference(im_r_resized, im_a)
    bbox = diff.getbbox()
    hist = diff.histogram()
    # sum of per-channel intensity as a rough delta magnitude
    total_diff = sum(i * n for i, n in enumerate(hist[0:256])) + \
                 sum(i * n for i, n in enumerate(hist[256:512])) + \
                 sum(i * n for i, n in enumerate(hist[512:768]))
    max_possible = im_a.size[0] * im_a.size[1] * 255 * 3
    pct_diff = round(total_diff / max_possible * 100, 3)
    entry["mean_pixel_diff_pct"] = pct_diff
    entry["diff_bbox"] = bbox
    diff_path = f"{RENDER_DIR}/diff_{sid.replace('-', '_')}.png"
    diff.save(diff_path)
    entry["diff_image"] = diff_path

    if pct_diff < 1.0:
        cls = "EXACT_OR_NEAR_MATCH"
    elif pct_diff < 4.0:
        cls = "MINOR_RENDERING_NOISE"
    else:
        cls = "MATERIAL_VISUAL_DELTA"
    entry["classification"] = cls
    entry["comparable"] = True
    results[sid] = entry

with open(f"{RENDER_DIR}/visual_diff_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)

for sid, e in results.items():
    print(sid, e.get("classification"), e.get("mean_pixel_diff_pct"), e.get("aspect_ratio_delta_pct"))

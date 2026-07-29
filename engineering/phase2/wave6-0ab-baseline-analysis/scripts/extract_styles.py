#!/usr/bin/env python3
"""Phase A Sections 9-11: parse inline style="" attributes from standalone-src.html,
split per approved screen (by id="1a" etc. boundary), and tabulate repeated literal
values for colors / font-size / border-radius / padding / gap / box-shadow.
Pure regex/stdlib only (no bs4), per Hard Stop #8 no-new-deps constraint.
"""
import re
import csv
import json
from collections import defaultdict, Counter

SRC = "/Users/mac/mac_Project/minecraft_points_festivals/temp/screen_renew/standalone-src.html"
OUT_DIR = "/tmp/mongle-wave6-0ab/6.0A"

with open(SRC, encoding="utf-8") as f:
    text = f.read()
lines = text.splitlines()

# Screen boundaries: find `<div id="1a"` etc, screen ends at next same-level id or EOF of section
screen_starts = []
for m in re.finditer(r'<div id="([^"]+)"', text):
    screen_starts.append((m.start(), m.group(1)))
screen_starts.sort()
boundaries = []
for i, (pos, sid) in enumerate(screen_starts):
    end = screen_starts[i + 1][0] if i + 1 < len(screen_starts) else len(text)
    boundaries.append((sid, pos, end))

SCREEN_LABELS = {
    "1a": "A1 로그인/프로필 선택", "1a-1": "A1 순수 로그인(ID/PW)",
    "1b": "A2 가족 홈", "1c": "A3 포인트 잔치",
    "1d": "A4 가족 대화(GROUP)", "1e": "A5 관리자 포인트 관리",
    "1f": "EXTRA-01 나 프로필", "1g": "EXTRA-02 가족 일정",
    "1h": "EXTRA-03 앨범", "1i": "EXTRA-04 할 일",
}

style_attr_re = re.compile(r'style="([^"]*)"')

def parse_style(style_str):
    props = {}
    for decl in style_str.split(";"):
        decl = decl.strip()
        if not decl or ":" not in decl:
            continue
        k, _, v = decl.partition(":")
        props[k.strip()] = v.strip()
    return props

# per-screen and global collectors
per_screen_props = {}
global_colors = Counter()
global_font_sizes = Counter()
global_radii = Counter()
global_paddings = Counter()
global_gaps = Counter()
global_shadows = Counter()
global_widths = Counter()

color_re = re.compile(r'#[0-9A-Fa-f]{3,8}\b')

for sid, start, end in boundaries:
    chunk = text[start:end]
    props_list = []
    for sm in style_attr_re.finditer(chunk):
        props = parse_style(sm.group(1))
        props_list.append(props)
        for k, v in props.items():
            if k == "color" or k == "background" or k == "border" or "background" in k:
                for c in color_re.findall(v):
                    global_colors[c.upper()] += 1
            if k == "font-size":
                global_font_sizes[v] += 1
            if k == "border-radius":
                global_radii[v] += 1
            if k == "padding":
                global_paddings[v] += 1
            if k == "gap":
                global_gaps[v] += 1
            if k == "box-shadow":
                global_shadows[v] += 1
            if k == "width":
                global_widths[v] += 1
    per_screen_props[sid] = props_list

# Write per-screen style dumps (JSON, for traceability / Measurement Table sourcing)
with open(f"{OUT_DIR}/_raw_per_screen_styles.json", "w", encoding="utf-8") as f:
    json.dump({sid: per_screen_props[sid] for sid, _, _ in boundaries}, f, ensure_ascii=False, indent=1)

# Token candidate CSVs
def write_counter_csv(fname, counter, category):
    with open(f"{OUT_DIR}/_raw_{fname}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["category", "raw_value", "occurrence_count"])
        for val, cnt in counter.most_common():
            w.writerow([category, val, cnt])

write_counter_csv("colors", global_colors, "color")
write_counter_csv("font_sizes", global_font_sizes, "font-size")
write_counter_csv("radii", global_radii, "border-radius")
write_counter_csv("paddings", global_paddings, "padding")
write_counter_csv("gaps", global_gaps, "gap")
write_counter_csv("shadows", global_shadows, "box-shadow")
write_counter_csv("widths", global_widths, "width")

print("Colors:", len(global_colors), "distinct")
print("Font sizes:", len(global_font_sizes), "distinct ->", global_font_sizes.most_common(20))
print("Radii:", global_radii.most_common(20))
print("Paddings:", global_paddings.most_common(15))
print("Gaps:", global_gaps.most_common(15))
print("Widths:", global_widths.most_common(15))
print("Shadows:", global_shadows.most_common(10))
print("Top colors:", global_colors.most_common(25))

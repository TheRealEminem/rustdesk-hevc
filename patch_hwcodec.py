#!/usr/bin/env python3
"""Re-enable the hevc_vaapi encoder that upstream hwcodec comments out on Linux.

Usage: patch_hwcodec.py <hwcodec>/src/ffmpeg_ram/encode.rs
Exits non-zero if the expected block can't be found, so CI fails loudly
instead of silently shipping a build without HEVC.
"""
import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
lines = path.read_text().splitlines(keepends=True)

name_re = re.compile(r'name:\s*"hevc_vaapi"')
commented_name_re = re.compile(r'^\s*//\s*name:\s*"hevc_vaapi"')

hits = [i for i, l in enumerate(lines) if name_re.search(l)]
if not hits:
    sys.exit("hevc_vaapi not found in encode.rs; upstream layout changed")
if not any(commented_name_re.match(lines[i]) for i in hits):
    print("hevc_vaapi is already enabled upstream; nothing to patch")
    sys.exit(0)

i = next(i for i in hits if commented_name_re.match(lines[i]))
start = next((j for j in range(i, max(i - 4, -1), -1)
              if re.match(r'^\s*//\s*codecs\.push\(CodecInfo \{', lines[j])), None)
end = next((j for j in range(i, min(i + 8, len(lines)))
            if re.match(r'^\s*//\s*\}\);', lines[j])), None)
if start is None or end is None:
    sys.exit("could not find the commented codecs.push block around hevc_vaapi")

for j in range(start, end + 1):
    lines[j] = re.sub(r'^(\s*)//\s?', r'\1', lines[j], count=1)

path.write_text("".join(lines))
print("Enabled hevc_vaapi:")
print("".join(lines[start:end + 1]), end="")

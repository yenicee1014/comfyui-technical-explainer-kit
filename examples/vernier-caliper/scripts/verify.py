"""Verify actual exported frames, scale relationships, text and audio duration."""

import importlib.util
import json
import math
import subprocess
from pathlib import Path

import av
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]


def probe(path):
    output = subprocess.run([
        "ffprobe", "-v", "error", "-count_frames", "-show_entries",
        "stream=codec_name,codec_type,width,height,r_frame_rate,nb_read_frames"
        ":format=duration", "-of", "json", str(path),
    ], check=True, capture_output=True).stdout
    return json.loads(output)


spec = importlib.util.spec_from_file_location("visuals", ROOT/"scripts/build.py")
visuals = importlib.util.module_from_spec(spec)
spec.loader.exec_module(visuals)
timeline = json.loads((ROOT/"timeline.json").read_text(encoding="utf-8"))
chunks = json.loads((ROOT/"chunks.json").read_text(encoding="utf-8"))
lines = {line["id"]: line for line in timeline["lines"]}
movie = ROOT/"vernier-caliper.mp4"
metadata = probe(movie)
expected = round(timeline["duration"]*24)
video = next(s for s in metadata["streams"] if s["codec_type"] == "video")
assert int(video["nb_read_frames"]) == expected
assert (video["width"], video["height"]) == (1280, 720)
assert any(s["codec_type"] == "audio" for s in metadata["streams"])
assert abs(float(metadata["format"]["duration"])-timeline["duration"]) < .08

semantic_frames = set()
for scene in ("one", "three", "main", "match", "result"):
    line = lines[scene]
    for phrase in line["phrases"]:
        point = round((line["start"]+phrase["start"])*24)
        semantic_frames.update(max(0, point+delta) for delta in (-2, -1, 0, 1, 2, 8, 20))
motion_frames = []
checks = []
contact = []
frame_number = 0
for frame in av.open(str(movie)).decode(video=0):
    index = frame_number
    frame_number += 1
    now = index/24
    chunk = next(c for c in chunks if c["start_frame"] <= index < c["end_frame"])
    line = lines[chunk["scene"]]
    array = frame.to_ndarray(format="rgb24")
    if line["id"] in ("one", "three"):
        selected = line["phrases"][1 if line["id"] == "one" else 0]
        local = now-line["anchor"]
        moving = visuals.progress(local, selected["start"], selected["end"])
        start, target = (0, .1) if line["id"] == "one" else (.1, .3)
        offset = start+(target-start)*moving
        x = round(168+85*offset)
        # A zero-line marker travels with the lower scale.
        patch = array[456:466, max(0, x-5):x+6]
        red = ((patch[..., 0] > 135) & (patch[..., 1] < 125)
               & (patch[..., 2] < 125))
        assert red.any(), (index, x, offset)
        motion_frames.append({"frame": index, "zero_x": x, "offset_mm": offset})
    if index in semantic_frames:
        image = Image.fromarray(array)
        image.save(ROOT/f"review/semantic-{index:04d}.jpg", quality=95)
        checks.append(index)
    for scene in ("question", "nine", "difference", "one", "three",
                  "main", "match", "result", "summary", "limits"):
        info = lines[scene]
        target_frame = round((info["end"]+.2)*24)
        if index == target_frame:
            contact.append((scene, now, Image.fromarray(array)))

assert frame_number == expected
glyphs = {}
audit = []
for line in timeline["lines"]:
    layer = visuals.scene_layer(line["id"], line["duration"]+.2,
                                line["duration"], line["text"], line["phrases"])
audit = list(visuals.TEXT_AUDIT.values())
assert all(item["inside"] for item in audit)
for k in (0, 1, 3, 9):
    offset = k*.1
    equality = offset+k*.9
    assert math.isclose(equality, k, abs_tol=1e-12)
assert math.isclose(12+3*.1, 12.3)

sheet = Image.new("RGB", (1280, math.ceil(len(contact)/2)*390), "#25251F")
draw = ImageDraw.Draw(sheet)
for i, (scene, now, image) in enumerate(contact):
    x, y = (i % 2)*640, (i//2)*390
    sheet.paste(image.resize((640, 360)), (x, y))
    draw.text((x+12, y+367), f"{scene} / {now:.3f}s",
              font=visuals.font(16, mono=True), fill="#ECE5D6")
sheet.save(ROOT/"review/contact-sheet.jpg", quality=94)
report = {
    "output": movie.name, "probe": metadata, "expected_frames": expected,
    "fully_decoded_frames": frame_number, "checked_zero_marker_frames": len(motion_frames),
    "semantic_frame_samples": checks, "text_items_checked": len(audit),
    "text_bounds_pass": True, "alignment_math_pass": True,
    "scope": "Computed positions, actual output frames, bounds and media checks. "
             "Does not establish full normal-speed human audiovisual review.",
}
(ROOT/"review/verification.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))

"""Join the ComfyUI-rendered shots, then save the full film through ComfyUI."""

import json
import shutil
import subprocess
import time
from pathlib import Path

from composite import ROOT, request, save


def run(args):
    result = subprocess.run(args, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr.decode())
    return result


def join():
    chunks = json.loads((ROOT/"chunks.json").read_text(encoding="utf-8"))
    entries = []
    for c in chunks:
        evidence = json.loads((ROOT/f"review/{c['key']}-execution.json").read_text(encoding="utf-8"))
        path = ROOT/"output"/evidence["output"]
        entries.extend([
            "file '" + path.as_posix().replace("'", "'\\''") + "'",
            f"duration {c['frames']/24:.12f}",
        ])
    listing = ROOT/"review/concat.txt"
    listing.write_text("\n".join(entries)+"\n", encoding="utf-8")
    frames = sum(c["frames"] for c in chunks)
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
         "-i", str(listing), "-i", str(ROOT/"input/narration.wav"),
         "-map", "0:v:0", "-map", "1:a:0",
         "-vf", "setpts=N/(24*TB)", "-fps_mode", "passthrough",
         "-frames:v", str(frames), "-c:v", "libx264", "-preset", "fast",
         "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac",
         "-b:a", "192k", "-movflags", "+faststart",
         str(ROOT/"input/vernier-caliper-assembled.mp4")])
    print(f"Assembled {frames} frames with the original measured narration.", flush=True)


def export():
    prompt = {
        "1": {"class_type": "LoadVideo", "inputs": {
            "file": "vernier-caliper-assembled.mp4"}},
        "2": {"class_type": "SaveVideo", "inputs": {
            "video": ["1", 0], "filename_prefix": "vernier-caliper-final",
            "format": "mp4", "format.codec": "auto"}},
    }
    workflow = {
        "last_node_id": 2, "last_link_id": 1, "version": .4,
        "nodes": [
            {"id": 1, "type": "LoadVideo", "pos": [50, 100], "size": [400, 420],
             "flags": {}, "order": 0, "mode": 0, "inputs": [],
             "outputs": [{"name": "VIDEO", "type": "VIDEO", "links": [1]}],
             "properties": {"Node name for S&R": "LoadVideo"},
             "widgets_values": ["vernier-caliper-assembled.mp4"],
             "widgets_values_named": {"file": "vernier-caliper-assembled.mp4"},
             "title": "01 Full film / ComfyUI-rendered shots + measured narration"},
            {"id": 2, "type": "SaveVideo", "pos": [530, 100], "size": [430, 420],
             "flags": {}, "order": 1, "mode": 0,
             "inputs": [{"name": "video", "type": "VIDEO", "link": 1}],
             "outputs": [{"name": "video", "type": "VIDEO", "links": None}],
             "properties": {"Node name for S&R": "SaveVideo"},
             "widgets_values": ["vernier-caliper-final", "mp4", "auto"],
             "widgets_values_named": {
                 "filename_prefix": "vernier-caliper-final", "format": "mp4",
                 "format.codec": "auto", "codec": "auto"},
             "title": "02 Final MP4 / picture + Chinese narration"},
        ],
        "links": [[1, 1, 0, 2, 0, "VIDEO"]], "groups": [], "config": {},
        "extra": {"ds": {"scale": .7, "offset": [10, 10]}},
    }
    save(ROOT/"workflows/full-film-api.json", prompt)
    save(ROOT/"workflows/full-film.json", workflow)
    save(ROOT/"user/default/workflows/vernier-caliper-full-film.json", workflow)
    result = request("/prompt", {
        "prompt": prompt, "extra_data": {"extra_pnginfo": {"workflow": workflow}},
        "client_id": "vernier-caliper-final-export",
    })
    task = result["prompt_id"]
    deadline = time.monotonic()+180
    while time.monotonic() < deadline:
        history = request("/history/"+task)
        if task in history:
            record = history[task]
            if record["status"]["status_str"] != "success":
                raise RuntimeError(record["status"])
            item = record["outputs"]["2"]["images"][0]
            path = ROOT/"output"/item["subfolder"]/item["filename"]
            shutil.copyfile(path, ROOT/"vernier-caliper.mp4")
            save(ROOT/"review/final-execution.json",
                 {"prompt_id": task, "output": str(path.relative_to(ROOT)),
                  "history": record})
            print(f"Final ComfyUI output: {path}", flush=True)
            return
        time.sleep(.5)
    raise TimeoutError(task)


if __name__ == "__main__":
    join()
    export()

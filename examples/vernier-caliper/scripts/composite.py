"""Prepare portable ComfyUI graphs and execute short batches with measured audio."""

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = os.environ.get("COMFYUI_URL", "http://127.0.0.1:8188").rstrip("/")


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def request(route, data=None):
    payload = None if data is None else json.dumps(data).encode()
    req = urllib.request.Request(
        BASE+route, data=payload,
        headers={"Content-Type": "application/json"} if payload else {},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        raise RuntimeError(error.read().decode()) from error


def graph(chunk):
    nodes = {
        "1": {"class_type": "LoadImage", "inputs": {"image": chunk["background"]}},
        "2": {"class_type": "RepeatImageBatch",
              "inputs": {"image": ["1", 0], "amount": chunk["frames"]}},
        "3": {"class_type": "LoadImage", "inputs": {"image": chunk["layer"]}},
        "4": {"class_type": "InvertMask", "inputs": {"mask": ["3", 1]}},
        "5": {"class_type": "ImageCompositeMasked", "inputs": {
            "destination": ["2", 0], "source": ["3", 0], "mask": ["4", 0],
            "x": 0, "y": 0, "resize_source": False}},
        "6": {"class_type": "LoadAudio", "inputs": {"audio": chunk["audio"]}},
        "7": {"class_type": "CreateVideo", "inputs": {
            "images": ["5", 0], "audio": ["6", 0], "fps": 24,
            "bit_depth": "auto", "color_space": "sRGB"}},
        "8": {"class_type": "SaveVideo", "inputs": {
            "video": ["7", 0], "filename_prefix": "vernier/"+chunk["key"],
            "format": "mp4", "format.codec": "h264",
            "format.codec.encoding": "re-encode",
            "format.codec.encoding.crf": 18}},
    }
    return nodes


def canvas(chunk):
    titles = [
        "01 Archive paper / background", "02 Match exact frame count",
        "03 Calculated scale / captions", "04 Transparency to opacity",
        "05 Composite exact layers", "06 Measured phrase narration",
        "07 Frames + narration / 24 fps", "08 Save MP4 / H.264",
    ]
    specs = [
        (1, "LoadImage", [30, 50], [265, 295], [chunk["background"], "image"],
         [], [("IMAGE", "IMAGE"), ("MASK", "MASK")]),
        (2, "RepeatImageBatch", [345, 50], [265, 90], [chunk["frames"]],
         [("image", "IMAGE")], [("IMAGE", "IMAGE")]),
        (3, "LoadImage", [30, 415], [265, 295], [chunk["layer"], "image"],
         [], [("IMAGE", "IMAGE"), ("MASK", "MASK")]),
        (4, "InvertMask", [345, 420], [265, 70], [],
         [("mask", "MASK")], [("MASK", "MASK")]),
        (5, "ImageCompositeMasked", [665, 200], [285, 180], [0, 0, False],
         [("destination", "IMAGE"), ("source", "IMAGE"), ("mask", "MASK")],
         [("IMAGE", "IMAGE")]),
        (6, "LoadAudio", [665, 470], [285, 120], [chunk["audio"]],
         [], [("AUDIO", "AUDIO")]),
        (7, "CreateVideo", [1005, 200], [275, 175], [24, "auto", "sRGB"],
         [("images", "IMAGE"), ("audio", "AUDIO")], [("VIDEO", "VIDEO")]),
        (8, "SaveVideo", [1335, 200], [330, 380],
         ["vernier/"+chunk["key"], "mp4", "h264", "re-encode", 18],
         [("video", "VIDEO")], [("video", "VIDEO")]),
    ]
    links = [
        [1, 1, 0, 2, 0, "IMAGE"], [2, 3, 1, 4, 0, "MASK"],
        [3, 4, 0, 5, 2, "MASK"], [4, 2, 0, 5, 0, "IMAGE"],
        [5, 3, 0, 5, 1, "IMAGE"], [6, 5, 0, 7, 0, "IMAGE"],
        [7, 6, 0, 7, 1, "AUDIO"], [8, 7, 0, 8, 0, "VIDEO"],
    ]
    nodes = []
    named = {
        1: {"image": chunk["background"], "upload": "image"},
        2: {"amount": chunk["frames"]},
        3: {"image": chunk["layer"], "upload": "image"},
        4: {},
        5: {"x": 0, "y": 0, "resize_source": False},
        6: {"audio": chunk["audio"], "upload": ""},
        7: {"fps": 24, "bit_depth": "auto", "color_space": "sRGB"},
        8: {"filename_prefix": "vernier/"+chunk["key"], "format": "mp4",
            "format.codec": "h264", "format.codec.encoding": "re-encode",
            "format.codec.encoding.crf": 18, "codec": "auto"},
    }
    for order, (id_, type_, pos, size, values, inputs, outputs) in enumerate(specs):
        ins = [{"name": n, "type": t, "link": next(
            (l[0] for l in links if l[3] == id_ and l[4] == i), None)}
               for i, (n, t) in enumerate(inputs)]
        outs = [{"name": n, "type": t, "slot_index": i,
                 "links": [l[0] for l in links if l[1] == id_ and l[2] == i] or None}
                for i, (n, t) in enumerate(outputs)]
        nodes.append({
            "id": id_, "type": type_, "pos": pos, "size": size,
            "flags": {}, "order": order, "mode": 0, "inputs": ins,
            "outputs": outs, "properties": {"Node name for S&R": type_},
            "widgets_values": values, "title": titles[order],
            "widgets_values_named": named[id_],
        })
    return {
        "last_node_id": 8, "last_link_id": 8, "version": .4,
        "nodes": nodes, "links": links, "groups": [], "config": {},
        "extra": {"ds": {"scale": .7, "offset": [0, 0]}},
    }


def prepare(chunk):
    prompt = graph(chunk)
    workflow = canvas(chunk)
    save(ROOT/"workflows"/f"{chunk['key']}-api.json", prompt)
    save(ROOT/"workflows"/f"{chunk['key']}.json", workflow)
    return prompt, workflow


def execute(chunk, force=False):
    evidence = ROOT/"review"/f"{chunk['key']}-execution.json"
    if evidence.exists() and not force:
        result = json.loads(evidence.read_text(encoding="utf-8"))
        output = ROOT/"output"/result["output"]
        if output.exists():
            print(f"Already rendered {chunk['key']}", flush=True)
            return
    prompt, workflow = prepare(chunk)
    response = request("/prompt", {
        "prompt": prompt, "extra_data": {"extra_pnginfo": {"workflow": workflow}},
        "client_id": "vernier-caliper-production",
    })
    if response.get("node_errors"):
        raise RuntimeError(response)
    task = response["prompt_id"]
    print(f"Queued {chunk['key']}: {task}", flush=True)
    deadline = time.monotonic() + 600
    while time.monotonic() < deadline:
        history = request("/history/"+task)
        if task in history:
            record = history[task]
            if record["status"]["status_str"] != "success":
                save(evidence, record)
                raise RuntimeError(record["status"])
            previews = record["outputs"]["8"]
            media = previews.get("images") or previews.get("videos")
            if not media:
                raise RuntimeError(previews)
            item = media[0]
            output = str(Path(item["subfolder"])/item["filename"])
            save(evidence, {"prompt_id": task, "output": output,
                            "chunk": chunk, "history": record})
            print(f"Completed {chunk['key']}: {output}", flush=True)
            return
        time.sleep(.8)
    raise TimeoutError(task)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--scene")
    parser.add_argument("--prepare-ui", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    chunks = json.loads((ROOT/"chunks.json").read_text(encoding="utf-8"))
    selected = [c for c in chunks if not args.scene or c["scene"] == args.scene]
    if args.prepare_ui:
        sample = selected[0]
        _, workflow = prepare(sample)
        destination = ROOT/"user/default/workflows/vernier-caliper-sample.json"
        save(destination, workflow)
        print(destination)
    else:
        for chunk in selected:
            execute(chunk, args.force)

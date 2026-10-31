"""Build measured narration and exact raster layers for a ComfyUI explainer."""

import argparse
import json
import math
import platform
import random
import re
import subprocess
import wave
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONT_DIR = ROOT.parents[1] / "assets/fonts"
W, H, FPS = 1280, 720, 24
PAPER = "#ECE5D6"
INK = "#25251F"
RED = "#C6382C"
MUTED = "#646358"
GRID = "#D0CABB"
BLUE = "#4C5A68"

LINES = [
    ("question", "一格一毫米的尺子，为什么能读出零点一毫米？", 0.55),
    ("parts", "游标卡尺的秘密，就在这排会滑动的刻度里。", 0.55),
    ("nine", "以十分度游标为例，把主尺九毫米，分成十个游标格。", 0.75),
    ("difference", "这样，游标每格零点九毫米，比主尺少零点一。", 0.65),
    ("one", "从零线对齐开始，向右移动零点一毫米，第一条线就对齐。", 0.65),
    ("three", "移动零点三毫米，就轮到第三条线。", 0.75),
    ("main", "现在读一次数。游标零线，已经越过主尺十二毫米。", 0.65),
    ("match", "再找对齐线，是第三条。", 0.8),
    ("result", "所以读数是，十二，加三乘零点一，等于十二点三毫米。", 0.95),
    ("summary", "两排刻度的差，把细小距离，变成了看得见的对齐。", 0.8),
    ("limits", "这是零点一毫米的分度值。实际测量，还要检查零位和接触。", 1.25),
]


def run(args, **kwargs):
    return subprocess.run(args, check=True, capture_output=True, **kwargs)


def save_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def duration(path):
    return float(run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1", str(path),
    ]).stdout)


@lru_cache(maxsize=100)
def font(size, bold=False, mono=False):
    filename = "SpaceMono-Regular.ttf" if mono else (
        "NotoSansSC-Bold.otf" if bold else "NotoSansSC-Regular.otf"
    )
    return ImageFont.truetype(str(FONT_DIR / filename), size)


TEXT_AUDIT = {}


def text(draw, xy, content, size=30, fill=INK, bold=False, mono=False, anchor=None):
    face = font(size, bold, mono)
    box = draw.textbbox(xy, content, font=face, anchor=anchor)
    TEXT_AUDIT[(content, size, box)] = {
        "text": content, "size": size, "box": list(box),
        "font": "SpaceMono-Regular.ttf" if mono else (
            "NotoSansSC-Bold.otf" if bold else "NotoSansSC-Regular.otf"),
        "inside": box[0] >= 0 and box[1] >= 0 and box[2] <= W and box[3] <= H,
    }
    draw.text(xy, content, font=face, fill=fill, anchor=anchor)


def ease(value):
    value = max(0.0, min(1.0, value))
    return value * value * (3 - 2 * value)


def progress(t, a, b):
    return ease((t - a) / (b - a))


def dimension(draw, x1, x2, y, label, color=RED, size=27):
    draw.line((x1, y, x2, y), fill=color, width=3)
    for x in (x1, x2):
        draw.line((x, y - 9, x, y + 9), fill=color, width=3)
    text(draw, ((x1 + x2) / 2, y - 14), label, size, color, anchor="mb")


def marker(draw, x, y, color=RED, up=False):
    direction = -1 if up else 1
    draw.polygon([(x, y), (x - 7, y + 12 * direction),
                  (x + 7, y + 12 * direction)], fill=color)


def paper_background(dark=False):
    rng = random.Random(44 if dark else 23)
    base = Image.new("RGB", (W, H), INK if dark else "#D9D3C5")
    draw = ImageDraw.Draw(base)
    for _ in range(18000):
        x, y = rng.randrange(W), rng.randrange(H)
        if dark:
            value = rng.randrange(33, 43)
            draw.point((x, y), fill=(value, value, max(0, value - 5)))
        else:
            value = rng.randrange(209, 224)
            draw.point((x, y), fill=(value, value - 5, value - 15))
    if dark:
        draw.polygon([(92, 103), (1148, 72), (1170, 623), (108, 644)],
                     fill="#161713")
        draw.polygon([(75, 87), (1132, 60), (1153, 606), (92, 629)],
                     fill="#BDB6A7")
        draw.polygon([(99, 75), (1188, 114), (1169, 621), (76, 593)],
                     fill="#817D70")
        draw.rectangle((91, 83, 1182, 610), fill=PAPER)
        draw.polygon([(114, 66), (252, 66), (247, 109), (109, 111)],
                     fill="#C3B58E")
        draw.polygon([(1040, 582), (1157, 589), (1153, 625), (1033, 616)],
                     fill="#B8AA85")
        grid_box = (123, 153, 1149, 565)
    else:
        draw.rectangle((25, 19, 1263, 679), fill="#A8A293")
        draw.rectangle((17, 11, 1255, 671), fill=PAPER)
        grid_box = (40, 160, 1230, 609)
    for x in range(grid_box[0], grid_box[2], 24):
        draw.line((x, grid_box[1], x, grid_box[3]), fill="#DAD4C6")
    for y in range(grid_box[1], grid_box[3], 24):
        draw.line((grid_box[0], y, grid_box[2], y), fill="#DAD4C6")
    for _ in range(9000):
        x, y = rng.randrange(grid_box[0], grid_box[2]), rng.randrange(
            grid_box[1], grid_box[3])
        draw.point((x, y), fill="#E4DDCD")
    return base


def head(draw, number, title, sub=None, dark=False):
    top = 105 if dark else 38
    left = 120 if dark else 58
    draw.rectangle((left, top, left + 35, top + 5), fill=RED)
    text(draw, (left + 48, top - 6), f"FIELD NOTES / {number:02d}",
         17, mono=True)
    text(draw, (left, top + 27), title, 41, bold=True)
    if sub:
        text(draw, (left, top + 87), sub, 23, MUTED)


def footer(draw, content, dark=False):
    if dark:
        draw.rectangle((58, 643, 1221, 700), fill="#1E1F1A")
        color = "#F1EBDD"
        y = 671
    else:
        draw.rectangle((39, 633, 1237, 691), fill=INK)
        color = "#F1EBDD"
        y = 662
    for i, color_bar in enumerate((BLUE, "#7A7F4E", "#D2A85E", RED)):
        draw.rectangle((52 + i * 5, y - 20, 56 + i * 5, y + 21),
                       fill=color_bar)
    size = 29
    while draw.textlength(content, font=font(size)) > 1120:
        size -= 1
    text(draw, (W / 2 + 12, y), content, size, color, anchor="mm")


def screw(draw, x, y, r=8):
    draw.ellipse((x-r, y-r, x+r, y+r), fill="#A9AAA2",
                 outline="#55574F", width=2)
    draw.line((x-r+4, y+2, x+r-4, y-2), fill="#575A53", width=2)


def caliper(draw, opening=110, highlight=False, y=315):
    x0 = 235
    # Outer measuring faces share x0 and x0 + opening.
    draw.rectangle((x0-31, y-55, 1064, y+2), fill="#666B66")
    draw.rectangle((x0-29, y-61, 1061, y-7), fill="#BDC0B7",
                   outline="#4A4F49", width=2)
    draw.line((x0-26, y-58, 1059, y-58), fill="#F2F1E5", width=2)
    for k in range(76):
        x = x0 + k * 10.3
        height = 25 if k % 10 == 0 else 17 if k % 5 == 0 else 10
        draw.line((x, y-12, x, y-12-height), fill="#3F443F", width=1)
        if k % 10 == 0 and k > 0:
            text(draw, (x, y-48), str(k), 13, mono=True, anchor="mm")
    draw.polygon([(x0-31, y-61), (x0, y-61), (x0, y+162),
                  (x0-18, y+145), (x0-31, y+82)], fill="#A8ADA5",
                 outline="#4A4F49", width=2)
    draw.line((x0, y+6, x0, y+158), fill="#F1F0E7", width=3)
    moving = x0 + opening
    draw.rounded_rectangle((moving-4, y-74, moving+211, y+40),
                           radius=3, fill="#D1D1C5", outline="#555C54", width=3)
    draw.rectangle((moving+1, y-51, moving+202, y-9), fill="#B5BAB0",
                   outline="#6B7167", width=1)
    draw.polygon([(moving, y+5), (moving+31, y+5),
                  (moving+31, y+82), (moving+17, y+145),
                  (moving, y+162)], fill="#A9AFA4",
                 outline="#4A4F49", width=2)
    draw.line((moving, y+5, moving, y+159), fill="#F0EFE2", width=3)
    for k in range(11):
        x = moving + k * (.9 * 10.3)
        draw.line((x, y+10, x, y+24), fill=RED if highlight else INK, width=2)
        if k in (0, 5, 10):
            text(draw, (x, y+30), str(k), 12, anchor="mt")
    screw(draw, moving+185, y-30)
    draw.rounded_rectangle((moving+72, y-89, moving+118, y-75),
                           radius=3, fill="#70766B", outline="#444B42", width=2)
    if highlight:
        draw.rectangle((moving-11, y+5, moving+104, y+59),
                       outline=RED, width=3)
        draw.line((moving+104, y+61, moving+195, y+112, moving+262, y+112),
                  fill=RED, width=2)
        text(draw, (moving+199, y+80), "游标尺", 26, RED, bold=True)
    return moving


def scales(draw, offset=0, x0=168, unit=82, y=330, count=11,
           highlight=None, zero=False, base=0):
    width = count * unit + 35
    draw.rectangle((x0-23, y-92, x0+width, y), fill="#D7D8CD",
                   outline="#878B80", width=2)
    draw.line((x0-21, y-89, x0+width-2, y-89), fill="#FAF7E9", width=3)
    for k in range(count+1):
        x = x0 + k * unit
        draw.line((x, y, x, y-40), fill=INK, width=2)
        text(draw, (x, y-67), str(k+base), 22, mono=True, anchor="mm")
    vx = x0 + offset * unit
    draw.rectangle((vx-22, y+16, vx+9*unit+23, y+108),
                   fill="#C9CABB", outline="#8B8D7E", width=2)
    draw.line((vx-19, y+19, vx+9*unit+21, y+19), fill="#FCF7E7", width=2)
    for k in range(11):
        x = vx + k * .9 * unit
        color = RED if k == highlight else INK
        draw.line((x, y+16, x, y+56), fill=color,
                  width=4 if k == highlight else 2)
        text(draw, (x, y+80), str(k), 23, color, mono=True, anchor="mm")
    if zero:
        draw.line((vx, y-51, vx, y+113), fill=RED, width=3)
        marker(draw, vx, y-56)
    if highlight is not None:
        x = vx + highlight * .9 * unit
        draw.rectangle((x-9, y-45, x+9, y+60), outline=RED, width=3)
        draw.line((x, y-45, x, y+60), fill=RED, width=3)
    return vx


def scene_layer(kind, local_time, line_duration, caption, phrases=None):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    p = local_time / max(line_duration, 0.01)
    def phrase_motion(index):
        phrase = phrases[index]
        a = phrase["start"]
        b = phrase["end"]
        return progress(local_time, a, b)

    dark = kind in ("question", "parts", "summary", "limits")
    if kind == "question":
        head(d, 1, "多一排刻度，就能读得更细？", dark=True)
        caliper(d, 118, y=343)
        text(d, (124, 542), "1 mm", 39, bold=True, mono=True)
        text(d, (305, 550), "→", 35, RED)
        text(d, (379, 542), "0.1 mm ?", 39, RED, bold=True, mono=True)
        text(d, (946, 558), "结构示意", 17, MUTED)
    elif kind == "parts":
        head(d, 1, "主尺不动，游标随量爪移动", dark=True)
        opening = 100 + 60 * math.sin(phrase_motion(1) * math.pi)
        moving = caliper(d, opening, True, y=333)
        text(d, (773, 270), "主尺", 27, bold=True)
        d.line((801, 303, 801, 275), fill=INK, width=2)
        dimension(d, 235, moving, 524, "测量间距")
    elif kind == "nine":
        head(d, 2, "让两排刻度，故意不一样长",
             "十分度直接游标 / 主尺每格 1 mm")
        scales(d, unit=86, count=10, y=339)
        dimension(d, 168, 168+9*86, 219, "主尺 9 mm")
        reveal = phrase_motion(2)
        if reveal > 0:
            dimension(d, 168, 168+9*86*reveal,
                      505, "游标 10 格")
        text(d, (1080, 535), "示意放大", 17, MUTED, anchor="rm")
    elif kind == "difference":
        head(d, 2, "每一格，只差 0.1 mm", "同一比例下比较两种格距")
        x0, unit, y1, y2 = 190, 680, 296, 440
        d.rectangle((x0-15, y1-44, x0+unit+25, y1+16), fill="#CFD2C7")
        d.rectangle((x0-15, y2-44, x0+.9*unit+25, y2+16), fill="#C0C4B6")
        for y, length in ((y1, unit), (y2, .9*unit)):
            for x in (x0, x0+length):
                d.line((x, y-48, x, y+20), fill=INK, width=3)
        text(d, (x0, y1-79), "主尺一格  1 mm", 29, bold=True)
        text(d, (x0, y2-79), "游标一格  0.9 mm", 29, bold=True)
        d.line((x0+unit, y1+22, x0+unit, y2+76), fill=RED, width=2)
        d.line((x0+.9*unit, y2+22, x0+.9*unit, y2+76), fill=RED, width=2)
        dimension(d, x0+.9*unit, x0+unit, y2+65, "0.1", size=25)
        text(d, (981, 307), "差值", 22, MUTED)
        text(d, (977, 348), "0.1", 60, RED, bold=True, mono=True)
        text(d, (980, 435), "mm", 27, RED, mono=True)
    elif kind in ("one", "three"):
        target = .1 if kind == "one" else .3
        start = 0 if kind == "one" else .1
        move = phrase_motion(1 if kind == "one" else 0)
        offset = start + (target-start)*move
        index = (0 if kind == "one" else 1) if move < .001 else (
            round(target*10) if move > .999 else None)
        head(d, 3, "移动一点，对齐线就换一条",
             "两排刻度始终按同一比例绘制")
        vx = scales(d, offset, unit=85, y=343, count=11,
                    highlight=index, zero=False)
        text(d, (167, 535), f"游标位移  {offset:.2f} mm", 30, RED,
             bold=True)
        if index is not None:
            text(d, (843, 535), f"第 {index} 条对齐", 31, RED,
                 bold=True)
        marker(d, vx, 467, up=True)
    elif kind in ("main", "match", "result"):
        head(d, 4, "读一次数：从整毫米开始", "假设零位正确 / 示意读数")
        scan = phrase_motion(0) if kind == "match" else 1
        index = min(3, int(scan*4)) if kind == "match" else (
            3 if kind == "result" else None)
        scales(d, .3, x0=150, unit=79, y=328, count=12, base=12,
               highlight=index, zero=kind == "main")
        text(d, (67, 271), "主尺", 21, MUTED)
        text(d, (67, 401), "游标", 21, MUTED)
        if kind == "main":
            d.line((150, 455, 173.7, 455), fill=RED, width=5)
            text(d, (190, 518), "零线在 12 与 13 mm 之间", 31, bold=True)
            text(d, (190, 564), "先读主尺：12 mm", 30, RED)
        elif kind == "match":
            x = 150 + 3*79
            if scan > .999:
                d.line((x, 442, x, 477, 730, 477), fill=RED, width=2)
                text(d, (746, 457), "第 3 条", 34, RED, bold=True)
                text(d, (168, 554), "小数部分：3 × 0.1 = 0.3 mm", 33,
                     bold=True)
        else:
            text(d, (156, 521), "12 + 3 × 0.1 =", 41, bold=True,
                 mono=True)
            if local_time >= phrases[3]["start"]:
                text(d, (705, 511), "12.3", 64, RED, bold=True, mono=True)
                text(d, (924, 540), "mm", 32, RED, mono=True)
                d.line((705, 591, 983, 591), fill=RED, width=3)
    elif kind == "summary":
        head(d, 5, "把“小距离”，变成“对齐”", dark=True)
        scales(d, .3, x0=178, unit=82, y=350, count=11, highlight=3)
        text(d, (174, 540), "1 − 0.9 = 0.1 mm", 33, RED, bold=True,
             mono=True)
        text(d, (905, 539), "差值放大直觉", 24, MUTED)
    elif kind == "limits":
        head(d, 5, "能读多细，不等于保证多准", dark=True)
        caliper(d, 123, True, y=332)
        text(d, (166, 529), "分度值  0.1 mm", 33, RED, bold=True)
        text(d, (718, 523), "检查零位  /  正确接触", 28, bold=True)
        text(d, (925, 574), "十分度示例", 17, MUTED)
    footer(d, caption, dark)
    return layer


def audio():
    voice = ROOT / "voice"
    cursor = 0.5
    lines = []
    for key, content, hold in LINES:
        pcm = bytearray()
        phrases = []
        for n, fragment in enumerate(
                f for f in re.split(r"[，。？！]", content) if f):
            raw = voice / f"{key}-phrase-{n+1}.aiff"
            wav_path = voice / f"{key}-phrase-{n+1}.wav"
            if not raw.exists():
                run(["say", "-v", "Tingting", "-r", "212", "-o", str(raw),
                     fragment + "。"])
            source_duration = duration(raw)
            log = run(["ffmpeg", "-hide_banner", "-i", str(raw), "-af",
                       "silencedetect=noise=-43dB:d=0.06", "-f", "null", "-"]).stderr.decode()
            events = [(m[1], float(m[2])) for m in re.finditer(
                r"silence_(start|end): ([\d.]+)", log)]
            onset = 0.0
            if events and events[0][0] == "start" and events[0][1] < .08:
                onset = next((v for typ, v in events if typ == "end"), 0)
            tail = source_duration
            if events and events[-1][0] == "end" and abs(
                    events[-1][1]-source_duration) < .12:
                tail = next((v for typ, v in reversed(events) if typ == "start"),
                            source_duration)
            trim_start, trim_end = max(0, onset-.035), min(
                source_duration, tail+.08)
            run(["ffmpeg", "-y", "-v", "error", "-i", str(raw), "-af",
                 f"atrim=start={trim_start}:end={trim_end},asetpts=PTS-STARTPTS",
                 "-ar", "48000", "-ac", "1", str(wav_path)])
            with wave.open(str(wav_path), "rb") as f:
                fragment_pcm = f.readframes(f.getnframes())
            begin = len(pcm) / 96000
            actual = len(fragment_pcm) / 96000
            phrases.append({
                "text": fragment, "start": begin + max(0, onset-trim_start),
                "end": begin+actual, "source_duration": source_duration,
                "trim_start": trim_start,
            })
            pcm.extend(fragment_pcm)
            pcm.extend(b"\0" * (round(.10*48000)*2))
        actual = len(pcm) / 96000
        with wave.open(str(voice / f"{key}.wav"), "wb") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(48000)
            f.writeframes(pcm)
        lines.append({
            "id": key, "text": content, "start": cursor,
            "anchor": cursor,
            "end": cursor+actual, "duration": actual, "hold": hold,
            "phrases": phrases,
        })
        cursor += actual + hold
        print(f"Measured {key}: {actual:.3f}s", flush=True)
    total = math.ceil(cursor*FPS)/FPS
    samples = bytearray(round(total*48000)*2)
    for line in lines:
        with wave.open(str(voice/f"{line['id']}.wav"), "rb") as f:
            pcm = f.readframes(f.getnframes())
        pos = round(line["start"]*48000)*2
        samples[pos:pos+len(pcm)] = pcm
    with wave.open(str(ROOT/"input/narration.wav"), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(48000)
        f.writeframes(samples)
    data = {"schema": 2, "fps": FPS, "width": W, "height": H, "duration": total,
            "voice": "macOS Tingting, 212 words/minute setting",
            "alignment": "Measured independent phrase recordings; no word timestamps inferred.",
            "lines": lines}
    save_json(ROOT/"timeline.json", data)
    return data


def build_inputs(timeline, only=None):
    lines = timeline["lines"]
    for dark, name in ((False, "paper"), (True, "desk")):
        paper_background(dark).save(ROOT/f"input/{name}.png")
    chunks = []
    chunk_frames = 60
    for i, line in enumerate(lines):
        scene_start = 0 if i == 0 else line["start"]
        scene_end = lines[i+1]["start"] if i+1 < len(lines) else timeline["duration"]
        first = round(scene_start*FPS)
        last = round(scene_end*FPS)
        boundaries = list(range(first, last, chunk_frames)) + [last]
        for part, (a, b) in enumerate(zip(boundaries, boundaries[1:])):
            key = f"{i+1:02d}-{line['id']}-{part+1:02d}"
            item = {
                "key": key, "scene": line["id"], "start_frame": a,
                "end_frame": b, "frames": b-a, "start": a/FPS,
                "duration": (b-a)/FPS,
                "background": "desk.png" if line["id"] in
                ("question", "parts", "summary", "limits") else "paper.png",
                "layer": f"{key}.webp", "audio": f"{key}.wav",
            }
            chunks.append(item)
            if only and line["id"] != only:
                continue
            frames = []
            for frame in range(a, b):
                now = frame/FPS
                layer = scene_layer(line["id"], now-line["anchor"],
                                    line["duration"], line["text"], line["phrases"])
                # Preserve every held frame when WebP optimizes identical images.
                layer.putpixel((0, 0), (frame % 256, frame // 256, 0, 1))
                frames.append(layer)
            frames[0].save(
                ROOT/"input"/item["layer"], save_all=True,
                append_images=frames[1:], duration=1000/FPS,
                lossless=True, loop=0, minimize_size=False,
            )
            with Image.open(ROOT/"input"/item["layer"]) as check:
                if check.n_frames != b-a:
                    raise ValueError(f"Collapsed animation frames: {key}")
            run(["ffmpeg", "-y", "-v", "error", "-ss", f"{a/FPS:.8f}",
                 "-i", str(ROOT/"input/narration.wav"), "-t", f"{(b-a)/FPS:.8f}",
                 "-ac", "1", "-ar", "48000",
                 str(ROOT/"input"/item["audio"])])
            print(f"Built {key}: {b-a} frames", flush=True)
        if not only or line["id"] == only:
            view_t = line["duration"]*.84
            layer = scene_layer(line["id"], view_t, line["duration"],
                                line["text"], line["phrases"])
            base = paper_background(line["id"] in
                                    ("question", "parts", "summary", "limits"))
            base.paste(layer, (0, 0), layer)
            base.save(ROOT/f"review/{i+1:02d}-{line['id']}.jpg", quality=94)
    save_json(ROOT/"chunks.json", chunks)
    save_json(ROOT/"review/text-audit.json", list(TEXT_AUDIT.values()))
    problems = [v for v in TEXT_AUDIT.values() if not v["inside"]]
    if problems:
        raise ValueError(f"Text outside frame: {problems[:5]}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio-only", action="store_true")
    parser.add_argument("--scene")
    parser.add_argument("--regenerate-audio", action="store_true",
                        help="Regenerate measured narration with macOS Tingting.")
    args = parser.parse_args()
    for folder in ("voice", "input", "review", "workflows"):
        (ROOT/folder).mkdir(parents=True, exist_ok=True)
    timeline_path = ROOT/"timeline.json"
    measured = json.loads(timeline_path.read_text(encoding="utf-8")) if timeline_path.exists() else {}
    if args.regenerate_audio or measured.get("schema") != 2:
        if platform.system() != "Darwin":
            raise SystemExit(
                "Narration generation uses macOS say/Tingting. Keep the bundled "
                "timeline.json and input/narration.wav to rebuild visuals on other systems."
            )
        measured = audio()
    if not args.audio_only:
        build_inputs(measured, args.scene)

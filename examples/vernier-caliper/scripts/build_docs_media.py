"""Build documentation media from the delivered movie and runnable workflow."""

import io
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, PngImagePlugin

ROOT = Path(__file__).resolve().parents[1]
SCENES = ROOT / "review/scenes"
FONT_DIR = ROOT.parents[1] / "assets/fonts"


def video_frame(index):
    result = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(ROOT / "vernier-caliper.mp4"),
         "-vf", f"select=eq(n\\,{index})", "-frames:v", "1",
         "-f", "image2pipe", "-c:v", "png", "-"],
        check=True, capture_output=True,
    )
    return Image.open(io.BytesIO(result.stdout)).convert("RGB")


def build():
    SCENES.mkdir(parents=True, exist_ok=True)
    timeline = json.loads((ROOT / "timeline.json").read_text(encoding="utf-8"))
    records = []
    for number, line in enumerate(timeline["lines"], 1):
        index = round((line["end"] + 0.2) * timeline["fps"])
        filename = f"{number:02d}-{line['id']}.jpg"
        video_frame(index).save(SCENES / filename, quality=94)
        records.append({"file": filename, "frame": index,
                        "seconds": index / timeline["fps"]})
    (SCENES / "frames.json").write_text(
        json.dumps({"source": "../../vernier-caliper.mp4",
                    "fps": timeline["fps"], "frames": records},
                   ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    frame = video_frame(520)
    metadata = PngImagePlugin.PngInfo()
    for key, filename in (("workflow", "05-one-02.json"),
                          ("prompt", "05-one-02-api.json")):
        data = json.loads((ROOT / "workflows" / filename).read_text(encoding="utf-8"))
        metadata.add_text(key, json.dumps(data, ensure_ascii=False))
    frame.save(ROOT / "review/starter-workflow.png", pnginfo=metadata)
    with Image.open(ROOT / "review/starter-workflow.png") as check:
        assert len(json.loads(check.info["workflow"])["nodes"]) == 8
        assert len(json.loads(check.info["prompt"])) == 8

    guide = Image.new("RGB", (1560, 620), "#f4f5f2")
    draw = ImageDraw.Draw(guide)
    regular = ImageFont.truetype(str(FONT_DIR / "NotoSansSC-Regular.otf"), 23)
    bold = ImageFont.truetype(str(FONT_DIR / "NotoSansSC-Bold.otf"), 29)
    draw.text((28, 24), "同一段视频：背景 + 透明动画 + WAV 配音 → 合成结果",
              fill="#25251f", font=bold)
    images = [
        Image.open(ROOT / "input/paper.png").convert("RGB"),
        Image.open(ROOT / "input/05-one-02.webp"),
        frame,
    ]
    images[1].seek(24)
    layers = []
    for i, image in enumerate(images):
        thumb = image.copy().convert("RGBA").resize((480, 270))
        board = Image.new("RGBA", thumb.size, "#ffffff")
        if i == 1:
            checkers = ImageDraw.Draw(board)
            for y in range(0, 270, 15):
                for x in range(0, 480, 15):
                    if (x // 15 + y // 15) % 2:
                        checkers.rectangle((x, y, x + 14, y + 14), fill="#dce1e4")
        board.alpha_composite(thumb)
        layers.append(board.convert("RGB"))
    headings = ["01 纸面背景", "02 透明动画 / 棋盘格表示透明", "03 ComfyUI 合成结果"]
    details = [
        ["paper.png", "LoadImage → RepeatImageBatch", "静态背景复制60帧"],
        ["05-one-02.webp + 05-one-02.wav", "LoadImage + InvertMask / LoadAudio",
         "刻度、动作、字幕和对应配音"],
        ["SaveVideo → MP4", "1280×720 / 24fps / 2.5秒", "游标移动并突出对齐线"],
    ]
    for i, image in enumerate(layers):
        x = 28 + i * 514
        draw.text((x, 90), headings[i], fill="#25251f", font=regular)
        guide.paste(image, (x, 141))
        for row, value in enumerate(details[i]):
            draw.text((x, 432 + row * 39), value, fill="#25251f", font=regular)
    draw.text((28, 578), "输入来自随包文件，结果取自实际成片；这是教程对照图，不是软件界面截图。",
              fill="#666960", font=regular)
    guide.save(ROOT / "review/input-output-guide.jpg", quality=94)

    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-ss", "18.2", "-t", "9.4",
         "-i", str(ROOT / "vernier-caliper.mp4"),
         "-filter_complex",
         "[0:v]fps=12,scale=896:-1:flags=lanczos,split[a][b];"
         "[a]palettegen=stats_mode=diff[p];[b][p]paletteuse=dither=bayer",
         "-an", "-loop", "0", str(ROOT / "review/motion-preview.gif")],
        check=True,
    )
    print(json.dumps({"scene_frames": len(records),
                      "workflow_png_nodes": 8,
                      "motion_preview_bytes":
                          (ROOT / "review/motion-preview.gif").stat().st_size}))


if __name__ == "__main__":
    build()

"""Generate exact input layers for the model-free ComfyUI compatibility check."""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
KIT = ROOT.parent
OUT = ROOT / "input"
WIDTH, HEIGHT = 640, 360
FRAME_COUNT = 48
FPS = 24
PAPER = "#ECE5D6"
INK = "#25251F"
RED = "#D63A2C"
GRID = "#D7D1C5"


def font(name, size):
    return ImageFont.truetype(str(KIT / "assets" / "fonts" / name), size)


def dashed(draw, start, end, fill, width=1):
    x1, y1 = start
    x2, y2 = end
    length = math.hypot(x2 - x1, y2 - y1)
    if length == 0:
        return
    for offset in range(0, math.ceil(length), 10):
        a, b = offset / length, min(offset + 5, length) / length
        draw.line(
            [(x1 + (x2 - x1) * a, y1 + (y2 - y1) * a),
             (x1 + (x2 - x1) * b, y1 + (y2 - y1) * b)],
            fill=fill, width=width,
        )


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    title = font("NotoSansSC-Bold.otf", 24)
    body = font("NotoSansSC-Regular.otf", 16)
    mono = font("SpaceMono-Regular.ttf", 12)
    base = Image.new("RGB", (WIDTH, HEIGHT), PAPER)
    draw = ImageDraw.Draw(base)
    for x in range(40, WIDTH - 30, 20):
        draw.line((x, 100, x, 292), fill=GRID)
    for y in range(110, 292, 20):
        draw.line((40, y, WIDTH - 30, y), fill=GRID)
    draw.rectangle((32, 22, 46, 25), fill=RED)
    draw.text((54, 16), "TECHNICAL ARCHIVE / MATH", font=mono, fill=INK)
    draw.text((32, 43), "圆周运动与垂直投影", font=title, fill=INK)
    draw.text((32, 316), "精确图层合成验证 / 无扩散模型", font=body, fill=INK)
    draw.text((427, 319), "COMFYUI / 24 FPS", font=mono, fill=INK)
    draw.line((32, 304, 608, 304), fill="#AAA498")
    cx, cy, radius, project_x = 194, 200, 82, 419
    draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), outline=INK, width=2)
    draw.line((cx-radius-15, cy, cx+radius+15, cy), fill=INK)
    draw.line((cx, cy-radius-15, cx, cy+radius+15), fill=INK)
    draw.line((project_x, cy-radius-10, project_x, cy+radius+10), fill=INK)
    draw.text((project_x+14, cy-radius-12), "1", font=mono, fill=INK)
    draw.text((project_x+14, cy-7), "0", font=mono, fill=INK)
    draw.text((project_x+14, cy+radius-7), "-1", font=mono, fill=INK)
    draw.text((project_x+35, 161), "y = sin(theta)", font=mono, fill=INK)
    base.save(OUT / "paper.png")

    frames = []
    for index in range(FRAME_COUNT):
        angle = math.radians(30 + 120 * index / (FRAME_COUNT - 1))
        px, py = cx + radius * math.cos(angle), cy - radius * math.sin(angle)
        layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        line = ImageDraw.Draw(layer)
        line.line((cx, cy, px, py), fill=INK, width=2)
        dashed(line, (px, py), (project_x, py), fill=RED, width=2)
        line.line((project_x, cy, project_x, py), fill=RED, width=4)
        for x, y in ((px, py), (project_x, py)):
            line.ellipse((x-5, y-5, x+5, y+5), fill=RED)
        line.text((370, 69), f"theta = {math.degrees(angle):05.1f} deg", font=mono, fill=INK)
        frames.append(layer)
    frames[0].save(
        OUT / "projection.webp",
        save_all=True, append_images=frames[1:], duration=1000 / FPS,
        loop=0, lossless=True, minimize_size=False,
    )
    print(f"Created paper.png and projection.webp: {FRAME_COUNT} exact RGBA frames, {WIDTH}x{HEIGHT}.")


if __name__ == "__main__":
    build()

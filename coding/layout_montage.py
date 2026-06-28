"""Build a per-subject montage of WORKSHEET pages (TG last page excluded) for the
roomy-layout visual gate. One column per topic (its worksheet pages stacked),
topics laid left->right. Usage: python -m coding.layout_montage <batch> <out.png>
"""
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SCR = Path("/private/tmp/claude-501/-Users-anthonnymonterroso/"
           "f4e448ec-7968-4b20-9319-5bc89cf538b4/scratchpad/montage")
SCR.mkdir(parents=True, exist_ok=True)

COLW = 430          # px per topic column
DPI = 90


def font(sz):
    try:
        return ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", sz)
    except Exception:
        return ImageFont.load_default()


def topic_dirs(batch):
    return sorted(p for p in (ROOT / "coding" / batch).iterdir()
                  if p.is_dir() and p.name[0].isdigit())


def combined(d):
    return next(p for p in d.glob("*.pdf")
                if not p.name.endswith("— Worksheet.pdf")
                and not p.name.endswith("— Teacher Guide.pdf"))


def npages(pdf):
    out = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    return next(int(l.split()[-1]) for l in out.splitlines() if l.startswith("Pages"))


def build(batch, out):
    cols = []
    for d in topic_dirs(batch):
        pdf = combined(d)
        n = npages(pdf)
        ws_pages = max(1, n - 1)   # exclude the single TG page at the end
        stem = SCR / f"{batch}_{d.name}"
        subprocess.run(["pdftoppm", "-png", "-r", str(DPI), "-f", "1",
                        "-l", str(ws_pages), str(pdf), str(stem)], check=True)
        imgs = [Image.open(p).convert("RGB") for p in sorted(SCR.glob(f"{batch}_{d.name}-*.png"))]
        imgs = [im.resize((COLW, int(im.height * COLW / im.width))) for im in imgs]
        label_h = 30
        colh = label_h + sum(im.height + 6 for im in imgs)
        col = Image.new("RGB", (COLW, colh), (235, 235, 235))
        dr = ImageDraw.Draw(col)
        dr.rectangle([0, 0, COLW, label_h], fill=(20, 40, 60))
        dr.text((6, 5), f"{d.name}  ({ws_pages}p)", fill=(255, 255, 255), font=font(18))
        y = label_h
        for im in imgs:
            col.paste(im, (0, y)); y += im.height + 6
        cols.append(col)
    H = max(c.height for c in cols)
    W = sum(c.width + 8 for c in cols)
    canvas = Image.new("RGB", (W, H), (150, 150, 150))
    x = 0
    for c in cols:
        canvas.paste(c, (x, 0)); x += c.width + 8
    canvas.save(out)
    print("wrote", out, canvas.size)


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])

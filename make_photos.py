"""Make web-sized copies and thumbnails of new photos.

1. Put full-size photos (JPG, PNG or WebP) in static/images/photos/originals/
2. Run:  python make_photos.py      (needs:  pip install pillow)

Photos that already have copies are skipped.
"""
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).parent / "static" / "images" / "photos"
SIZES = {"web": (1800, 82), "thumb": (720, 78)}   # longest side in px, JPEG quality

for src in sorted((ROOT / "originals").iterdir()):
    if src.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
        continue
    name = src.stem + ".jpg"
    for folder, (size, quality) in SIZES.items():
        out = ROOT / folder / name
        if out.exists():
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
        im.thumbnail((size, size))
        im.save(out, quality=quality, optimize=True, progressive=True)
        print("made", out.relative_to(ROOT))

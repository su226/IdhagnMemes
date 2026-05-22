import random
from datetime import datetime
from io import BytesIO
from pathlib import Path

from meme_generator import add_meme
from meme_generator.meme import MemeArgsModel
from pil_utils import BuildImage

img_dir = Path(__file__).parent / "images"


def cxk(images: list[BuildImage], texts: list[str], args: MemeArgsModel) -> BytesIO:
    return (
        BuildImage.new("RGB", (830, 830), "white")
        .paste(
            images[0].convert("RGBA").resize((130, 130)),
            (382, 59),
            alpha=True,
        )
        .paste(
            images[1].convert("RGBA").resize((130, 130)).rotate(random.uniform(0, 360)),
            (609, 317),
            alpha=True,
        )
        .paste(BuildImage.open(img_dir / "0.png"), alpha=True)
        .save_jpg()
    )


add_meme(
    "cxk",
    cxk,
    min_images=2,
    max_images=2,
    keywords=["蔡徐坤", "cxk", "打篮球", "鸡你太美"],
    date_created=datetime(2022, 11, 11),
    date_modified=datetime(2026, 5, 22),
)

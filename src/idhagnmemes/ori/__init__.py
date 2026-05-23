from datetime import datetime
from io import BytesIO
from pathlib import Path

from meme_generator import add_meme
from meme_generator.meme import MemeArgsModel
from pil_utils import BuildImage

img_dir = Path(__file__).parent / "images"


def ori(images: list[BuildImage], texts: list[str], args: MemeArgsModel) -> BytesIO:
    return (
        BuildImage.open(img_dir / "0.png")
        .paste(
            images[0].convert("RGBA").circle().resize((100, 100)),
            (305, 222),
            alpha=True,
        )
        .save_jpg()
    )


add_meme(
    "ori",
    ori,
    min_images=1,
    max_images=1,
    keywords=["ori", "拥抱光明"],
    date_created=datetime(2022, 2, 14),
    date_modified=datetime(2025, 12, 4),
)

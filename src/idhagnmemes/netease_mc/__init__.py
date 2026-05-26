from datetime import datetime
from io import BytesIO
from pathlib import Path

from meme_generator import add_meme
from meme_generator.meme import MemeArgsModel
from meme_generator.utils import make_jpg_or_gif
from pil_utils import BuildImage

img_dir = Path(__file__).parent / "images"


def netease_mc(
    images: list[BuildImage],
    texts: list[str],
    args: MemeArgsModel,
) -> BytesIO:
    overlay = BuildImage.open(file=img_dir / "0.png")

    def make(images: list[BuildImage]) -> BuildImage:
        return (
            images[0]
            .convert("RGBA")
            .resize((512, 512), keep_ratio=True)
            .paste(overlay, alpha=True)
        )

    return make_jpg_or_gif(images, make)


add_meme(
    "netease_mc",
    netease_mc,
    min_images=1,
    max_images=1,
    keywords=["贺新春"],
    date_created=datetime(2025, 3, 21),
    date_modified=datetime(2026, 5, 25),
)

from datetime import datetime
from io import BytesIO
from pathlib import Path

from meme_generator import add_meme
from meme_generator.meme import MemeArgsModel
from meme_generator.utils import make_jpg_or_gif
from pil_utils import BuildImage

from idhagnmemes.image import flatten

img_dir = Path(__file__).parent / "images"


def patrick(images: list[BuildImage], texts: list[str], args: MemeArgsModel) -> BytesIO:
    base = BuildImage.open(img_dir / "0.png")

    def make(images: list[BuildImage]) -> BuildImage:
        return base.paste(
            BuildImage(
                flatten(
                    images[0].convert("RGBA").resize((280, 280), keep_ratio=True).image
                )
            ).circle_corner(60),
            (403, 319),
            alpha=True,
        )

    return make_jpg_or_gif(images, make)


add_meme(
    "patrick",
    patrick,
    min_images=1,
    max_images=1,
    keywords=["派大星举"],
    date_created=datetime(2026, 6, 7),
    date_modified=datetime(2026, 6, 7),
)

from datetime import datetime
from io import BytesIO
from pathlib import Path

from meme_generator import add_meme
from meme_generator.meme import MemeArgsModel
from meme_generator.utils import make_jpg_or_gif
from PIL import Image, ImageEnhance
from pil_utils import BuildImage

img_dir = Path(__file__).parent / "images"


def flash(images: list[BuildImage], texts: list[str], args: MemeArgsModel) -> BytesIO:
    flash = BuildImage.open(img_dir / "0.png")

    def make(images: list[BuildImage]) -> BuildImage:
        image = (
            images[0]
            .convert("RGBA")
            .resize((8, 6), Image.Resampling.NEAREST, keep_ratio=True)
            .resize((400, 300), Image.Resampling.NEAREST)
        )
        image = BuildImage(ImageEnhance.Brightness(image.image).enhance(0.5))
        return image.paste(flash, (152, 78), alpha=True)

    return make_jpg_or_gif(images, make)


add_meme(
    "flash",
    flash,
    min_images=1,
    max_images=1,
    keywords=["闪照"],
    date_created=datetime(2022, 11, 15),
    date_modified=datetime(2025, 12, 4),
)

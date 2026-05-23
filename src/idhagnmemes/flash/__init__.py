from datetime import datetime
from io import BytesIO
from pathlib import Path

from meme_generator import add_meme
from meme_generator.meme import MemeArgsModel
from PIL import Image, ImageEnhance
from pil_utils import BuildImage

img_dir = Path(__file__).parent / "images"


def flash(images: list[BuildImage], texts: list[str], args: MemeArgsModel) -> BytesIO:
    image = (
        images[0]
        .resize((8, 6), Image.Resampling.NEAREST, True)
        .resize((400, 300), Image.Resampling.NEAREST)
    )
    return (
        BuildImage(ImageEnhance.Brightness(image.image).enhance(0.5))
        .paste(BuildImage.open(img_dir / "0.png"), (152, 78), alpha=True)
        .save_jpg()
    )


add_meme(
    "flash",
    flash,
    min_images=1,
    max_images=1,
    keywords=["闪照"],
    date_created=datetime(2022, 11, 15),
    date_modified=datetime(2025, 12, 4),
)

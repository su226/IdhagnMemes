from datetime import datetime
from io import BytesIO
from pathlib import Path

from meme_generator import add_meme
from meme_generator.exception import TextOverLength
from meme_generator.meme import MemeArgsModel
from PIL import ImageFilter
from pil_utils import BuildImage, Text2Image

img_dir = Path(__file__).parent / "images"


def nokia(images: list[BuildImage], texts: list[str], args: MemeArgsModel) -> BytesIO:
    text_img = (
        Text2Image.from_text(texts[0], 42, font_families=["FZXS14"], fill=(24, 53, 4))
        .wrap(320)
        .to_image()
    )
    if text_img.height > 225:
        raise TextOverLength(texts[0])
    text_img = (
        BuildImage(text_img)
        .resize_canvas((320, 225), direction="northwest")
        .rotate(-15, expand=True)
        .filter(ImageFilter.GaussianBlur(1))
    )
    return (
        BuildImage.open(img_dir / "0.png")
        .paste(text_img, (85, 126), alpha=True)
        .save_jpg()
    )


add_meme(
    "nokia1",
    nokia,
    min_texts=1,
    max_texts=1,
    keywords=["无内鬼"],
    default_texts=["有内鬼\n终止交易"],
    date_created=datetime(2022, 2, 14),
    date_modified=datetime(2026, 5, 27),
)

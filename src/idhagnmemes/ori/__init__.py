from datetime import datetime
from io import BytesIO
from pathlib import Path

from meme_generator import add_meme
from meme_generator.meme import MemeArgsModel
from meme_generator.utils import make_jpg_or_gif
from PIL import Image
from pil_utils import BuildImage

img_dir = Path(__file__).parent / "images"


def flatten(image: BuildImage) -> BuildImage:
    if image.image.has_transparency_data:
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        out = Image.new("RGB", image.size, "white")
        out.paste(image.image, mask=image.image)
        return BuildImage(out)
    if image.mode != "RGB":
        return image.convert("RGB")
    return image


def ori(images: list[BuildImage], texts: list[str], args: MemeArgsModel) -> BytesIO:
    base = BuildImage.open(img_dir / "0.png")

    def make(images: list[BuildImage]) -> BuildImage:
        return base.paste(
            flatten(
                images[0].convert("RGBA").resize((100, 100), keep_ratio=True)
            ).circle(),
            (305, 222),
            alpha=True,
        )

    return make_jpg_or_gif(images, make)


add_meme(
    "ori",
    ori,
    min_images=1,
    max_images=1,
    keywords=["ori", "拥抱光明"],
    date_created=datetime(2022, 2, 14),
    date_modified=datetime(2025, 12, 4),
)

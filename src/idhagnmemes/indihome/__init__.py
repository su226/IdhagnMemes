import random
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import TypeVar, cast

from meme_generator import add_meme
from meme_generator.meme import MemeArgsModel
from PIL import Image
from pil_utils import BuildImage

img_dir = Path(__file__).parent / "images"
AVATAR_BOX = (0, 0, 360, 360)
PRICE_BOX = (225, 66, 305, 146)
SLIDE_FRAMES = 3
SLIDE_DURATION = 150
AVATAR_DURATION = 150
SCALE_FRAMES = 3
SCALE_DURATION = 150
PRICE_FRAMES = 5
PRICE_DURATION = 250

T = TypeVar("T", bound=tuple[float, ...])


def lerp(box1: T, box2: T, r2: float) -> T:
    r1 = 1 - r2
    return cast(T, tuple(int(i * r1 + j * r2) for i, j in zip(box1, box2)))


def paste(im: Image.Image, im2: Image.Image, box: tuple[int, int, int, int]) -> None:
    im2 = im2.resize((box[2] - box[0], box[3] - box[1]), Image.Resampling.LANCZOS)
    im.paste(im2, box, im2)


def make_price_im(bg: Image.Image, fg: Image.Image) -> Image.Image:
    im = bg.copy()
    im.paste(fg, (24 + random.randint(-10, 10), 93 + random.randint(-10, 10)))
    return im


def indihome(
    images: list[BuildImage],
    texts: list[str],
    args: MemeArgsModel,
) -> BytesIO:
    price_bg_im = Image.open(img_dir / "0.png")
    price_fg_im = Image.open(img_dir / "1.png")
    width, height = price_bg_im.size
    assert width == height, "素材无效"
    image = images[0].convert("RGBA").resize((360, 360)).circle().image
    frames = list[Image.Image]()
    durations = list[int]()
    for i in range(SLIDE_FRAMES):
        im = Image.new("RGB", (width, height), (255, 255, 255))
        im.paste(image, lerp((width, 0), (0, 0), i / SLIDE_FRAMES), image)
        frames.append(im)
        durations.append(SLIDE_DURATION // SLIDE_FRAMES)
    avatar_im = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    avatar_im.paste(image, AVATAR_BOX, image)
    frames.append(avatar_im)
    durations.append(AVATAR_DURATION)
    white = Image.new("RGB", (width, height), (255, 255, 255))
    for i in range(SCALE_FRAMES):
        ratio = (i + 1) / (SCALE_FRAMES + 1)
        price_im = make_price_im(price_bg_im, price_fg_im)
        im = Image.blend(white, price_im, ratio)
        paste(im, image, lerp(AVATAR_BOX, PRICE_BOX, ratio))
        frames.append(im)
        durations.append(SCALE_DURATION // SCALE_FRAMES)
    for i in range(PRICE_FRAMES):
        price_im = make_price_im(price_bg_im, price_fg_im)
        paste(price_im, image, PRICE_BOX)
        frames.append(price_im)
        durations.append(PRICE_DURATION // PRICE_FRAMES)
    f = BytesIO()
    # meme-generator 不支持保存每帧时长不同的 GIF
    frames[0].save(
        f,
        "GIF",
        append_images=frames[1:],
        save_all=True,
        loop=0,
        duration=durations,
    )
    return f


add_meme(
    "indihome",
    indihome,
    min_images=1,
    max_images=1,
    keywords=["indihome", "印尼宽带"],
    date_created=datetime(2022, 2, 14),
    date_modified=datetime(2026, 5, 23),
)

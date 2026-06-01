import random
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Literal, Optional

from meme_generator import (
    MemeArgsModel,
    MemeArgsType,
    ParserArg,
    ParserOption,
    add_meme,
)
from meme_generator.exception import TextOverLength
from meme_generator.utils import MemeFeedback, make_jpg_or_gif
from PIL import Image, ImageChops, ImageFilter, ImageOps
from pil_utils import BuildImage, Text2Image
from pil_utils.typing import SkiaFontStyle
from pydantic import Field

from idhagnmemes.color import parse
from idhagnmemes.image import flatten, flatten_grayscale
from idhagnmemes.text import has_wrap

img_dir = Path(__file__).parent / "images"


def get_builtin_images() -> list[Path]:
    try:
        return sorted(
            (
                path
                for path in (img_dir / "builtin_images").iterdir()
                if path.is_file() and path.suffix == ".png"
            ),
            key=lambda path: path.stem,
        )
    except FileNotFoundError:
        return []


builtin_images = get_builtin_images()
BUILTIN_COLORS = [
    (97, 0, 94),
    (112, 112, 109),
    (137, 0, 41),
    (196, 0, 14),
    (109, 0, 29),
    (106, 0, 189),
    (241, 0, 0),
    (0, 113, 177),
    (249, 188, 0),
    (44, 0, 119),
    (186, 0, 154),
    (0, 144, 71),
    (0, 157, 158),
    (34, 46, 133),
    (189, 0, 46),
    (0, 157, 26),
    (117, 165, 0),
]


def open_builtin_image(image_id: Optional[int]) -> BuildImage:
    if not builtin_images:
        raise MemeFeedback("内置图片不可用")
    if image_id is None or image_id == 0:
        return BuildImage.open(random.choice(builtin_images))
    if image_id > len(builtin_images):
        raise MemeFeedback(f"图片无效，内置图片从 0 到 {len(builtin_images)}，0 为随机")
    return BuildImage.open(builtin_images[image_id - 1])


def parse_color(s: str) -> tuple[int, int, int]:
    try:
        color_id = int(s)
        if color_id == 0:
            return random.choice(BUILTIN_COLORS)
        return BUILTIN_COLORS[color_id - 1]
    except (ValueError, IndexError) as e:
        color = parse(s)
        if color is None:
            raise MemeFeedback(
                f"颜色无效，内置颜色从 0 到 {len(BUILTIN_COLORS)}，0 为随机",
            ) from e
        return color


def make_sketch(im: Image.Image, pencil: Image.Image) -> Image.Image:
    """魔改版的 louvre，用于生成素描风格图像"""
    shade = im.point(lambda v: 0 if v > 127 else 255, "L")
    shade = shade.filter(ImageFilter.BoxBlur(1))
    shade = ImageChops.multiply(shade, ImageOps.invert(pencil))

    im1 = im.filter(ImageFilter.BoxBlur(3))
    im = ImageChops.subtract(im, im1, 2, 128)
    im = im.point(lambda v: 0 if v > 124 else 255, "L")
    im = im.filter(ImageFilter.BoxBlur(1))
    return ImageOps.invert(ImageChops.lighter(im, shade))


Position = Literal["左上", "左下", "右上", "右下", "lt", "lb", "rt", "rb"]
Style = Literal["原图", "灰度", "素描", "original", "grayscale", "sketch"]


class Model(MemeArgsModel):
    header: str = Field("", description="页眉")
    subtitle: str = Field("", description="副标题")
    position: Position = Field("rb", description="副标题方位")
    author: str = Field("", description="作者")
    color: str = Field("", description="颜色")
    builtin_image: Optional[int] = Field(
        None,
        description="内置图片",
        ge=0,
        le=len(builtin_images),
    )
    style: Style = Field("sketch", description="外部图片样式")


args_type = MemeArgsType(
    args_model=Model,
    parser_options=[
        ParserOption(
            names=["-h", "--header"],
            args=[ParserArg(name="header", value="str")],
            help_text="页眉",
        ),
        ParserOption(
            names=["-s", "--subtitle"],
            args=[ParserArg(name="subtitle", value="str")],
            help_text="副标题",
        ),
        ParserOption(
            names=["-p", "--position"],
            args=[ParserArg(name="position", value="str")],
            help_text="副标题方位",
        ),
        ParserOption(
            names=["-a", "--author"],
            args=[ParserArg(name="author", value="str")],
            help_text="作者",
        ),
        ParserOption(
            names=["-c", "--color"],
            args=[ParserArg(name="color", value="str")],
            help_text="颜色",
        ),
        ParserOption(
            names=["-b", "--builtin-image"],
            args=[ParserArg(name="builtin_image", value="int")],
            help_text="内置图片",
        ),
        ParserOption(
            names=["--style"],
            args=[ParserArg(name="style", value="str")],
            help_text="外部图片样式",
        ),
    ],
)


def orly(images: list[BuildImage], texts: list[str], args: Model) -> BytesIO:
    title1 = texts[0]
    title2 = texts[1] if len(texts) > 1 else ""
    if (
        has_wrap(title1)
        or has_wrap(title2)
        or has_wrap(args.header)
        or has_wrap(args.subtitle)
        or has_wrap(args.author)
    ):
        raise MemeFeedback("内容不能有换行")
    color = parse_color(args.color) if args.color else random.choice(BUILTIN_COLORS)
    image_id = args.builtin_image
    image = images[0] if images else None
    style = args.style
    if image is not None and image_id is not None:
        raise MemeFeedback("不能同时使用内置图片和外部图片")
    if image is None:
        image = open_builtin_image(image_id)
        style = "original"

    medium = SkiaFontStyle(
        SkiaFontStyle.kMedium_Weight,
        SkiaFontStyle.kNormal_Width,
        SkiaFontStyle.kUpright_Slant,
    )
    heavy = SkiaFontStyle(
        SkiaFontStyle.kBlack_Weight,
        SkiaFontStyle.kNormal_Width,
        SkiaFontStyle.kUpright_Slant,
    )
    base_im = Image.new("RGB", (1000, 1400), (255, 255, 255))
    if args.header:
        header = Text2Image.from_text(args.header, 28, font_style=medium)
        if header.longest_line > 920:
            raise TextOverLength(args.header)
        header_im = header.to_image()
        base_im.paste(header_im, (500 - header_im.width // 2, 19), header_im)
    base_im.paste(color, (40, 0, 960, 19))
    rect_y = 802
    if args.subtitle:
        subtitle = Text2Image.from_text(args.subtitle, 39, font_style=medium)
        if subtitle.longest_line > 920:
            raise MemeFeedback(args.subtitle)
        subtitle_im = subtitle.to_image()
        if args.position in ("左上", "lt"):
            base_im.paste(subtitle_im, (40, 801), subtitle_im)
            rect_y += subtitle_im.height
        elif args.position in ("左下", "lb"):
            base_im.paste(subtitle_im, (40, 1072), subtitle_im)
        elif args.position in ("右上", "rt"):
            base_im.paste(
                subtitle_im,
                (959 - subtitle_im.width, 801),
                subtitle_im,
            )
            rect_y += subtitle_im.height
        else:
            base_im.paste(subtitle_im, (959 - subtitle_im.width, 1072), subtitle_im)
    base_im.paste(color, (40, rect_y, 960, rect_y + 270))
    if title2:
        title1_t2i = Text2Image.from_text(
            title1,
            77,
            font_style="bold",
            fill="white",
            font_families=["Noto Serif SC"],
        )
        if title1_t2i.longest_line > 864:
            raise TextOverLength(title1)
        title1_im = title1_t2i.to_image()
        base_im.paste(
            title1_im,
            (68, rect_y + 144 - title1_im.height),
            title1_im,
        )
        title2_t2i = Text2Image.from_text(
            title2,
            77,
            font_style="bold",
            fill="white",
            font_families=["Noto Serif SC"],
        )
        if title2_t2i.longest_line > 864:
            raise TextOverLength(title2)
        title2_im = title2_t2i.to_image()
        base_im.paste(
            title2_im,
            (68, rect_y + 236 - title2_im.height),
            title2_im,
        )
    else:
        title_t2i = Text2Image.from_text(
            title1,
            118,
            font_style="bold",
            fill="white",
            font_families=["Noto Serif SC"],
        )
        if title_t2i.longest_line > 864:
            raise TextOverLength(title1)
        title_image = title_t2i.to_image()
        base_im.paste(
            title_image,
            (68, rect_y + 247 - title_image.height),
            title_image,
        )
    orly = Text2Image.from_text("O'RLY?", 44, font_style=heavy)
    orly_im = orly.to_image()
    base_im.paste(orly_im, (56, 1356 - orly_im.height), orly_im)
    if args.author:
        author_t2i = Text2Image.from_text(args.author, 33, font_style=medium)
        if author_t2i.longest_line > 880 - orly_im.width:
            raise TextOverLength(args.author)
        author_im = author_t2i.to_image()
        base_im.paste(
            author_im,
            (944 - author_im.width, 1353 - author_im.height),
            author_im,
        )

    pencil: Optional[Image.Image] = None

    def open_pencil(size: tuple[int, int]) -> Image.Image:
        nonlocal pencil
        if pencil is None:
            pencil = Image.open(img_dir / "sketch.png").convert("L")
            pencil = ImageOps.cover(pencil, size)
            left = (pencil.width - size[0]) // 2
            top = (pencil.height - size[1]) // 2
            pencil = pencil.crop((left, top, left + size[0], top + size[1]))
        return pencil

    def make(images: list[BuildImage]) -> BuildImage:
        cover = ImageOps.contain(images[0].image, (920, 707))
        if style in ("原图", "original"):
            cover = flatten(cover)
        elif style in ("灰度", "grayscale"):
            cover = flatten_grayscale(cover)
        else:
            pencil = open_pencil(cover.size)
            cover = make_sketch(flatten_grayscale(cover), pencil)
        im = base_im.copy()
        im.paste(cover, (960 - cover.width, 802 - cover.height))
        return BuildImage(im)

    return make_jpg_or_gif([image], make)


add_meme(
    "orly",
    orly,
    min_texts=1,
    max_texts=2,
    min_images=0,
    max_images=1,
    args_type=args_type,
    keywords=["orly", "动物书"],
    default_texts=["表情包制作", "从入门到入土"],
    date_created=datetime(2022, 7, 28),
    date_modified=datetime(2026, 5, 31),
)

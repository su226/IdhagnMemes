import math
from datetime import datetime
from io import BytesIO
from pathlib import Path

import skia
from meme_generator import add_meme
from meme_generator.meme import MemeArgsModel
from meme_generator.utils import make_png_or_gif
from PIL import Image
from pil_utils import BuildImage, Text2Image

img_dir = Path(__file__).parent / "images"
MARGIN = 32
AVATAR_WIDTH = 98
AVATAR_BORDER_WIDTH = 4
AVATAR_MARGIN_RIGHT = 42
THINKING_MARGIN_BOTTOM = 24
THINKING_MARGIN_RIGHT = 18
CHEVRON_SIZE = 19
CONTENT_BAR_WIDTH = 6
CONTENT_BAR_MARGIN_RIGHT = 29


def paint_text(canvas: skia.Canvas, text2image: Text2Image, x: float, y: float) -> None:
    for para in text2image.paragraphs:
        if para.stroke_paragraph:
            para.stroke_paragraph.paint(canvas, x, y)
        para.paragraph.paint(canvas, x, y)
        y += para.height


def draw_chevron(canvas: skia.Canvas, x: float, y: float) -> None:
    path = skia.Path()
    path.moveTo(x - CHEVRON_SIZE, y + CHEVRON_SIZE / 2)
    path.lineTo(x, y - CHEVRON_SIZE / 2)
    path.lineTo(x + CHEVRON_SIZE, y + CHEVRON_SIZE / 2)
    canvas.drawPath(
        path,
        {
            "Color": 0xFF707070,
            "StrokeWidth": 4.2,
            "Style": skia.Paint.kStroke_Style,
            "AntiAlias": True,
        },
    )


def deepseek(
    images: list[BuildImage],
    texts: list[str],
    args: MemeArgsModel,
) -> BytesIO:
    thinking_text = Text2Image.from_text("思考中…", 44, fill=(188, 188, 188))
    thinking_width = math.ceil(thinking_text.longest_line)
    thinking_height = math.ceil(thinking_text.height)
    content_text = Text2Image.from_text(texts[0], 44, fill=(188, 188, 188))
    content_width = math.ceil(content_text.longest_line)
    content_height = math.ceil(content_text.height)
    width_left = AVATAR_WIDTH + AVATAR_MARGIN_RIGHT
    width_right = max(
        thinking_width + THINKING_MARGIN_RIGHT + CHEVRON_SIZE * 2,
        CONTENT_BAR_WIDTH + CONTENT_BAR_MARGIN_RIGHT + content_width,
    )
    width = MARGIN * 2 + width_left + width_right
    height_right = thinking_height + THINKING_MARGIN_BOTTOM + content_height
    height = MARGIN * 2 + max(AVATAR_WIDTH, height_right)

    surface = skia.Surfaces.MakeRasterN32Premul(width, height)
    with surface as canvas:
        canvas.clear(0xFF0F0F0F)
        canvas.drawCircle(
            MARGIN + AVATAR_WIDTH / 2,
            MARGIN + AVATAR_WIDTH / 2,
            (AVATAR_WIDTH - AVATAR_BORDER_WIDTH) / 2,
            {
                "Color": 0xFF323232,
                "StrokeWidth": AVATAR_BORDER_WIDTH,
                "Style": skia.Paint.kStroke_Style,
                "AntiAlias": True,
            },
        )
        x = MARGIN + AVATAR_WIDTH + AVATAR_MARGIN_RIGHT
        paint_text(canvas, thinking_text, x, MARGIN)
        draw_chevron(
            canvas,
            x + thinking_width + THINKING_MARGIN_RIGHT + CHEVRON_SIZE,
            MARGIN + thinking_height / 2,
        )
        y = MARGIN + thinking_height + THINKING_MARGIN_BOTTOM
        canvas.drawRect(
            (x, y, CONTENT_BAR_WIDTH, content_height),
            {"Color": 0xFF505050},
        )
        paint_text(
            canvas,
            content_text,
            x + CONTENT_BAR_WIDTH + CONTENT_BAR_MARGIN_RIGHT,
            y,
        )
    base = Image.fromarray(
        surface.makeImageSnapshot().convert(
            colorType=skia.kRGBA_8888_ColorType,
            alphaType=skia.kUnpremul_AlphaType,
        ),
        "RGBA",
    )
    avatar_size = AVATAR_WIDTH - AVATAR_BORDER_WIDTH * 2
    avatar_pos = MARGIN + AVATAR_BORDER_WIDTH

    def make(images: list[BuildImage]) -> BuildImage:
        return BuildImage(base.copy()).paste(
            images[0].resize((avatar_size, avatar_size)).circle(),
            (avatar_pos, avatar_pos),
            alpha=True,
        )

    return make_png_or_gif(images, make)


add_meme(
    "deepseek",
    deepseek,
    min_images=1,
    max_images=1,
    min_texts=1,
    max_texts=1,
    keywords=["思考中"],
    default_texts=["我操，用户彻底怒了。"],
    date_created=datetime(2026, 6, 9),
    date_modified=datetime(2026, 6, 9),
)

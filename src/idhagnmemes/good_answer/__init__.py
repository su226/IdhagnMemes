import math
from datetime import datetime
from io import BytesIO
from pathlib import Path

from meme_generator import add_meme
from meme_generator.meme import MemeArgsModel
from pil_utils import BuildImage, Text2Image

img_dir = Path(__file__).parent / "images"
PADDING_X = 45
PADDING_Y = 25
MEDAL_MARGIN_RIGHT = 20
MEDAL_MARGIN_BOTTOM = 40
FONT_SIZE = 60


def good_answer(
    images: list[BuildImage],
    texts: list[str],
    args: MemeArgsModel,
) -> BytesIO:
    medal = BuildImage.open(img_dir / "0.png")
    if len(texts) == 2:
        title, content = texts
    else:
        title = "优质解答"
        content = texts[0]
    title_layout = Text2Image.from_text(title, FONT_SIZE, font_style="bold")
    content_layout = Text2Image.from_text(content, FONT_SIZE)
    width = PADDING_X * 2 + max(
        medal.width + MEDAL_MARGIN_RIGHT + math.ceil(title_layout.longest_line),
        math.ceil(content_layout.longest_line),
    )
    header_height = max(medal.height, math.ceil(title_layout.height))
    height = (
        PADDING_Y * 2
        + header_height
        + MEDAL_MARGIN_BOTTOM
        + math.ceil(content_layout.height)
    )
    return (
        BuildImage.new("RGB", (width, height), "white")
        .paste(medal, (PADDING_X, PADDING_Y + (header_height - medal.height) // 2))
        .paste(
            title_layout.to_image(),
            (
                PADDING_X + medal.width + MEDAL_MARGIN_RIGHT,
                PADDING_Y + round((header_height - title_layout.height) / 2),
            ),
            alpha=True,
        )
        .paste(
            content_layout.to_image(),
            (PADDING_X, PADDING_Y + header_height + MEDAL_MARGIN_BOTTOM),
            alpha=True,
        )
        .save_jpg()
    )


add_meme(
    "good_answer",
    good_answer,
    min_texts=1,
    max_texts=2,
    keywords=["优质解答"],
    default_texts=["优质解答", "我不知道"],
    date_created=datetime(2026, 5, 29),
    date_modified=datetime(2026, 5, 29),
)

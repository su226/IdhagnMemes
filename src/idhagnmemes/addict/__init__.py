from datetime import datetime
from io import BytesIO
from pathlib import Path

from meme_generator import add_meme
from meme_generator.exception import TextOverLength
from meme_generator.meme import MemeArgsModel
from pil_utils import BuildImage
from pil_utils.typing import SkiaFontStyle

img_dir = Path(__file__).parent / "images"


def addict(images: list[BuildImage], texts: list[str], args: MemeArgsModel) -> BytesIO:
    frame = BuildImage.open(img_dir / "0.png")
    try:
        frame = frame.draw_text(
            (398, 648, 688, 720),
            texts[0],
            max_fontsize=50,
            min_fontsize=20,
            font_style=SkiaFontStyle(
                SkiaFontStyle.kMedium_Weight,
                SkiaFontStyle.kNormal_Width,
                SkiaFontStyle.kUpright_Slant,
            ),
            fill="white",
            lines_align="center",
        )
    except ValueError as e:
        raise TextOverLength(texts[0]) from e
    return frame.save_jpg()


add_meme(
    "addict",
    addict,
    min_texts=1,
    max_texts=1,
    keywords=["成瘾前后", "成瘾"],
    default_texts=["表情包制作"],
    date_created=datetime(2022, 7, 28),
    date_modified=datetime(2026, 5, 22),
)

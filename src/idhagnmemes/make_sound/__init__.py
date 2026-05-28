from datetime import datetime
from io import BytesIO
from pathlib import Path

from meme_generator import add_meme
from meme_generator.exception import MemeFeedback, TextOverLength
from meme_generator.meme import MemeArgsModel
from pil_utils import BuildImage

img_dir = Path(__file__).parent / "images"


def make_sound(
    images: list[BuildImage],
    texts: list[str],
    args: MemeArgsModel,
) -> BytesIO:
    base = BuildImage.open(img_dir / "0.png")
    frame = BuildImage.new("RGB", base.size, (236, 240, 217))

    dialogue_image = images[0] if images else None
    dialogue_text = texts[1] if len(texts) > 1 else None
    caption = texts[0]

    if dialogue_image is not None and dialogue_text is not None:
        raise MemeFeedback("不能同时包含文本和图片")
    elif dialogue_image is not None:
        frame = frame.paste(dialogue_image.resize((122, 74), keep_ratio=True), (6, 26))
        frame = frame.paste(base, alpha=True)
    elif dialogue_text is not None:
        frame = frame.paste(base, alpha=True)
        try:
            frame = frame.draw_text(
                (6, 26, 128, 100),
                dialogue_text,
                min_fontsize=20,
                max_fontsize=50,
            )
        except ValueError as e:
            raise TextOverLength(dialogue_text) from e
    else:
        raise MemeFeedback("需要包含文本或图片")

    try:
        frame = frame.draw_text(
            (0, 310, 380, 380),
            caption,
            min_fontsize=20,
            max_fontsize=50,
        )
    except ValueError as e:
        raise TextOverLength(caption) from e

    return frame.save_jpg()


add_meme(
    "make_sound",
    make_sound,
    min_images=0,
    max_images=1,
    min_texts=1,
    max_texts=2,
    keywords=["发出声音"],
    default_texts=["发出猛男的声音", "嘤"],
    date_created=datetime(2026, 5, 28),
    date_modified=datetime(2026, 5, 28),
)

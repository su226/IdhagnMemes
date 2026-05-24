from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any, Literal

import cv2
import numpy as np
from arclet.alconna import store_false
from meme_generator import MemeArgsType, ParserArg, ParserOption, add_meme
from meme_generator.meme import MemeArgsModel
from PIL import Image, ImageChops, ImageFilter
from pil_utils import BuildImage
from pil_utils.gradient import ColorStop, LinearGradient
from pydantic import Field

img_dir = Path(__file__).parent / "images"


def kernel_average(size: int) -> np.ndarray[Any, Any]:
    return np.full((size, size), 1 / size**2)


KERNELS: dict[str, np.ndarray[Any, Any]] = {
    "thin": kernel_average(5),
    "normal": kernel_average(7),
    "semibold": kernel_average(9),
    "bold": kernel_average(11),
    "black": kernel_average(13),
    "emboss": np.array(
        [
            [1, 1, 1],
            [1, 1, -1],
            [-1, -1, -1],
        ]
    ),
}
# 这些选项在原网站不可调
SHADE_LIGHT = 80
LIGHT_CUT = 128


def make_mask(
    im: Image.Image,
    pencil: Image.Image,
    kernel: str = "normal",
    dark_cut: int = 118,  # 对应原网站线迹轻重
    shade_limit: int = 108,  # 对应原网站调子数量
    denoise: bool = True,  # 对应原网站降噪
) -> Image.Image:
    shade = im.point(lambda v: 0 if v > shade_limit else 255, "L")
    shade = shade.filter(ImageFilter.BoxBlur(3))
    shade = ImageChops.multiply(shade, ImageChops.invert(pencil))
    shade = ImageChops.multiply(shade, Image.new("L", shade.size, SHADE_LIGHT))

    if denoise:
        im = im.filter(ImageFilter.Kernel((3, 3), [1] * 9, 9))

    # 因为PIL只支持3x3和5x5的卷积核，NumPy的卷积是一维的，要用OpenCV
    im1 = Image.fromarray(cv2.filter2D(np.array(im), -1, KERNELS[kernel]))
    im = ImageChops.subtract(im, im1, 1, 128)

    scale = (255 - LIGHT_CUT - dark_cut) / 255
    im = ImageChops.subtract(im, Image.new("L", im.size, dark_cut), scale)

    return ImageChops.lighter(ImageChops.invert(im), shade)


def make_gradient(width: int, height: int) -> Image.Image:
    return LinearGradient(
        (0, 0, width, height),
        [
            ColorStop(0.0, (251, 186, 48)),
            ColorStop(0.4, (252, 114, 53)),
            ColorStop(0.6, (252, 53, 78)),
            ColorStop(0.7, (207, 54, 223)),
            ColorStop(0.8, (55, 181, 217)),
            ColorStop(1.0, (62, 182, 218)),
        ],
    ).create_image((width, height))


def grayscale(image: Image.Image) -> Image.Image:
    if image.mode in ("RGBA", "RGBa", "LA", "La"):
        image = image.convert("LA")
        out = Image.new("L", image.size, 255)
        out.paste(image, mask=image)
        return out
    return image.convert("L")


class Model(MemeArgsModel):
    style: Literal["thin", "normal", "semibold", "bold", "black", "emboss"] = Field(
        "normal", description="线条风格"
    )
    edge: int = Field(118, ge=80, le=126, description="边缘强度")
    shade: int = Field(108, ge=20, le=200, description="暗部强度")
    denoise: bool = Field(True, description="降噪")


args_type = MemeArgsType(
    args_model=Model,
    parser_options=[
        ParserOption(
            names=["--style"],
            args=[ParserArg(name="style", value="str")],
            help_text="线条风格",
        ),
        ParserOption(
            names=["--edge"],
            args=[ParserArg(name="edge", value="int")],
            help_text="边缘强度",
        ),
        ParserOption(
            names=["--shade"],
            args=[ParserArg(name="shade", value="int")],
            help_text="暗部强度",
        ),
        ParserOption(
            names=["--no-denoise"],
            dest="denoise",
            default=True,
            action=store_false,
            help_text="禁用降噪",
        ),
    ],
)


def louvre(images: list[BuildImage], texts: list[str], args: Model) -> BytesIO:
    print(args)
    image = grayscale(images[0].image)
    pencil = (
        BuildImage.open(img_dir / "0.jpg")
        .convert("L")
        .resize(image.size, keep_ratio=True)
        .image
    )
    gradient = make_gradient(image.width, image.height)
    mask = make_mask(image, pencil, args.style, args.edge, args.shade, args.denoise)
    frame = Image.new("RGB", image.size, (255, 255, 255))
    frame.paste(gradient, mask=mask)
    return BuildImage(frame).save_jpg()


add_meme(
    "louvre",
    louvre,
    min_images=1,
    max_images=1,
    args_type=args_type,
    keywords=["卢浮宫"],
    date_created=datetime(1, 1, day=1),
    date_modified=datetime(2026, 5, 24),
)

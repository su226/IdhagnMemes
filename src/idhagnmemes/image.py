from PIL import Image


def flatten(image: Image.Image) -> Image.Image:
    if image.has_transparency_data:
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        out = Image.new("RGB", image.size, "white")
        out.paste(image, mask=image)
        return out
    if image.mode != "RGB":
        return image.convert("RGB")
    return image


def flatten_grayscale(image: Image.Image) -> Image.Image:
    if image.has_transparency_data:
        if image.mode != "LA":
            image = image.convert("LA")
        out = Image.new("L", image.size, "white")
        out.paste(image, mask=image)
        return out
    if image.mode != "L":
        return image.convert("L")
    return image

"""
Image processing services for sticker conversion.
All comments must be in English. Follows PEP 8 and Google-style docstrings.
"""

import io

import PIL.Image as Image


def convert_to_sticker_image(img_bytes: bytes, out_path: str) -> str:
    """
    Converts an image to a 512x512 RGBA WEBP sticker format and saves it.
    ...
    """
    img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
    ratio = max(512 / img.width, 512 / img.height)
    new_size = (round(img.width * ratio), round(img.height * ratio))
    img = img.resize(new_size, Image.LANCZOS)
    canvas = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    x = (512 - img.width) // 2
    y = (512 - img.height) // 2
    canvas.paste(img, (x, y), img)
    canvas.save(out_path, "WEBP")
    return out_path

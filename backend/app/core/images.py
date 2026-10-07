import io
import uuid
import warnings

from fastapi import HTTPException
from PIL import Image, ImageOps, UnidentifiedImageError

from . import config

# Allow normal high-resolution phone pictures, reject decompression bombs.
Image.MAX_IMAGE_PIXELS = 40_000_000


def save_image(data: bytes) -> str:
    if not data or len(data) > config.MAX_IMAGE_BYTES:
        raise HTTPException(413, "Bilder dürfen höchstens 20 MB groß sein.")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(data)) as source:
                if source.format not in {"JPEG", "PNG", "WEBP"}:
                    raise HTTPException(400, "Bitte ein JPEG-, PNG- oder WebP-Bild auswählen.")
                source.load()
                image = ImageOps.exif_transpose(source)
                image.thumbnail((config.MAX_IMAGE_EDGE, config.MAX_IMAGE_EDGE), Image.Resampling.LANCZOS)
                if image.mode in {"RGBA", "LA"} or "transparency" in image.info:
                    rgba = image.convert("RGBA")
                    image = Image.new("RGB", rgba.size, "white")
                    image.paste(rgba, mask=rgba.getchannel("A"))
                else:
                    image = image.convert("RGB")
                name = f"{uuid.uuid4().hex}.jpg"
                # Re-encode pixel data; discard EXIF/GPS and embedded metadata.
                image.save(config.UPLOAD_DIR / name, "JPEG", quality=82, optimize=True)
                return name
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise HTTPException(400, "Das Bild ist ungültig oder hat zu viele Pixel.") from exc

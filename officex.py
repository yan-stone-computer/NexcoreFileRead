"""NexcoreFileRead · NexcoreFileRead —— Office 内嵌图片提取模块

docx / pptx / xlsx 均为 zip 结构，直接读取 word/media、ppt/media、xl/media
目录下的图片文件，以 Markdown 图片（base64 data URI）形式内嵌，图片不丢失。
"""
import base64
import io
import mimetypes
import os
import zipfile
from dataclasses import dataclass, field
from typing import List

MEDIA_PREFIXES = ("word/media", "ppt/media", "xl/media")
IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tif", ".tiff")


@dataclass
class OfficeImage:
    name: str
    data: bytes


def extract_office_images(data: bytes) -> List[OfficeImage]:
    """从 Office 文档（zip 结构）提取全部内嵌图片"""
    out: List[OfficeImage] = []
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            for name in z.namelist():
                low = name.lower()
                if not any(low.startswith(p) for p in MEDIA_PREFIXES):
                    continue
                if not low.endswith(IMAGE_EXTS):
                    continue
                try:
                    out.append(OfficeImage(os.path.basename(name), z.read(name)))
                except Exception:
                    continue
    except zipfile.BadZipFile:
        return out
    return out


def embed_image(img: OfficeImage, max_bytes: int = 3 * 1024 * 1024) -> str:
    """内嵌为 base64 data URI；超大图压缩缩略图"""
    from PIL import Image as PILImage

    mime = mimetypes.guess_type(img.name)[0] or "image/png"
    data = img.data
    try:
        pil = PILImage.open(io.BytesIO(data))
        pil.load()
    except Exception:
        b64 = base64.b64encode(data).decode("ascii")
        return f"![{img.name}](data:{mime};base64,{b64})"

    if len(data) > max_bytes or max(pil.size) > 1600:
        pil.thumbnail((1600, 1600), PILImage.LANCZOS)
        buf = io.BytesIO()
        if pil.mode in ("RGBA", "LA", "P"):
            pil.convert("RGBA").save(buf, "PNG")
            mime = "image/png"
        else:
            pil.convert("RGB").save(buf, "JPEG", quality=82)
            mime = "image/jpeg"
        data = buf.getvalue()

    b64 = base64.b64encode(data).decode("ascii")
    return f"![{img.name}](data:{mime};base64,{b64})"


def append_images_section(markdown: str, data: bytes) -> str:
    """将 Office 文档内嵌图片以 '## 文档图片' 章节追加到 Markdown 末尾"""
    imgs = extract_office_images(data)
    if not imgs:
        return markdown
    section = "\n\n## 文档图片\n\n" + "\n\n".join(embed_image(i) for i in imgs)
    return (markdown + section).strip()

"""NexcoreFileRead · NexcoreFileRead —— OCR 识别模块（RapidOCR + PyMuPDF）

- ocr_image_bytes: 直接识别图片中的文字
- ocr_pdf_bytes: 将扫描 PDF 逐页渲染为图片后识别
模型延迟加载，首次调用时初始化（约 1-3 秒）。
"""
import io
import threading
from typing import List, Optional

import numpy as np
from PIL import Image

_lock = threading.Lock()
_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        with _lock:
            if _engine is None:
                from rapidocr_onnxruntime import RapidOCR

                _engine = RapidOCR()
    return _engine


def _ocr_ndarray(img: np.ndarray) -> str:
    result, _ = _get_engine()(img)
    lines: List[str] = []
    for item in result or []:
        text = item[1] if isinstance(item, (list, tuple)) and len(item) > 1 else str(item)
        if text:
            lines.append(text)
    return "\n".join(lines)


def ocr_image_bytes(data: bytes) -> str:
    """识别图片（png/jpg/bmp/webp 等）中的文字"""
    img = Image.open(io.BytesIO(data)).convert("RGB")
    return _ocr_ndarray(np.array(img))


def ocr_pdf_bytes(data: bytes, dpi: int = 200) -> str:
    """扫描 PDF：逐页渲染为图片后 OCR"""
    import pymupdf as fitz  # PyMuPDF

    doc = fitz.open(stream=data, filetype="pdf")
    parts: List[str] = []
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=dpi)
        img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
        text = _ocr_ndarray(np.array(img)).strip()
        parts.append(f"## 第 {i + 1} 页\n\n{text}" if text else f"## 第 {i + 1} 页\n\n（本页未识别到文字）")
    return "\n\n".join(parts)

"""NexcoreFileRead · NexcoreFileRead —— PDF 增强转换引擎（PyMuPDF 实现）

相比 markitdown 默认的 pdfminer 转换，本引擎：
1. 文本提取保留公式原貌（Unicode 数学符号完整，不再被拆成表格碎片）
2. 提取 PDF 内嵌图片，以 Markdown 图片（base64 data URI）内嵌，图片不丢失
3. 提取 PDF 超链接，转为 Markdown 链接
4. 文本不足时判定为扫描件，自动回调 OCR 识别
"""
import base64
from dataclasses import dataclass, field
from typing import Callable, List, Optional

import pymupdf as fitz

MIN_TEXT_CHARS = 50  # 低于该值视为扫描件/图片型 PDF


@dataclass
class PdfImage:
    name: str
    data: bytes
    mime: str = "image/png"


@dataclass
class PdfResult:
    markdown: str
    images: List[PdfImage] = field(default_factory=list)
    is_scanned: bool = False


def _embed(img: PdfImage) -> str:
    b64 = base64.b64encode(img.data).decode("ascii")
    return f"![{img.name}](data:{img.mime};base64,{b64})"


def _text_inside(page, rect) -> str:
    """收集链接矩形覆盖范围内的文本（近似）"""
    words = page.get_text("words")  # x0,y0,x1,y1,word,block,line,word_no
    parts = []
    for w in words:
        x0, y0, x1, y1 = w[0], w[1], w[2], w[3]
        if x0 >= rect.x0 - 1 and x1 <= rect.x1 + 1 and y0 >= rect.y0 - 1 and y1 <= rect.y1 + 1:
            parts.append(w[4])
    return "".join(parts)


def convert_pdf(data: bytes, ocr_func: Optional[Callable[[bytes], str]] = None) -> PdfResult:
    """将 PDF 转为 Markdown（公式/图片/链接完整保留）。

    ocr_func: 扫描件兜底用，接收 pdf bytes 返回识别文本。
    """
    doc = fitz.open(stream=data, filetype="pdf")
    parts: List[str] = []
    images: List[PdfImage] = []
    links_out: List[str] = []
    total_text = 0
    img_no = 0

    for pno, page in enumerate(doc):
        parts.append(f"## 第 {pno + 1} 页")

        # 1) 文本（保留公式原貌）
        text = page.get_text("text").strip()
        total_text += len(text)
        if text:
            parts.append(text)

        # 2) 内嵌图片
        for img in page.get_images(full=True):
            xref = img[0]
            try:
                pix = fitz.Pixmap(doc, xref)
                if pix.n - pix.alpha >= 4:  # CMYK/多通道转 RGB
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                png = pix.tobytes("png")
            except Exception:
                continue
            img_no += 1
            im = PdfImage(f"page{pno + 1}_img{img_no}.png", png)
            images.append(im)
            parts.append(_embed(im))

        # 3) 超链接
        for link in page.get_links():
            uri = link.get("uri")
            if not uri:
                continue
            label = _text_inside(page, fitz.Rect(link["from"])) or uri
            links_out.append(f"- [{label}]({uri})")

    # 扫描件判定：几乎无文本 -> 走 OCR
    if total_text < MIN_TEXT_CHARS and ocr_func is not None:
        ocr_text = (ocr_func(data) or "").strip()
        if ocr_text:
            parts = [f"## 第 {i + 1} 页\n\n{seg}" for i, seg in enumerate(ocr_text.split("\n\n"))]
            return PdfResult(markdown="\n\n".join(parts), images=images, is_scanned=True)

    if links_out:
        parts.append("## 文档链接\n" + "\n".join(links_out))

    return PdfResult(markdown="\n\n".join(parts), images=images, is_scanned=total_text < MIN_TEXT_CHARS)

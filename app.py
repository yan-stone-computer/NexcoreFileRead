# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for license information.
# ---------------------------------------------------------------------------
# 本文件基于微软开源项目 MarkItDown (https://github.com/microsoft/markitdown) 深度二次开发，
# 直接调用了 MarkItDown 的转换 API（MarkItDown / StreamInfo），故保留上方原版版权声明。
# 以下内容由天枢序列团队（TianShu Series）独立实现：
#   - 自研 PyMuPDF PDF 增强解析引擎（公式/图片/链接，见 pdfx.py）
#   - 自研 RapidOCR 离线识别集成（见 ocr.py）
#   - 自研 Office 内嵌图片提取（见 officex.py）
#   - 自研 Web 服务编排与前端（index.html）
# ---------------------------------------------------------------------------
"""TianShu2Markdown · 天枢文档 —— 全能文档转 Markdown 本地服务

天枢（Dubhe）为北斗七星之首，寓意"指引、开端"。
本服务将 PDF / Office / 图片 / 网页 / 数据文件等转换为结构完整的 Markdown，
所有转换均在本机完成，文件不会离开用户设备。

启动: uvicorn app:app --host 127.0.0.1 --port 8765
"""
import asyncio
import base64
import io
import mimetypes
import os
import sys
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from PIL import Image

from markitdown import MarkItDown
from markitdown._stream_info import StreamInfo

from ocr import ocr_image_bytes, ocr_pdf_bytes
from officex import append_images_section
from pdfx import convert_pdf

# ---- 常量定义 ----
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".gif", ".tif", ".tiff"}  # 图片类型
OFFICE_EXTS = {".docx", ".doc", ".pptx", ".ppt", ".xlsx", ".xls", ".odt", ".odp", ".ods"}  # Office 文档
EMBED_MAX_BYTES = 3 * 1024 * 1024  # 内嵌图片体积上限，超过则压缩缩略图


def resource_path(rel: str) -> Path:
    """定位资源文件：兼容源码运行与 PyInstaller 打包运行（onefile 解压到 _MEIPASS）"""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / rel


app = FastAPI(title="TianShu2Markdown / 天枢文档", version="3.0.0")

# 核心转换引擎（markitdown），负责 Office / 网页 / 数据文件等格式
engine = MarkItDown()


def _inline_image(raw: bytes, filename: str) -> str:
    """将图片以 base64 data URI 内嵌进 Markdown；超大图自动压缩缩略图"""
    try:
        img = Image.open(io.BytesIO(raw))
        img.load()
    except Exception:
        # 无法解析时原样内嵌
        b64 = base64.b64encode(raw).decode("ascii")
        mime = mimetypes.guess_type(filename)[0] or "image/png"
        return f"![{filename}](data:{mime};base64,{b64})"

    # 压缩策略：超过体积上限或超过 1600px 边长时生成缩略图
    if len(raw) > EMBED_MAX_BYTES or max(img.size) > 1600:
        img.thumbnail((1600, 1600), Image.LANCZOS)
        buf = io.BytesIO()
        if img.mode in ("RGBA", "LA", "P"):
            img.convert("RGBA").save(buf, "PNG")
            mime = "image/png"
        else:
            img.convert("RGB").save(buf, "JPEG", quality=82)
            mime = "image/jpeg"
        raw = buf.getvalue()
    else:
        mime = mimetypes.guess_type(filename)[0] or "image/png"

    b64 = base64.b64encode(raw).decode("ascii")
    return f"![{filename}](data:{mime};base64,{b64})"


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    """返回前端页面"""
    return (resource_path("index.html")).read_text(encoding="utf-8")


@app.post("/api/convert")
async def convert_document(file: UploadFile = File(...)) -> JSONResponse:
    """统一转换入口：按文件类型分派到对应引擎"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="未选择文件")

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="文件内容为空")

    ext = os.path.splitext(file.filename)[1].lower() or None
    loop = asyncio.get_running_loop()

    # ---- PDF：PyMuPDF 增强引擎（公式/图片/链接完整保留，扫描件自动 OCR）----
    if ext == ".pdf":
        try:
            # convert_pdf 内部：文本 < 50 字符判定为扫描件并回调 ocr_pdf_bytes
            pdf_res = await loop.run_in_executor(None, convert_pdf, raw, ocr_pdf_bytes)
            md_text = pdf_res.markdown or ""
            ocr_fallback = pdf_res.is_scanned
        except Exception:  # 增强引擎异常时回退 markitdown
            try:
                result = engine.convert_stream(
                    io.BytesIO(raw),
                    stream_info=StreamInfo(filename=file.filename, extension=ext),
                )
                md_text = result.text_content or ""
                ocr_fallback = False
            except Exception as exc:
                raise HTTPException(status_code=500, detail=f"转换失败: {exc}") from exc

    # ---- 独立图片：OCR 识别文字 + 内嵌原图 ----
    elif ext in IMAGE_EXTS:
        embed = _inline_image(raw, file.filename)
        try:
            # OCR 在独立线程执行，避免阻塞事件循环
            ocr_text = (await loop.run_in_executor(None, ocr_image_bytes, raw)).strip()
        except Exception:
            ocr_text = ""
        md_text = (ocr_text + "\n\n" + embed).strip() if ocr_text else embed
        ocr_fallback = bool(ocr_text)

    # ---- 其他格式（Office / HTML / 数据文件）：markitdown + 提取内嵌图片 ----
    else:
        try:
            result = engine.convert_stream(
                io.BytesIO(raw),
                stream_info=StreamInfo(filename=file.filename, extension=ext),
            )
            md_text = result.text_content or ""
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"转换失败: {exc}") from exc
        ocr_fallback = False

        # Office 文档（zip 结构）提取内嵌图片，图片不丢失
        if ext in OFFICE_EXTS:
            md_text = append_images_section(md_text, raw)

    return JSONResponse(
        {
            "filename": file.filename,
            "markdown": md_text,
            "ocr": ocr_fallback,
            "ocr_note": "此文件通过 OCR 识别，可能存在个别识别误差。" if ocr_fallback else None,
        }
    )

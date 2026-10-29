# NexcoreFileRead

> NexcoreWork 的本地文档读取层：把 PDF、Office、图片、HTML 与数据文件转换成结构化
> Markdown，保留公式、图片和链接；扫描件在本机 OCR。文件不上传云端。

这个仓库由原来的 TianShu2Markdown 演进而来。它保留原项目历史和 MIT 许可，重点不再是
一个独立转换网页，而是成为 NexcoreWork 智能体可调用的文件读取基础设施。

## 组合方案

NexcoreWork 采用两条路径，并按可用性组合：

```text
Word / Excel / PowerPoint / HTML / CSV / JSON
  └─ 浏览器零依赖解析：ZIP + XML + DOMParser

PDF / 扫描件 / 公式 / 内嵌图片 / 复杂 Office
  └─ NexcoreFileRead 本地服务
       ├─ PyMuPDF：文本、版面、图片、链接
       ├─ RapidOCR：扫描 PDF 与图片离线识别
       ├─ MarkItDown：Office / HTML / 数据格式分派
       └─ Office ZIP：内嵌图片提取

智能体只接收有长度上限的 Markdown 文本，原文件留在本机。
```

前端零依赖路径保证基础功能在服务未启动时仍可用；NexcoreFileRead 提供更高保真度的
PDF、公式、图片和 OCR 路径。服务不可达时，NexcoreWork 会明确回退并继续处理，不会让
一份无法解析的扫描件静默变成空文本。

## 快速启动

要求 Python 3.10+。

```bash
git clone https://github.com/yan-stone-computer/NexcoreFileRead.git
cd NexcoreFileRead
python -m pip install -r requirements.txt
python launcher.py
```

默认只监听 `127.0.0.1:8765`。

## HTTP API

### 健康检查

```http
GET /api/health
```

### 转换文件

```http
POST /api/convert
Content-Type: multipart/form-data

file=<document>
```

响应：

```json
{
  "filename": "report.pdf",
  "markdown": "## 第 1 页\n\n...",
  "ocr": false,
  "engine": "pymupdf"
}
```

字段说明：

- `markdown`：交给下游智能体的结构化文本；
- `ocr`：是否走过扫描件或图片 OCR；
- `engine`：本次使用的解析路径；
- `warnings`：可选，说明降级、跳过或无法保真的内容。

## NexcoreWork 集成

NexcoreWork 的本地服务把前端 multipart 文件转发到：

```text
NEXCORE_FILE_READ_URL=http://127.0.0.1:8765
```

只接受回环地址。返回的 Markdown 会像普通上传文档一样进入本机文件表，随后由上下文预算
决定注入量；原始文件不会进入模型上下文。

## 支持的格式

| 格式 | 文本 | 图片 | 链接 | 扫描件 OCR |
|---|---:|---:|---:|---:|
| PDF | 是 | 是 | 是 | 是 |
| DOCX / PPTX / XLSX | 是 | 是 | 视格式 | 图片可单独识别 |
| 图片 | OCR 文本 | 原图内嵌 | 不适用 | 是 |
| HTML | 是 | 视输入 | 是 | 不适用 |
| CSV / JSON / TXT | 是 | 不适用 | 保留原文 | 不适用 |

## 设计边界

- 本服务不是数据库，不保存长期状态；每次请求独立处理。
- 文档内容视为不可信数据，不执行其中的脚本、宏或嵌入对象。
- 公式保留依赖 PDF 文本层；纯图片公式只能走 OCR，可能损失上下标精度。
- Office 内嵌图片会按体积和长边压缩后以 data URI 内嵌。
- 加密 PDF、受密码保护的 Office 文件不会绕过保护。
- OCR 可能出错，响应会明确标记，不把识别结果说成原文。

## 与 NexcoreWork 中其他模块的关系

- 上下文治理：[nexcore-context-governor](https://github.com/yan-stone-computer/nexcore-context-governor)
- 视觉证据：[NexcoreVision](https://github.com/yan-stone-computer/NexcoreVision)
- 完整本地工作台：[NexcoreWork 产品站](https://github.com/yan-stone-computer/nexcorework-site)

## 来源、许可与上游

- 仓库自身：MIT，见 [LICENSE](LICENSE)。
- 上游基础：Microsoft MarkItDown（MIT），只复用其转换 API 与少量通用工具。
- PDF 增强：PyMuPDF。
- 离线 OCR：RapidOCR + ONNX Runtime。
- Office 图片提取与 NexcoreWork 集成代码由团队实现。

原 TianShu2Markdown README 中关于 MarkItDown 二次开发的归属说明继续适用。仓库更名为
NexcoreFileRead 不改变第三方资源原有许可与版权。

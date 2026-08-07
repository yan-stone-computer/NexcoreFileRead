<div align="center">

# ⚡ TianShu2Markdown · 天枢文档

### 把任何文件，变成干净的 Markdown —— 本地、私密、即刻完成

**公式不碎 · 图片不丢 · 链接不丢 · 扫描件也能读**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-orange)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![Build](https://img.shields.io/badge/build-single%20exe-orange)
![OCRed](https://img.shields.io/badge/OCR-Offline%20%7C%20zh%2Ben-green)

**⭐ 喜欢就点个 Star！⭐**

</div>

---

## 📜 开源溯源声明

本工具基于微软开源项目 **MarkItDown** 深度二次开发

- 原仓库地址：https://github.com/microsoft/markitdown
- 开源协议：MIT（完整 LICENSE 见仓库根目录，已原样保留）

### 重构范围说明
1. 全量重写底层 PDF 文件解析协议（PyMuPDF 引擎：公式 / 图片 / 链接完整保留）；
2. 重构整体架构：新增离线 OCR（RapidOCR 中英文识别）、Office 内嵌图片提取、Web 服务编排；
3. 新增 base64 图片内嵌、扫描件自动 OCR、格式识别等全套自研功能；
4. 仅复用 MarkItDown 核心转换 API 与少量通用工具函数，核心转换逻辑由天枢序列团队独立重构。


---

## 🚀 天枢一转，万物成文

大多数转换工具，都在**悄悄毁掉你的文档**：

| 能力 | 其他转换工具 | **TianShu2Markdown** |
|---|---|---|
| 🧮 公式 | ❌ 被拆成表格碎片，下标全乱 | ✅ **完整保留** `ln(Sit) = α0 + β1 ln(Pit)` |
| 🖼️ 图片 | ❌ 静默丢失 | ✅ 自动提取，base64 内嵌 |
| 🔗 链接 | ❌ 被丢弃 | ✅ 转为标准 Markdown 链接 |
| 📄 扫描版 PDF | ❌ 一片空白 | ✅ **离线 OCR**（中英文） |
| 🖼️ 照片 / 截图 | ❌ 什么都读不出 | ✅ OCR 文字 + 内嵌原图 |
| 🧾 Word / PPT / Excel | ⚠️ 仅文字 | ✅ 文字 + 内嵌图片 |
| 🔒 隐私 | ⚠️ 文件上传云端 | ✅ **纯本地转换，文件不出本机** |

### 真实效果对比（同一份公式文档）

**修复前** —— 传统引擎：公式碎成表格，`∑` 符号丢失，下标孤立成行。

**修复后 —— TianShu2Markdown**：公式完整可读。

```markdown
## 第 1 页
ln(Sit) = α0 + β1 ln(Pit) + γ1 · Weekday + δ1 · Trend + ε

## 第 2 页
max ∑ i [Pit · Dit(Pit) −Cit · Qit −λiIit]
2 ≤ ∑ i yi ≤3,  yi ∈{0, 1}
Qit ≥2.5 kg,  Ii,0,  Pit ≥1
```

---

## ✨ 为什么是 TianShu2Markdown？

- 🧮 **公式完整** —— 自研 PyMuPDF 引擎，Unicode 数学符号原样保留，告别"公式变表格碎片"
- 🖼️ **图片不丢** —— PDF 页内图片、Word / PPT / Excel 内嵌图片全部自动提取并内嵌
- 🔗 **链接保留** —— 文档超链接转成 `[文字](网址)`
- 📄 **扫描件 OCR** —— 内置中英文识别模型，**完全离线**，隐私安全
- 🚀 **单文件 exe** —— 双击即用，无需安装 Python，绿色便携
- 🔒 **纯本地** —— 没有服务器，没有上传，机密文档不离开你的电脑

---

## 🗂️ 支持的格式

| 格式 | 文字 | 图片 | 链接 | OCR |
|---|---:|---:|---:|---:|
| PDF（文本型） | ✅ | ✅ | ✅ | — |
| PDF（扫描件） | ✅ | ✅ | — | ✅ |
| Word `.docx` | ✅ | ✅ | — | — |
| PowerPoint `.pptx` | ✅ | ✅ | — | — |
| Excel `.xlsx` | ✅ | ✅ | — | — |
| 图片（png / jpg / …） | — | ✅ | — | ✅ |
| HTML | ✅ | — | ✅ | — |
| CSV / JSON / XML / TXT | ✅ | — | — | — |
| EPUB / ZIP | ✅ | — | — | — |
| 音频（元数据） | ✅ | — | — | — |

---

## 🚀 快速开始

### 方式一：桌面版（零门槛）

Windows：双击 **`TianShu2Markdown.exe`** → 浏览器自动打开 → 拖入文件 → 完成。

> 单文件约 158 MB，内置 OCR 引擎与模型，离线可用，绿色免安装。

### 方式二：源码运行

```bash
git clone https://github.com/yan-stone-computer/tianshu2markdown
cd tianshu2markdown
pip install -r requirements.txt

uvicorn app:app --host 127.0.0.1 --port 8765
# 浏览器打开 http://127.0.0.1:8765
```

### 试用样例

仓库自带 `samples/` 目录，含公式 PDF、带图 DOCX / PPTX / XLSX、HTML、图片等 8 种样例文件，开箱即测。

---

## 🧱 技术架构

```
┌────────────┐    ┌──────────────────────────────────────────┐
│  你的文件    │ →  │  TianShu2Markdown 引擎                          │
│  PDF/DOCX  │    │  • PyMuPDF    → 公式 / 图片 / 链接完整保留   │
│  PPTX/XLSX │    │  • markitdown → 文字与表格                  │
│  图片       │    │  • RapidOCR   → 扫描件 / 照片文字（中英文）  │
│  HTML/CSV  │    │  • Office zip → 提取内嵌图片                │
└────────────┘    └───────────────────┬──────────────────────┘
                                      ↓
                              干净的 Markdown
                    （图片以 base64 data URI 内嵌）
```

- **公式**：PyMuPDF 提取，Unicode 数学符号原样保留
- **图片**：PDF 页内 + Office media 目录提取，base64 内嵌（超大图自动压缩）
- **链接**：PDF 超链接转 Markdown 链接
- **OCR**：RapidOCR + PyMuPDF 渲染，中英文模型内置，离线可用

---

## 🗺️ Roadmap

- [ ] LaTeX 公式识别（Pix2Text 接入）
- [ ] 批量 / 文件夹转换
- [ ] 导出 `.zip`（Markdown + 图片资源）
- [ ] 暗色主题 & 多语言
- [ ] macOS / Linux 版本

---

## 🤝 参与贡献

Issues、功能建议、PR 全部欢迎！也欢迎到 `samples/` 补充更多测试文件。

**如果这个工具帮到了你，请点个 ⭐ Star 支持一下～**

---

## 📄 开源协议

[MIT](./LICENSE) —— 个人与商业使用均免费。

---

<div align="center"><sub>用 ❤️ 打造 · 天枢序列 · TianShu Series</sub></div>

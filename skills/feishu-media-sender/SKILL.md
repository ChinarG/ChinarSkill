---
name: feishu-media-sender
description: Send images, files, and videos to Feishu/Lark via API. Auto-detects file type and uses appropriate upload method. Supports PNG/JPG/GIF images, PDF/DOC/XLS/PPT documents, and MP4 videos.
---

# Feishu Media Sender

飞书媒体发送技能 - 支持图片、文件、视频等多种媒体类型。

## 功能

- **图片发送**: PNG, JPG, JPEG, GIF, BMP, WEBP
- **文件发送**: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, 其他格式
- **视频发送**: MP4, MOV, AVI, MKV, FLV
- **自动类型检测**: 根据文件扩展名自动判断媒体类型

## 使用方法

### 命令行

```bash
# 发送图片（自动检测）
python3 scripts/send-media.py --file photo.png --to ou_xxx

# 发送 PDF 文件
python3 scripts/send-media.py --file document.pdf --to ou_xxx

# 发送视频
python3 scripts/send-media.py --file video.mp4 --to ou_xxx

# 手动指定类型
python3 scripts/send-media.py --file data.bin --to ou_xxx --type file
```

### Python API

```python
from scripts.send-media import send_media_to_feishu

# 自动检测类型
result = send_media_to_feishu(
    file_path="/path/to/file.png",
    receive_id="ou_xxx"
)

# 手动指定类型
result = send_media_to_feishu(
    file_path="/path/to/video.mp4",
    receive_id="ou_xxx",
    media_type="video"  # image | video | file | auto
)
```

## 配置

### 环境变量

| 变量名 | 说明 |
|--------|------|
| `FEISHU_APP_ID` | 飞书应用 ID |
| `FEISHU_APP_SECRET` | 飞书应用密钥 |

### 命令行参数

| 参数 | 说明 |
|------|------|
| `--file, -f` | 文件路径 (必需) |
| `--to, -t` | 接收者 open_id (必需) |
| `--type` | 媒体类型: image/video/file/auto (默认: auto) |
| `--app-id` | 飞书 App ID (可选) |
| `--app-secret` | 飞书 App Secret (可选) |

## 文件类型映射

| 扩展名 | 媒体类型 | 飞书类型 | 消息类型 |
|--------|----------|----------|----------|
| .png, .jpg, .jpeg, .gif, .bmp, .webp | image | - | image |
| .mp4, .mov, .avi, .mkv, .flv | video | mp4 | media |
| .pdf | file | pdf | file |
| .doc, .docx | file | doc | file |
| .xls, .xlsx | file | xls | file |
| .ppt, .pptx | file | ppt | file |
| 其他 | file | stream | file |

## API 说明

### 图片上传
- URL: `POST /open-apis/im/v1/images`
- 消息类型: `image`

### 文件上传
- URL: `POST /open-apis/im/v1/files`
- 视频消息类型: `media`
- 文件消息类型: `file`

## 依赖

```
requests>=2.28.0
```

## 安装

```bash
pip install -r requirements.txt
```

## 与 feishu-video-sender 的区别

| Skill | 功能 | 适用场景 |
|-------|------|----------|
| feishu-video-sender | 仅视频 | 专门发送视频 |
| feishu-media-sender | 图片/文件/视频 | 通用媒体发送 |

## 安全说明

- 不在代码中硬编码密钥
- 使用环境变量或命令行参数
- 公开仓库前检查无敏感信息

## License

MIT

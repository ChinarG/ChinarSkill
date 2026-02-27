---
name: feishu-video-sender
description: Send video files to Feishu/Lark via API. Use when you need to upload and send video files to Feishu users. Supports MP4 format, uses environment variables or command-line arguments for credentials.
---

# Feishu Video Sender

飞书视频发送技能 - 通过飞书 API 上传并发送视频文件。

## 功能

- 上传视频到飞书 IM 云盘
- 发送视频消息到指定用户
- 支持命令行参数或环境变量配置

## 使用方法

### 命令行

```bash
# 使用环境变量配置凭证
export FEISHU_APP_ID="cli_xxx"
export FEISHU_APP_SECRET="xxx"
python3 scripts/send-video.py --file video.mp4 --to ou_xxx

# 使用命令行参数
python3 scripts/send-video.py --file video.mp4 --to ou_xxx --app-id cli_xxx --app-secret xxx
```

### Python API

```python
from scripts.send-video import send_video_to_feishu

result = send_video_to_feishu(
    file_path="/path/to/video.mp4",
    receive_id="ou_xxx",
    app_id="cli_xxx",      # 可选，默认从环境变量读取
    app_secret="xxx"       # 可选，默认从环境变量读取
)

print(result["message_id"])
print(result["chat_id"])
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
| `--file, -f` | 视频文件路径 (必需) |
| `--to, -t` | 接收者 open_id (必需) |
| `--app-id` | 飞书 App ID (可选) |
| `--app-secret` | 飞书 App Secret (可选) |

## 依赖

```
requests>=2.28.0
```

## 安装

```bash
pip install -r requirements.txt
```

## API 说明

### 上传接口
- URL: `POST https://open.feishu.cn/open-apis/im/v1/files`
- 文件类型: `mp4`

### 发送接口
- URL: `POST https://open.feishu.cn/open-apis/im/v1/messages`
- 消息类型: `media` (视频用 media，不是 file)

## 安全说明

- **不要**在代码中硬编码密钥
- 使用环境变量或命令行参数传入凭证
- 公开仓库前确保没有提交敏感信息

## License

MIT

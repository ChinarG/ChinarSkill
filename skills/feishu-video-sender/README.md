# Feishu Video Sender Skill

飞书视频发送技能 - 用于通过飞书 API 发送视频文件。

## 功能

- 上传视频到飞书云盘
- 发送视频消息到指定用户

## 使用方法

```typescript
import { sendVideoToFeishu } from "./src/send-video.js";

const result = await sendVideoToFeishu({
  filePath: "/path/to/video.mp4",
  receiveId: "ou_xxx",  // 用户 open_id
  appId: "cli_xxx",
  appSecret: "xxx"
});
```

## 依赖

- Python 3.8+
- requests

## 安装

```bash
cd skills/feishu-video-sender
pip install -r requirements.txt
```

## 配置

在 `config.json` 中配置飞书应用凭证：

```json
{
  "appId": "your_app_id",
  "appSecret": "your_app_secret"
}
```

## 参考

- 飞书 API: https://open.feishu.cn/
- 上传接口: POST /open-apis/im/v1/files
- 消息类型: media

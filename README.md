# ChinarSkill

个人 OpenClaw Skills 仓库

## Skills

### feishu-video-sender
通过飞书 API 发送视频文件。

**功能:**
- 上传视频到飞书 IM
- 发送视频消息到指定用户
- 支持环境变量和命令行参数

**使用:**
```bash
cd skills/feishu-video-sender
export FEISHU_APP_ID="your_app_id"
export FEISHU_APP_SECRET="your_app_secret"
python3 scripts/send-video.py --file video.mp4 --to ou_xxx
```

详见 [skills/feishu-video-sender/SKILL.md](skills/feishu-video-sender/SKILL.md)

## 安全提示

所有技能都**不包含**硬编码的密钥或敏感信息。凭证通过以下方式传入：
- 环境变量
- 命令行参数
- 配置文件（用户自行创建，不提交到仓库）

## 安装 Skill

```bash
# 克隆仓库
git clone <your-repo-url>

# 安装依赖
cd skills/<skill-name>
pip install -r requirements.txt
```

## License

MIT

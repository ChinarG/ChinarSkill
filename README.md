# ChinarSkill

个人技能仓库 - 用于存放自定义 OpenClaw Skills

## 结构

```
ChinarSkill/
├── skills/                 # 技能目录
│   └── feishu-video-sender/  # 飞书视频发送技能
├── LICENSE
└── README.md
```

## Skills

### feishu-video-sender
飞书视频发送工具，用于通过 API 发送视频文件到飞书。

## 使用

```bash
# 克隆仓库
git clone <repository-url>

# 安装技能
cd skills/feishu-video-sender
pip install -r requirements.txt

# 使用
python3 src/send-video.py --file video.mp4 --to ou_xxx
```

## 开发规范

1. 每个技能放在 `skills/` 目录下的独立文件夹
2. 必须包含 `README.md` 和 `skill.json`
3. Python 技能需要 `requirements.txt`
4. 代码需要注释和类型提示

## 提交记录

- 2026-02-27: 创建仓库，添加 feishu-video-sender 技能

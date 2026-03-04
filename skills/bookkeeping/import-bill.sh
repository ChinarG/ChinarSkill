#!/bin/bash
# 飞书账单管家 - 快速入口

cd /root/openclaw/kimi/downloads
source venv/bin/activate

python3 /root/.openclaw/workspace/skills/bookkeeping/bookkeeping.py "$@"

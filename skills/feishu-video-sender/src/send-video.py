#!/usr/bin/env python3
"""
Feishu Video Sender
飞书视频发送工具

Usage:
    python3 send-video.py --file /path/to/video.mp4 --to ou_xxx
    python3 send-video.py --file /path/to/video.mp4 --to ou_xxx --app-id cli_xxx --app-secret xxx
"""

import requests
import json
import os
import argparse
from typing import Optional


def get_tenant_token(app_id: str, app_secret: str) -> str:
    """获取飞书 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json"}
    data = {"app_id": app_id, "app_secret": app_secret}
    resp = requests.post(url, headers=headers, json=data)
    result = resp.json()
    
    if result.get("code") != 0:
        raise Exception(f"Failed to get token: {result.get('msg')}")
    
    return result["tenant_access_token"]


def upload_video_to_im(token: str, file_path: str) -> str:
    """
    上传视频到飞书 IM
    
    Args:
        token: tenant_access_token
        file_path: 视频文件路径
        
    Returns:
        file_key: 飞书文件标识
    """
    url = "https://open.feishu.cn/open-apis/im/v1/files"
    headers = {"Authorization": f"Bearer {token}"}
    
    file_name = os.path.basename(file_path)
    
    with open(file_path, 'rb') as f:
        files = {
            'file': (file_name, f, 'video/mp4')
        }
        data = {
            'file_type': 'mp4',
            'file_name': file_name
        }
        resp = requests.post(url, headers=headers, data=data, files=files)
    
    result = resp.json()
    
    if result.get("code") != 0:
        raise Exception(f"Upload failed: {result.get('msg')}")
    
    return result["data"]["file_key"]


def send_media_message(token: str, file_key: str, receive_id: str) -> dict:
    """
    发送媒体消息
    
    Args:
        token: tenant_access_token
        file_key: 文件标识
        receive_id: 接收者 open_id
        
    Returns:
        发送结果
    """
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    params = {"receive_id_type": "open_id"}
    
    content = {"file_key": file_key}
    
    data = {
        "receive_id": receive_id,
        "msg_type": "media",  # 视频用 media 类型
        "content": json.dumps(content)
    }
    
    resp = requests.post(url, headers=headers, params=params, json=data)
    result = resp.json()
    
    if result.get("code") != 0:
        raise Exception(f"Send failed: {result.get('msg')}")
    
    return result["data"]


def send_video_to_feishu(
    file_path: str,
    receive_id: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> dict:
    """
    发送视频到飞书
    
    Args:
        file_path: 视频文件路径
        receive_id: 接收者 open_id
        app_id: 飞书 App ID (可选，默认从环境变量读取)
        app_secret: 飞书 App Secret (可选，默认从环境变量读取)
        
    Returns:
        发送结果，包含 message_id 和 chat_id
    """
    # 从参数或环境变量读取凭证
    app_id = app_id or os.environ.get("FEISHU_APP_ID")
    app_secret = app_secret or os.environ.get("FEISHU_APP_SECRET")
    
    if not app_id or not app_secret:
        raise ValueError("App ID and App Secret are required")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # 1. 获取 token
    token = get_tenant_token(app_id, app_secret)
    
    # 2. 上传视频
    file_key = upload_video_to_im(token, file_path)
    
    # 3. 发送消息
    result = send_media_message(token, file_key, receive_id)
    
    return {
        "message_id": result.get("message_id"),
        "chat_id": result.get("chat_id"),
        "file_key": file_key
    }


def main():
    parser = argparse.ArgumentParser(description="Send video to Feishu")
    parser.add_argument("--file", "-f", required=True, help="Video file path")
    parser.add_argument("--to", "-t", required=True, help="Receiver open_id")
    parser.add_argument("--app-id", help="Feishu App ID")
    parser.add_argument("--app-secret", help="Feishu App Secret")
    
    args = parser.parse_args()
    
    try:
        result = send_video_to_feishu(
            file_path=args.file,
            receive_id=args.to,
            app_id=args.app_id,
            app_secret=args.app_secret
        )
        print(f"✅ Video sent successfully!")
        print(f"   Message ID: {result['message_id']}")
        print(f"   Chat ID: {result['chat_id']}")
        print(f"   File Key: {result['file_key']}")
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()

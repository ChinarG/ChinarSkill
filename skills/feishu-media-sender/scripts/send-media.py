#!/usr/bin/env python3
"""
Feishu Media Sender
飞书媒体发送工具 - 支持图片、文件、视频

Usage:
    python3 send-media.py --file image.png --to ou_xxx --type image
    python3 send-media.py --file document.pdf --to ou_xxx --type file
    python3 send-media.py --file video.mp4 --to ou_xxx --type video
"""

import requests
import json
import os
import argparse
from typing import Optional, Literal


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


def upload_image(token: str, file_path: str) -> str:
    """
    上传图片到飞书
    
    Args:
        token: tenant_access_token
        file_path: 图片文件路径
        
    Returns:
        image_key: 飞书图片标识
    """
    url = "https://open.feishu.cn/open-apis/im/v1/images"
    headers = {"Authorization": f"Bearer {token}"}
    
    file_name = os.path.basename(file_path)
    
    with open(file_path, 'rb') as f:
        files = {'image': (file_name, f)}
        data = {'image_type': 'message'}
        resp = requests.post(url, headers=headers, data=data, files=files)
    
    result = resp.json()
    
    if result.get("code") != 0:
        raise Exception(f"Image upload failed: {result.get('msg')}")
    
    return result["data"]["image_key"]


def upload_file(token: str, file_path: str, file_type: str) -> str:
    """
    上传文件到飞书 IM
    
    Args:
        token: tenant_access_token
        file_path: 文件路径
        file_type: 文件类型 (mp4, pdf, doc, xls, ppt, stream)
        
    Returns:
        file_key: 飞书文件标识
    """
    url = "https://open.feishu.cn/open-apis/im/v1/files"
    headers = {"Authorization": f"Bearer {token}"}
    
    file_name = os.path.basename(file_path)
    
    with open(file_path, 'rb') as f:
        files = {'file': (file_name, f)}
        data = {
            'file_type': file_type,
            'file_name': file_name
        }
        resp = requests.post(url, headers=headers, data=data, files=files)
    
    result = resp.json()
    
    if result.get("code") != 0:
        raise Exception(f"File upload failed: {result.get('msg')}")
    
    return result["data"]["file_key"]


def send_image_message(token: str, image_key: str, receive_id: str) -> dict:
    """发送图片消息"""
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    params = {"receive_id_type": "open_id"}
    
    content = {"image_key": image_key}
    
    data = {
        "receive_id": receive_id,
        "msg_type": "image",
        "content": json.dumps(content)
    }
    
    resp = requests.post(url, headers=headers, params=params, json=data)
    result = resp.json()
    
    if result.get("code") != 0:
        raise Exception(f"Send image failed: {result.get('msg')}")
    
    return result["data"]


def send_file_message(token: str, file_key: str, receive_id: str, msg_type: str = "file") -> dict:
    """发送文件/媒体消息"""
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    params = {"receive_id_type": "open_id"}
    
    content = {"file_key": file_key}
    
    data = {
        "receive_id": receive_id,
        "msg_type": msg_type,  # file 或 media
        "content": json.dumps(content)
    }
    
    resp = requests.post(url, headers=headers, params=params, json=data)
    result = resp.json()
    
    if result.get("code") != 0:
        raise Exception(f"Send file failed: {result.get('msg')}")
    
    return result["data"]


def detect_file_type(file_path: str) -> tuple:
    """
    检测文件类型
    
    Returns:
        (media_type, file_type, msg_type)
        media_type: image | video | file
        file_type: mp4 | pdf | doc | xls | ppt | stream
        msg_type: image | media | file
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    # 图片类型
    image_exts = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
    if ext in image_exts:
        return ('image', None, 'image')
    
    # 视频类型
    video_exts = ['.mp4', '.mov', '.avi', '.mkv', '.flv']
    if ext in video_exts:
        return ('video', 'mp4', 'media')
    
    # 文档类型
    doc_exts = ['.doc', '.docx']
    if ext in doc_exts:
        return ('file', 'doc', 'file')
    
    # 表格类型
    xls_exts = ['.xls', '.xlsx']
    if ext in xls_exts:
        return ('file', 'xls', 'file')
    
    # PPT类型
    ppt_exts = ['.ppt', '.pptx']
    if ext in ppt_exts:
        return ('file', 'ppt', 'file')
    
    # PDF类型
    if ext == '.pdf':
        return ('file', 'pdf', 'file')
    
    # 其他类型
    return ('file', 'stream', 'file')


def send_media_to_feishu(
    file_path: str,
    receive_id: str,
    media_type: Optional[Literal['image', 'video', 'file', 'auto']] = 'auto',
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> dict:
    """
    发送媒体文件到飞书
    
    Args:
        file_path: 文件路径
        receive_id: 接收者 open_id
        media_type: 媒体类型 (image/video/file/auto)，默认自动检测
        app_id: 飞书 App ID (可选)
        app_secret: 飞书 App Secret (可选)
        
    Returns:
        发送结果
    """
    # 读取凭证
    app_id = app_id or os.environ.get("FEISHU_APP_ID")
    app_secret = app_secret or os.environ.get("FEISHU_APP_SECRET")
    
    if not app_id or not app_secret:
        raise ValueError("App ID and App Secret are required")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # 检测文件类型
    if media_type == 'auto':
        detected_type, file_type, msg_type = detect_file_type(file_path)
    else:
        type_map = {
            'image': ('image', None, 'image'),
            'video': ('video', 'mp4', 'media'),
            'file': ('file', 'stream', 'file')
        }
        detected_type, file_type, msg_type = type_map.get(media_type, ('file', 'stream', 'file'))
    
    # 获取 token
    token = get_tenant_token(app_id, app_secret)
    
    # 上传和发送
    if detected_type == 'image':
        image_key = upload_image(token, file_path)
        result = send_image_message(token, image_key, receive_id)
        return {
            "message_id": result.get("message_id"),
            "chat_id": result.get("chat_id"),
            "image_key": image_key,
            "type": "image"
        }
    else:
        file_key = upload_file(token, file_path, file_type)
        result = send_file_message(token, file_key, receive_id, msg_type)
        return {
            "message_id": result.get("message_id"),
            "chat_id": result.get("chat_id"),
            "file_key": file_key,
            "type": msg_type
        }


def main():
    parser = argparse.ArgumentParser(description="Send media to Feishu")
    parser.add_argument("--file", "-f", required=True, help="File path")
    parser.add_argument("--to", "-t", required=True, help="Receiver open_id")
    parser.add_argument("--type", choices=['image', 'video', 'file', 'auto'], 
                       default='auto', help="Media type (default: auto)")
    parser.add_argument("--app-id", help="Feishu App ID")
    parser.add_argument("--app-secret", help="Feishu App Secret")
    
    args = parser.parse_args()
    
    try:
        result = send_media_to_feishu(
            file_path=args.file,
            receive_id=args.to,
            media_type=args.type,
            app_id=args.app_id,
            app_secret=args.app_secret
        )
        print(f"✅ {result['type'].upper()} sent successfully!")
        print(f"   Message ID: {result['message_id']}")
        print(f"   Chat ID: {result['chat_id']}")
        if 'image_key' in result:
            print(f"   Image Key: {result['image_key']}")
        if 'file_key' in result:
            print(f"   File Key: {result['file_key']}")
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()

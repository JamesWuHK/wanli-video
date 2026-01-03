#!/usr/bin/env python3
"""
Runway API 测试脚本 - 图片生成视频

注意：此脚本需要正确的 Runway API 端点
Runway 官方 API 文档: https://docs.runwayml.com/
"""

import requests
import json
import time
from typing import Optional, Dict, Any

# API 配置
API_KEY = "sk-hSsIao5zgH3uctxxJqWZOezaSW2HZWFTf8HHJQgL6mav6cpJ"

# 可能的 API 端点（需要根据实际情况选择）
ENDPOINTS = {
    "apifox_doc": "https://vectorengine.apifox.cn/api-349239177",  # 这个似乎是文档页面
    "runway_official": "https://api.runwayml.com/v1",  # Runway 官方 API
    "custom_proxy": "https://vectorengine.apifox.cn/v1",  # 可能的代理端点
}

# 选择要使用的端点
BASE_URL = ENDPOINTS["apifox_doc"]

# 设置请求头
def get_headers(content_type: str = "application/json") -> Dict[str, str]:
    """生成请求头"""
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": content_type,
        "User-Agent": "Runway-API-Test/1.0"
    }


def test_image_to_video(image_url, prompt="", duration=5):
    """
    测试图片生成视频功能

    Args:
        image_url: 图片URL
        prompt: 视频生成提示词（可选）
        duration: 视频时长（秒）
    """
    print("=" * 60)
    print("测试 Runway 图片生成视频 API")
    print("=" * 60)

    # 构建请求数据
    payload = {
        "image_url": image_url,
        "prompt": prompt,
        "duration": duration
    }

    print(f"\n请求数据:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    try:
        # 发送请求
        print(f"\n发送请求到: {BASE_URL}")
        response = requests.post(
            BASE_URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        print(f"\n状态码: {response.status_code}")
        print(f"\n响应头:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")

        # 打印响应内容
        print(f"\n响应内容:")
        try:
            response_json = response.json()
            print(json.dumps(response_json, indent=2, ensure_ascii=False))

            # 检查是否成功
            if response.status_code == 200:
                print("\n✅ 请求成功！")
                if "task_id" in response_json or "id" in response_json:
                    task_id = response_json.get("task_id") or response_json.get("id")
                    print(f"任务ID: {task_id}")
                if "video_url" in response_json:
                    print(f"视频URL: {response_json['video_url']}")
            else:
                print(f"\n❌ 请求失败: {response.status_code}")

        except json.JSONDecodeError:
            print(response.text)

    except requests.exceptions.Timeout:
        print("\n❌ 请求超时")
    except requests.exceptions.RequestException as e:
        print(f"\n❌ 请求错误: {e}")

    print("\n" + "=" * 60)


def test_with_sample_image():
    """
    使用示例图片测试
    """
    # 使用一个公开的示例图片
    sample_image = "https://images.unsplash.com/photo-1506905925346-21bda4d32df4"
    prompt = "A beautiful mountain landscape with moving clouds"

    test_image_to_video(
        image_url=sample_image,
        prompt=prompt,
        duration=5
    )


if __name__ == "__main__":
    print("\nRunway API 测试工具")
    print("=" * 60)
    print("\n选项:")
    print("1. 使用示例图片测试")
    print("2. 使用自定义图片URL测试")

    choice = input("\n请选择 (1 或 2, 直接回车默认为1): ").strip()

    if choice == "2":
        image_url = input("请输入图片URL: ").strip()
        prompt = input("请输入提示词（可选，直接回车跳过）: ").strip()
        duration = input("请输入视频时长（秒，默认5）: ").strip()
        duration = int(duration) if duration else 5

        test_image_to_video(image_url, prompt, duration)
    else:
        test_with_sample_image()

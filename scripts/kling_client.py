#!/usr/bin/env python3
"""
可灵 Kling AI 图生视频客户端
支持原生中文，解决VEO3中文乱码问题
"""

import os
import time
import base64
import requests
from pathlib import Path
from typing import Optional, Dict, Any


class KlingClient:
    """可灵AI视频生成客户端"""

    def __init__(self, api_key: str, base_url: str = "https://api.302.ai"):
        """初始化可灵客户端

        Args:
            api_key: API密钥
            base_url: API基础URL
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        print(f"✅ 可灵 Kling 客户端初始化成功")
        print(f"   API Key: {api_key[:20]}...")
        print(f"   Base URL: {base_url}")

    def _encode_image(self, image_path: Path) -> str:
        """将图片编码为base64"""
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')

    def generate_video_from_image(
        self,
        image_path: Path,
        prompt: str = "",
        model: str = "kling-v2-5-turbo",
        mode: str = "std",
        duration: int = 5,
        aspect_ratio: str = "16:9",
        cfg_scale: float = 0.5,
        output_path: Optional[Path] = None
    ) -> Optional[Path]:
        """使用图片生成视频

        Args:
            image_path: 输入图片路径
            prompt: 文本提示词（可选，支持中文）
            model: 模型名称 (kling-v2-5-turbo, kling-v2-6等)
            mode: 模式 (std标准版, pro高品质版)
            duration: 视频时长（秒），支持 5, 10
            aspect_ratio: 宽高比，默认 16:9
            cfg_scale: 生成自由度 [0, 1]，值越大相关性越强
            output_path: 输出视频路径

        Returns:
            生成的视频路径，失败返回 None
        """
        print(f"   🤖 调用可灵 {model} ({mode}) 生成视频...")
        if prompt:
            print(f"      提示词: {prompt[:60]}...")
        else:
            print(f"      提示词: (使用图片自动生成)")

        try:
            # 读取并上传图片
            with open(image_path, 'rb') as f:
                image_data = f.read()

            # 第一步：上传图片获取URL
            upload_url = f"{self.base_url}/kling/v1/images/upload"
            files = {
                'image': (image_path.name, image_data, 'image/png')
            }

            print(f"   📤 上传图片...")
            upload_response = requests.post(
                upload_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                files=files,
                timeout=60
            )

            if upload_response.status_code != 200:
                print(f"   ❌ 图片上传失败: {upload_response.status_code}")
                print(f"   响应: {upload_response.text}")
                return None

            upload_result = upload_response.json()
            if upload_result.get('code') != 0:
                print(f"   ❌ 图片上传失败: {upload_result.get('message')}")
                return None

            image_url = upload_result.get('data', {}).get('url')
            if not image_url:
                print(f"   ❌ 未获取到图片URL")
                return None

            print(f"   ✅ 图片上传成功")

            # 第二步：提交视频生成任务
            payload = {
                "model_name": model,
                "mode": mode,
                "image": image_url,
                "aspect_ratio": aspect_ratio,
                "duration": str(duration),
                "cfg_scale": cfg_scale
            }

            if prompt:
                payload["prompt"] = prompt

            print(f"   📊 参数: model={model}, mode={mode}, duration={duration}s")

            response = requests.post(
                f"{self.base_url}/kling/v1/videos/image2video",
                headers=self.headers,
                json=payload,
                timeout=120
            )

            response.raise_for_status()
            result = response.json()

            print(f"   📦 API 响应: {result}")

            if result.get('code') != 0:
                error_msg = result.get('message', 'Unknown error')
                print(f"   ❌ 视频生成失败: {error_msg}")
                return None

            # 提取任务ID
            task_data = result.get('data', {})
            task_id = task_data.get('task_id')
            task_status = task_data.get('task_status')

            if not task_id:
                print(f"   ❌ 未获取到任务ID")
                return None

            print(f"   ✅ 视频任务创建成功: ID={task_id}, 状态={task_status}")

            # 第三步：轮询任务状态
            print(f"   ⏳ 等待视频生成...")
            max_retries = 120  # 可灵生成较慢，需要1-2分钟

            for i in range(max_retries):
                time.sleep(5)  # 每5秒查询一次

                # 查询任务状态
                status_url = f"{self.base_url}/kling/v1/videos/{task_id}"
                status_response = requests.get(
                    status_url,
                    headers=self.headers,
                    timeout=30
                )

                if status_response.status_code == 200:
                    status_result = status_response.json()

                    if status_result.get('code') != 0:
                        print(f"   ⚠️  状态查询失败: {status_result.get('message')}")
                        continue

                    status_data = status_result.get('data', {})
                    current_status = status_data.get('task_status', 'unknown')

                    print(f"      状态检查 {i+1}/{max_retries}: {current_status}")

                    if current_status == 'succeed':
                        # 任务成功
                        videos = status_data.get('task_result', {}).get('videos', [])
                        if videos and len(videos) > 0:
                            video_url = videos[0].get('url')

                            if video_url:
                                print(f"   ✅ 视频生成成功: {video_url}")

                                # 下载视频
                                if output_path:
                                    print(f"   📥 下载视频...")
                                    video_response = requests.get(video_url, timeout=120)
                                    video_response.raise_for_status()

                                    output_path.parent.mkdir(parents=True, exist_ok=True)
                                    with open(output_path, 'wb') as f:
                                        f.write(video_response.content)

                                    file_size = len(video_response.content) / (1024 * 1024)
                                    print(f"   ✅ 视频已保存: {output_path} ({file_size:.1f}MB)")
                                    return output_path

                                return None

                        print(f"   ❌ 未找到视频URL")
                        return None

                    elif current_status == 'failed':
                        error_msg = status_data.get('task_status_msg', 'Unknown error')
                        print(f"   ❌ 视频生成失败: {error_msg}")
                        return None

                else:
                    print(f"   ⚠️  状态查询失败: HTTP {status_response.status_code}")

            print(f"   ❌ 等待超时")
            return None

        except requests.exceptions.RequestException as e:
            print(f"   ❌ API请求失败: {e}")
            if hasattr(e, 'response') and e.response:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('message', e.response.text)
                    print(f"   响应内容: {error_msg}")
                except:
                    print(f"   响应内容: {e.response.text}")
            return None
        except Exception as e:
            print(f"   ❌ 生成失败: {e}")
            import traceback
            traceback.print_exc()
            return None


def main():
    """测试函数"""
    import argparse

    parser = argparse.ArgumentParser(description='可灵AI图生视频客户端')
    parser.add_argument('--api-key', required=True, help='API密钥')
    parser.add_argument('--image', required=True, help='输入图片路径')
    parser.add_argument('--prompt', default='', help='文本提示词（支持中文）')
    parser.add_argument('--model', default='kling-v2-5-turbo', help='模型名称')
    parser.add_argument('--mode', default='std', choices=['std', 'pro'], help='模式')
    parser.add_argument('--duration', type=int, default=5, choices=[5, 10], help='视频时长')
    parser.add_argument('--output', required=True, help='输出视频路径')
    parser.add_argument('--base-url', default='https://api.302.ai', help='API基础URL')

    args = parser.parse_args()

    client = KlingClient(api_key=args.api_key, base_url=args.base_url)

    result = client.generate_video_from_image(
        image_path=Path(args.image),
        prompt=args.prompt,
        model=args.model,
        mode=args.mode,
        duration=args.duration,
        output_path=Path(args.output)
    )

    if result:
        print(f"\n✅ 成功！视频保存至: {result}")
    else:
        print(f"\n❌ 失败")
        exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
VectorEngine (向量引擎) API 客户端 - 修复版
支持 sora-2, veo_3_1-fast 等多种视频生成模型
"""

import os
import time
import base64
import requests
from pathlib import Path
from typing import Optional, Dict, Any


class VectorEngineClient:
    """VectorEngine API 客户端"""

    def __init__(self, api_key: str = None, base_url: str = "https://api.vectorengine.ai/v1"):
        """初始化客户端

        Args:
            api_key: API密钥，如不提供则从环境变量 VECTORENGINE_API_KEY 读取
            base_url: API基础URL
        """
        self.api_key = api_key or os.getenv('VECTORENGINE_API_KEY')
        if not self.api_key:
            raise ValueError("需要提供 API Key 或设置环境变量 VECTORENGINE_API_KEY")

        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        print(f"✅ VectorEngine 客户端初始化成功")
        print(f"   API Key: {self.api_key[:20]}...")

    def _encode_image(self, image_path: Path) -> str:
        """将图片编码为 base64

        Args:
            image_path: 图片路径

        Returns:
            base64 编码的图片字符串
        """
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')

    def generate_video_from_image(
        self,
        image_path: Path,
        prompt: str,
        model: str = "sora-2",
        duration: int = 5,
        aspect_ratio: str = "16:9",
        output_path: Optional[Path] = None
    ) -> Optional[Path]:
        """使用图片生成视频（使用 VectorEngine 统一视频格式 /v1/video/create）

        Args:
            image_path: 输入图片路径
            prompt: 视频生成提示词
            model: 模型名称 (sora-2, sora-2-all 等)
            duration: 视频时长（秒），支持 10, 15
            aspect_ratio: 宽高比，默认 16:9
            output_path: 输出视频路径

        Returns:
            生成的视��路径，失败返回 None
        """
        print(f"   🤖 调用 VectorEngine {model} 生成视频...")
        print(f"      提示词: {prompt[:60]}...")

        try:
            # 将宽高比转换为分辨率格式
            size_map = {
                "16:9": "1280x720",
                "9:16": "720x1280",
            }
            size = size_map.get(aspect_ratio, "1280x720")

            # VectorEngine 支持 10s 和 15s
            if duration <= 10:
                video_duration = 10
            else:
                video_duration = 15

            # 编码图片为 base64
            image_base64 = self._encode_image(image_path)

            # 构建请求（JSON 格式）
            payload = {
                "model": model,
                "prompt": prompt,
                "image": f"data:image/png;base64,{image_base64}",
                "size": size,
                "duration": video_duration
            }

            print(f"   📊 参数: model={model}, size={size}, duration={video_duration}s")

            # 使用 /v1/video/create 端点（VectorEngine 统一视频格式）
            response = requests.post(
                f"{self.base_url}/video/create",
                headers=self.headers,
                json=payload,
                timeout=600
            )

            response.raise_for_status()
            result = response.json()

            print(f"   📦 API 响应: {result}")

            # 处理响应
            video_id = result.get('id')
            status = result.get('status', 'unknown')

            if status == 'error':
                error_msg = result.get('error', 'Unknown error')
                print(f"   ❌ 视频生成失败: {error_msg}")
                return None

            print(f"   ✅ 视频任务创建成功: ID={video_id}, 状态={status}")

            # 如果是异步任务，需要轮询状态
            if status in ['pending', 'processing', 'queued', 'in_progress']:
                print(f"   ⏳ 等待视频生成...")
                max_retries = 60

                for i in range(max_retries):
                    time.sleep(10)

                    # 查询状态
                    status_response = requests.get(
                        f"{self.base_url}/videos/{video_id}",
                        headers=self.headers,
                        timeout=30
                    )

                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        current_status = status_data.get('status', 'unknown')
                        progress = status_data.get('progress', 0)
                        print(f"      状态检查 {i+1}/{max_retries}: {current_status} ({progress}%)")

                        if current_status in ['completed', 'success']:
                            result = status_data
                            break
                        elif current_status in ['failed', 'error']:
                            error_msg = status_data.get('error', 'Unknown error')
                            print(f"   ❌ 视频生成失败: {error_msg}")
                            return None
                    else:
                        print(f"   ⚠️  状态查询失败: HTTP {status_response.status_code}")
                else:
                    print(f"   ❌ 等待超时")
                    return None

            # 提取视频 URL
            video_url = None
            if 'url' in result:
                video_url = result['url']
            elif 'video_url' in result:
                video_url = result['video_url']
            elif 'output' in result:
                if isinstance(result['output'], dict) and 'url' in result['output']:
                    video_url = result['output']['url']
                elif isinstance(result['output'], str):
                    video_url = result['output']
            elif 'data' in result and isinstance(result['data'], list) and len(result['data']) > 0:
                video_url = result['data'][0].get('url')

            if not video_url:
                print(f"   ⚠️  未找到视频URL")
                print(f"   完整响应: {result}")
                return None

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

        except requests.exceptions.RequestException as e:
            print(f"   ❌ API请求失败: {e}")
            if hasattr(e, 'response') and e.response:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('error', e.response.text)
                    print(f"   响应内容: {error_msg}")
                except:
                    print(f"   响应内容: {e.response.text}")
            return None
        except Exception as e:
            print(f"   ❌ 生成失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def check_balance(self) -> Optional[Dict[str, Any]]:
        """查询账户余额

        Returns:
            账户信息字典，失败返回 None
        """
        try:
            response = requests.get(
                f"{self.base_url}/dashboard/billing/subscription",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"   ⚠️  查询余额失败: {e}")
            return None


def main():
    """测试函数"""
    import argparse

    parser = argparse.ArgumentParser(description='VectorEngine 视频生成测试')
    parser.add_argument('--api-key', help='API密钥')
    parser.add_argument('--image', help='输入图片路径')
    parser.add_argument('--prompt', default='一段自然流畅的动态视频', help='提示词')
    parser.add_argument('--model', default='sora-2', help='模型名称')
    parser.add_argument('--output', help='输出视频路径')
    parser.add_argument('--check-balance', action='store_true', help='查询余额')

    args = parser.parse_args()

    client = VectorEngineClient(api_key=args.api_key)

    if args.check_balance:
        balance = client.check_balance()
        if balance:
            print(f"\n💰 账户信息: {balance}")
        return

    if args.image:
        output_path = Path(args.output) if args.output else Path('output_video.mp4')
        result = client.generate_video_from_image(
            image_path=Path(args.image),
            prompt=args.prompt,
            model=args.model,
            output_path=output_path
        )
        if result:
            print(f"\n✅ 成功！视频保存至: {result}")
    else:
        print("❌ 请提供 --image 参数")


if __name__ == "__main__":
    main()

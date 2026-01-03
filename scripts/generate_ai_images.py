#!/usr/bin/env python3
"""
AI 图像生成脚本
支持多种图像生成服务：OpenAI DALL-E、Google Imagen 等
为分镜场景生成设计参考图
"""

import os
import json
import base64
import requests
from pathlib import Path
from typing import Dict, List, Optional
import yaml
import time


class AIImageGenerator:
    """AI 图像生成器 - 支持多种服务"""

    def __init__(self):
        """初始化图像生成器"""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")

        # 检查可用的服务
        self.available_services = []
        if self.openai_api_key:
            self.available_services.append("openai")
        if self.google_api_key:
            self.available_services.append("google")

        if not self.available_services:
            print("⚠️  警告：未配置任何图像生成服务的 API Key")
            print("请在 .env 文件中配置以下之一：")
            print("  - OPENAI_API_KEY (用于 DALL-E)")
            print("  - GOOGLE_API_KEY (用于 Imagen)")
            print("\n将使用模拟模式生成占位图...")
            self.mock_mode = True
        else:
            self.mock_mode = False
            print(f"✅ 可用服务: {', '.join(self.available_services)}")

    def load_script(self, script_path: str) -> Dict:
        """加载脚本文件"""
        with open(script_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def extract_scenes(self, script_data: Dict) -> List[Dict]:
        """提取场景信息"""
        scenes = []
        for scene in script_data.get('scenes', []):
            if 'image_generation_prompt' in scene:
                scenes.append({
                    'id': scene['id'],
                    'prompt': scene['image_generation_prompt'],
                    'narration': scene.get('narration', ''),
                    'duration': scene.get('duration', 0),
                    'storyboard': scene.get('storyboard', {})
                })
        return scenes

    def generate_with_openai_dalle(self, prompt: str, output_path: str) -> bool:
        """使用 OpenAI DALL-E 生成图像

        Args:
            prompt: 图像描述
            output_path: 输出路径

        Returns:
            是否成功
        """
        try:
            # DALL-E 3 API
            url = "https://api.openai.com/v1/images/generations"
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }

            # DALL-E 3 参数
            data = {
                "model": "dall-e-3",
                "prompt": prompt[:4000],  # DALL-E 3 限制
                "n": 1,
                "size": "1792x1024",  # 接近 16:9
                "quality": "hd",
                "style": "vivid"
            }

            print(f"      ⏳ 调用 DALL-E 3 生成图像...")
            response = requests.post(url, headers=headers, json=data, timeout=120)

            if response.status_code == 200:
                result = response.json()
                image_url = result['data'][0]['url']

                # 下载图像
                print(f"      ⏳ 下载图像...")
                img_response = requests.get(image_url, timeout=30)

                if img_response.status_code == 200:
                    with open(output_path, 'wb') as f:
                        f.write(img_response.content)
                    print(f"      ✅ 图像已保存")
                    return True
                else:
                    print(f"      ❌ 下载失败: {img_response.status_code}")
                    return False
            else:
                error_msg = response.json().get('error', {}).get('message', '未知错误')
                print(f"      ❌ 生成失败: {error_msg}")
                return False

        except Exception as e:
            print(f"      ❌ 异常: {str(e)}")
            return False

    def generate_with_stability(self, prompt: str, output_path: str) -> bool:
        """使用 Stability AI 生成图像（备用方案）

        注意：需要单独申请 Stability AI API Key
        """
        stability_key = os.getenv("STABILITY_API_KEY")
        if not stability_key:
            return False

        # Stability AI 实现...
        return False

    def create_placeholder_image(self, scene: Dict, output_path: str):
        """创建占位图（当无法使用AI生成时）"""
        from PIL import Image, ImageDraw, ImageFont

        # 创建 16:9 图像
        width, height = 1920, 1080
        img = Image.new('RGB', (width, height), color='#2C2C2C')
        draw = ImageDraw.Draw(img)

        # 尝试加载字体
        try:
            font_large = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 60)
            font_small = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 30)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # 绘制场景ID
        scene_id = scene['id']
        draw.text((width//2, height//2 - 100), scene_id,
                 fill='white', font=font_large, anchor='mm')

        # 绘制提示
        draw.text((width//2, height//2 + 50),
                 "[ 占位图 - 请配置 API Key 生成实际图像 ]",
                 fill='#888888', font=font_small, anchor='mm')

        # 绘制旁白片段
        narration = scene.get('narration', '')[:50] + '...'
        draw.text((width//2, height//2 + 120),
                 narration,
                 fill='#666666', font=font_small, anchor='mm')

        img.save(output_path, quality=95)

    def generate_images(self, script_path: str, output_dir: str):
        """为所有场景生成图像

        Args:
            script_path: 脚本文件路径
            output_dir: 输出目录
        """
        # 加载脚本
        print(f"\n📖 加载脚本: {script_path}")
        script_data = self.load_script(script_path)

        # 提取场景
        scenes = self.extract_scenes(script_data)
        print(f"✅ 找到 {len(scenes)} 个场景\n")

        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 生成图像
        success_count = 0
        failed_scenes = []

        for i, scene in enumerate(scenes, 1):
            scene_id = scene['id']
            print(f"🎨 [{i}/{len(scenes)}] {scene_id}")
            print(f"   时长: {scene['duration']}秒")
            print(f"   旁白: {scene['narration'][:50]}...")

            # 输出路径
            img_path = output_path / f"{scene_id}_ai_generated.png"

            # 如果已存在，跳过
            if img_path.exists():
                print(f"   ⏭️  已存在，跳过")
                success_count += 1
                continue

            # 尝试生成
            success = False

            if not self.mock_mode:
                # 使用真实 AI 服务
                if "openai" in self.available_services:
                    success = self.generate_with_openai_dalle(
                        scene['prompt'],
                        str(img_path)
                    )

                    # DALL-E API 有速率限制，等待一下
                    if success and i < len(scenes):
                        print(f"      ⏳ 等待 3 秒（避免速率限制）...")
                        time.sleep(3)

            # 如果失败或模拟模式，创建占位图
            if not success:
                if self.mock_mode:
                    print(f"   📝 创建占位图...")
                else:
                    print(f"   📝 生成失败，创建占位图...")

                self.create_placeholder_image(scene, str(img_path))

            success_count += 1
            print()

        # 总结
        print("=" * 60)
        print(f"✅ 完成！成功生成 {success_count}/{len(scenes)} 张图像")

        if failed_scenes:
            print(f"\n⚠️  以下场景生成失败：")
            for scene_id in failed_scenes:
                print(f"   - {scene_id}")

        print(f"\n📁 输出目录: {output_dir}")
        print("=" * 60)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="为分镜场景生成 AI 图像")
    parser.add_argument(
        "--script",
        default="./文脉薪传_细化脚本.yaml",
        help="脚本文件路径"
    )
    parser.add_argument(
        "--output",
        default="./storyboards/文脉薪传/ai_generated_images",
        help="输出目录"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("🎨 AI 图像生成器")
    print("=" * 60)

    # 创建生成器
    generator = AIImageGenerator()

    # 生成图像
    generator.generate_images(args.script, args.output)

    print("\n💡 提示：")
    if generator.mock_mode:
        print("  1. 当前为模拟模式（生成占位图）")
        print("  2. 要生成真实图像，请配置 API Key：")
        print("     - OPENAI_API_KEY (DALL-E)")
        print("     - GOOGLE_API_KEY (Imagen)")
    else:
        print("  1. 图像已生成，请查看输出目录")
        print("  2. 可以将这些图像用作视频制作的参考")
    print("  3. 也可以使用提示词在 Midjourney 中生成更精美的图像")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
使用青云API豆包模型生成万里书院2026元旦海报
豆包模型支持准确渲染中文汉字
"""

import os
import requests
import time
from pathlib import Path
from datetime import datetime


class DoubaoPosterGenerator:
    """豆包AI海报生成器"""

    def __init__(self, api_key: str = None):
        """初始化"""
        self.api_key = api_key or os.getenv("QINGYUN_API_KEY")
        if not self.api_key:
            raise ValueError("需要提供 QINGYUN_API_KEY 环境变量或 --api-key 参数")

        self.base_url = "https://api.qingyuntop.top/v1"
        print(f"✅ 青云API已配置 - 豆包模型（支持中文汉字渲染）")

    def generate_poster(self, prompt: str, output_path: str):
        """生成海报"""
        url = f"{self.base_url}/images/generations"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # 豆包模型参数
        data = {
            "model": "doubao-seedream-4-0-250828",
            "prompt": prompt,
            "n": 1,
            "size": "2048x1152",  # 16:9 横版海报
            "sequential_image_generation": "disabled",
            "watermark": True,
            "stream": False,
            "response_format": "url"
        }

        print("⏳ 正在生成海报...")
        print(f"   模型: doubao-seedream-4-0-250828")
        print(f"   尺寸: 2048x1152 (16:9)")
        print(f"   提示词: {prompt[:100]}...")
        print()

        try:
            # 调用API生成
            response = requests.post(url, headers=headers, json=data, timeout=180)

            if response.status_code == 200:
                result = response.json()
                image_url = result['data'][0]['url']

                print("✅ 图像生成成功！")
                print(f"   图像URL: {image_url[:80]}...")
                print()

                # 下载图像
                print("⏳ 正在下载图像...")
                img_response = requests.get(image_url, timeout=60)

                if img_response.status_code == 200:
                    with open(output_path, 'wb') as f:
                        f.write(img_response.content)

                    file_size = len(img_response.content) / 1024 / 1024
                    print(f"✅ 下载成功！")
                    print(f"   文件大小: {file_size:.2f} MB")
                    return True
                else:
                    print(f"❌ 下载失败: HTTP {img_response.status_code}")
                    return False

            else:
                error_msg = response.text
                try:
                    error_json = response.json()
                    error_msg = error_json.get('error', {}).get('message', error_msg)
                except:
                    pass
                print(f"❌ API错误 ({response.status_code}): {error_msg}")
                return False

        except Exception as e:
            print(f"❌ 生成失败: {str(e)}")
            return False


def create_premium_design_poster(output_path: str):
    """创建专业级设计海报（无需API）"""
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageFilter
        import random
    except ImportError:
        print("❌ 需要安装 Pillow: pip install Pillow")
        return False

    print("⏳ 正在创建专业级设计海报...")

    # 创建 16:9 超高清画布
    width, height = 2048, 1152

    # 创建更复杂的渐变背景
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)

    # 绘制径向渐变背景（中国红）
    for y in range(height):
        for x in range(width):
            # 计算距离中心的距离
            dx = (x - width/2) / width
            dy = (y - height/2) / height
            distance = (dx**2 + dy**2) ** 0.5

            # 径向渐变：中心亮，边缘暗
            factor = max(0, min(1, distance))
            r = int(200 - 80 * factor)
            g = int(20 - 10 * factor)
            b = int(30 - 20 * factor)

            img.putpixel((x, y), (r, g, b))

    # 添加装饰图案层
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)

    # 绘制多层祥云图案
    for layer in range(3):
        for _ in range(30):
            x = random.randint(-200, width)
            y = random.randint(-200, height)
            size = random.randint(100, 300)
            alpha = random.randint(10, 30)
            overlay_draw.ellipse(
                [(x, y), (x + size, y + size//2)],
                fill=(255, 215, 0, alpha)
            )

    # 绘制烟花效果
    for _ in range(15):
        cx = random.randint(0, width)
        cy = random.randint(0, height//2)
        for angle in range(0, 360, 30):
            import math
            length = random.randint(50, 150)
            end_x = cx + int(length * math.cos(math.radians(angle)))
            end_y = cy + int(length * math.sin(math.radians(angle)))
            overlay_draw.line(
                [(cx, cy), (end_x, end_y)],
                fill=(255, 215, 0, 80),
                width=2
            )

    # 合并图层
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')

    # 添加光晕效果
    img = img.filter(ImageFilter.GaussianBlur(radius=3))

    draw = ImageDraw.Draw(img)

    # 尝试加载中文字体
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "C:\\Windows\\Fonts\\simhei.ttf",
        "C:\\Windows\\Fonts\\msyh.ttc",
    ]

    title_font = subtitle_font = year_font = None
    for font_path in font_paths:
        try:
            title_font = ImageFont.truetype(font_path, 160)
            subtitle_font = ImageFont.truetype(font_path, 100)
            year_font = ImageFont.truetype(font_path, 280)
            break
        except:
            continue

    if not title_font:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        year_font = ImageFont.load_default()

    # 绘制年份背景（半透明大字）
    year_text = "2026"
    year_bbox = draw.textbbox((0, 0), year_text, font=year_font)
    year_width = year_bbox[2] - year_bbox[0]
    year_height = year_bbox[3] - year_bbox[1]
    year_x = (width - year_width) // 2
    year_y = height - year_height - 80

    # 多层阴影效果
    for offset in range(8, 0, -1):
        shadow_alpha = int(100 * (1 - offset / 8))
        draw.text(
            (year_x + offset, year_y + offset),
            year_text,
            fill=(0, 0, 0, shadow_alpha),
            font=year_font
        )

    draw.text(
        (year_x, year_y),
        year_text,
        fill=(255, 215, 0),
        font=year_font,
        stroke_width=4,
        stroke_fill=(139, 0, 0)
    )

    # 绘制主标题
    title_text = "万里书院"
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_height = title_bbox[3] - title_bbox[1]
    title_x = (width - title_width) // 2
    title_y = 180

    # 多层阴影
    for offset in range(5, 0, -1):
        draw.text(
            (title_x + offset * 2, title_y + offset * 2),
            title_text,
            fill=(0, 0, 0, 150),
            font=title_font
        )

    draw.text(
        (title_x, title_y),
        title_text,
        fill=(255, 223, 0),
        font=title_font,
        stroke_width=4,
        stroke_fill=(200, 0, 0)
    )

    # 绘制副标题
    subtitle_text = "元旦快乐"
    subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (width - subtitle_width) // 2
    subtitle_y = title_y + title_height + 50

    for offset in range(3, 0, -1):
        draw.text(
            (subtitle_x + offset * 2, subtitle_y + offset * 2),
            subtitle_text,
            fill=(0, 0, 0, 150),
            font=subtitle_font
        )

    draw.text(
        (subtitle_x, subtitle_y),
        subtitle_text,
        fill=(255, 255, 255),
        font=subtitle_font,
        stroke_width=3,
        stroke_fill=(255, 215, 0)
    )

    # 添加装饰线和图案
    line_y = subtitle_y + subtitle_bbox[3] + 40
    line_length = 800
    line_x1 = (width - line_length) // 2
    line_x2 = line_x1 + line_length

    # 双线装饰
    draw.line([(line_x1, line_y), (line_x2, line_y)], fill=(255, 215, 0), width=4)
    draw.line([(line_x1, line_y + 8), (line_x2, line_y + 8)], fill=(255, 215, 0), width=2)

    # 装饰圆点
    for i in range(7):
        circle_x = line_x1 + i * (line_length // 6)
        draw.ellipse(
            [(circle_x - 12, line_y - 12), (circle_x + 12, line_y + 12)],
            fill=(255, 223, 0),
            outline=(200, 0, 0),
            width=2
        )

    # 保存
    img.save(output_path, quality=98, dpi=(300, 300))

    file_size = os.path.getsize(output_path) / 1024 / 1024
    print(f"✅ 海报生成成功！")
    print(f"   文件大小: {file_size:.2f} MB")
    return True


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="生成万里书院2026元旦海报")
    parser.add_argument("--api-key", default=None, help="青云API密钥")
    parser.add_argument("--output", default=None, help="输出文件路径")
    parser.add_argument("--fallback", action="store_true", help="直接使用设计版本，不调用API")

    args = parser.parse_args()

    print("=" * 70)
    print("🎨 万里书院2026元旦海报生成器")
    print("=" * 70)
    print()

    # 确定输出路径
    if args.output:
        output_path = Path(args.output)
    else:
        output_dir = Path("./posters")
        output_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"万里书院_2026元旦_专业版_{timestamp}.png"

    # 如果指定了fallback或没有API密钥，直接生成设计版
    if args.fallback or not args.api_key:
        if not args.api_key:
            print("ℹ️  未提供API密钥，将生成专业设计版海报\n")
        success = create_premium_design_poster(str(output_path))

        if success:
            print()
            print("=" * 70)
            print("🎉 海报生成成功！")
            print("=" * 70)
            print(f"\n📁 保存位置: {output_path}")
            print(f"📐 图像尺寸: 2048 x 1152 像素 (16:9)")
            print(f"🎨 设计风格: 专业级中国传统喜庆风格")
            print(f"🌈 配色方案: 中国红径向渐变 + 金色装饰")
            print(f"✨ 特色: 祥云、烟花、多层阴影、精美描边")
            print()
            print("💡 提示：")
            print("   - 这是专业级设计海报，可直接使用")
            print("   - 如需AI生成版本，请提供 --api-key 参数")
            print("   - 可在Photoshop等软件中进一步精修")
            print("=" * 70)
        return

    try:
        # 创建生成器
        generator = DoubaoPosterGenerator(api_key=args.api_key)

        # 精心设计的中文提示词（豆包模型支持准确渲染中文）
        prompt = """
创作一张精美的中国新年海报，主题"万里书院2026元旦快乐"：

【主体内容】
- 画面中央上方：优雅的中文书法"万里书院"（金色，大字）
- 画面中央下方：喜庆的"2026元旦快乐"（红色和金色）
- 背景：中国传统书院建筑，古色古香的飞檐翘角和雕花门窗

【装饰元素】
- 红灯笼挂在屋檐下，散发温暖的光芒
- 盛开的梅花枝条（红色和白色）
- 漫天烟花绽放，金色和红色交织
- 飘动的祥云图案（金色半透明）
- 中国传统窗花纹样

【配色方案】
- 主色调：中国红（#DC143C）和皇家金（#FFD700）
- 辅助色：深红、橙红、明黄
- 背景色：深红渐变到暗红
- 天空：傍晚的深蓝紫色，点缀金色星光

【视觉风格】
- 中国传统绘画美学与现代设计结合
- 电影级光影效果，暖色调氛围
- 构图庄重典雅又充满节日喜庆
- 高清细腻，色彩饱满鲜艳

【画面构图】
- 16:9横版海报
- 对称式构图，中轴线平衡
- 前景：梅花枝条和灯笼（虚化景深）
- 中景：书院建筑主体和文字
- 远景：烟花和祥云天空

【文字要求】
- "万里书院"四个大字：中国书法艺术字体，金色，带红色描边和阴影
- "2026元旦快乐"：喜庆字体，红色主体，金色描边
- 文字清晰可读，融入整体画面

【整体氛围】
盛大、喜庆、温馨、文化底蕴深厚，既有传统韵味又不失现代美感。

Chinese New Year poster for "Wanli Academy 2026 New Year": traditional Chinese academy architecture, red lanterns, plum blossoms, fireworks, golden clouds. Text "万里书院" and "2026元旦快乐" in Chinese calligraphy. Red and gold color scheme, cinematic lighting, 16:9 format, elegant and festive atmosphere.
"""

        # 确定输出路径
        if args.output:
            output_path = Path(args.output)
        else:
            output_dir = Path("./posters")
            output_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = output_dir / f"万里书院_2026元旦_AI_{timestamp}.png"

        # 生成海报
        success = generator.generate_poster(prompt, str(output_path))

        if success:
            print()
            print("=" * 70)
            print("🎉 海报生成成功！")
            print("=" * 70)
            print(f"\n📁 保存位置: {output_path}")
            print(f"📐 图像尺寸: 2048 x 1152 像素 (16:9)")
            print(f"🎨 生成模型: 豆包 doubao-seedream-4-0-250828")
            print(f"✨ 特点: 支持准确渲染中文汉字")
            print(f"🌈 设计风格: 中国传统+现代AI美学")
            print()
            print("💡 提示：")
            print("   - 这是AI生成的专业级海报")
            print("   - 如不满意可重新生成（每次效果不同）")
            print("   - 可在Photoshop等软件中进一步精修")
            print("=" * 70)
        else:
            print()
            print("=" * 70)
            print("❌ 生成失败，请检查：")
            print("   1. API密钥是否正确")
            print("   2. 账户余额是否充足")
            print("   3. 网络连接是否正常")
            print("=" * 70)

    except ValueError as e:
        print(f"\n❌ 错误: {e}")
        print()
        print("💡 使用方法：")
        print("   方法1: 设置环境变量")
        print("   export QINGYUN_API_KEY='sk-your-api-key'")
        print("   python3 generate_wanli_poster_doubao.py")
        print()
        print("   方法2: 使用命令行参数")
        print("   python3 generate_wanli_poster_doubao.py --api-key 'sk-your-api-key'")
        print()


if __name__ == "__main__":
    main()

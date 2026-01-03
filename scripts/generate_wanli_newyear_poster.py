#!/usr/bin/env python3
"""
万里书院2026元旦快乐海报生成器
使用 OpenAI DALL-E 3 生成高质量节日海报
如果无 API Key，将创建精美的设计模板海报
"""

import os
import requests
from pathlib import Path
from datetime import datetime


def create_design_poster():
    """创建设计精美的海报模板（无需API）"""
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageFilter
        import random
    except ImportError:
        print("❌ 需要安装 Pillow 库: pip install Pillow")
        return

    # 创建输出目录
    output_dir = Path("./posters")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"万里书院_2026元旦_{timestamp}.png"

    print("=" * 70)
    print("🎨 万里书院2026元旦海报生成器（设计模板）")
    print("=" * 70)

    # 创建 16:9 高清画布
    width, height = 1920, 1080

    # 创建渐变背景（中国红到金色）
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)

    # 绘制渐变背景
    for y in range(height):
        # 从深红到金红的渐变
        r = int(139 + (220 - 139) * (y / height))
        g = int(0 + (20 - 0) * (y / height))
        b = int(0 + (60 - 0) * (y / height))
        draw.rectangle([(0, y), (width, y+1)], fill=(r, g, b))

    # 添加一些装饰性图案
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)

    # 绘制祥云图案（圆形）
    for _ in range(20):
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.randint(50, 150)
        overlay_draw.ellipse(
            [(x, y), (x + size, y + size)],
            fill=(255, 215, 0, 30)  # 半透明金色
        )

    # 合并图层
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')

    # 添加光晕效果
    img = img.filter(ImageFilter.GaussianBlur(radius=2))

    draw = ImageDraw.Draw(img)

    # 加载字体（尝试多个中文字体）
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "C:\\Windows\\Fonts\\simhei.ttf",
        "C:\\Windows\\Fonts\\msyh.ttc",
    ]

    title_font = None
    subtitle_font = None
    year_font = None

    for font_path in font_paths:
        try:
            title_font = ImageFont.truetype(font_path, 120)
            subtitle_font = ImageFont.truetype(font_path, 80)
            year_font = ImageFont.truetype(font_path, 200)
            break
        except:
            continue

    if not title_font:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        year_font = ImageFont.load_default()

    # 绘制年份（大背景）
    year_text = "2026"
    year_bbox = draw.textbbox((0, 0), year_text, font=year_font)
    year_width = year_bbox[2] - year_bbox[0]
    year_height = year_bbox[3] - year_bbox[1]
    year_x = (width - year_width) // 2
    year_y = height - year_height - 100

    # 年份阴影
    for offset in range(5, 0, -1):
        shadow_alpha = int(255 * (1 - offset / 5))
        draw.text(
            (year_x + offset, year_y + offset),
            year_text,
            fill=(0, 0, 0, shadow_alpha),
            font=year_font
        )

    # 年份主体（金色）
    draw.text(
        (year_x, year_y),
        year_text,
        fill=(255, 215, 0),
        font=year_font
    )

    # 绘制主标题"万里书院"
    title_text = "万里书院"
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_height = title_bbox[3] - title_bbox[1]
    title_x = (width - title_width) // 2
    title_y = 200

    # 标题阴影
    draw.text(
        (title_x + 3, title_y + 3),
        title_text,
        fill=(0, 0, 0),
        font=title_font
    )

    # 标题主体（金色）
    draw.text(
        (title_x, title_y),
        title_text,
        fill=(255, 223, 0),
        font=title_font,
        stroke_width=2,
        stroke_fill=(139, 0, 0)
    )

    # 绘制副标题"元旦快乐"
    subtitle_text = "元旦快乐"
    subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (width - subtitle_width) // 2
    subtitle_y = title_y + title_height + 40

    # 副标题阴影
    draw.text(
        (subtitle_x + 2, subtitle_y + 2),
        subtitle_text,
        fill=(0, 0, 0),
        font=subtitle_font
    )

    # 副标题主体（白色带描边）
    draw.text(
        (subtitle_x, subtitle_y),
        subtitle_text,
        fill=(255, 255, 255),
        font=subtitle_font,
        stroke_width=2,
        stroke_fill=(255, 215, 0)
    )

    # 添加装饰线
    line_y = subtitle_y + subtitle_bbox[3] + 30
    line_length = 600
    line_x1 = (width - line_length) // 2
    line_x2 = line_x1 + line_length

    draw.line(
        [(line_x1, line_y), (line_x2, line_y)],
        fill=(255, 215, 0),
        width=3
    )

    # 添加小装饰圆点
    for i in range(5):
        circle_x = line_x1 + i * (line_length // 4)
        draw.ellipse(
            [(circle_x - 8, line_y - 8), (circle_x + 8, line_y + 8)],
            fill=(255, 223, 0)
        )

    # 保存图像
    img.save(output_path, quality=95, dpi=(300, 300))

    file_size = os.path.getsize(output_path) / 1024 / 1024

    print("\n✅ 海报生成成功！")
    print("=" * 70)
    print(f"\n📁 保存位置: {output_path}")
    print(f"📊 文件大小: {file_size:.2f} MB")
    print(f"📐 图像尺寸: {width} x {height} 像素 (16:9)")
    print(f"🎨 设计风格: 中国传统喜庆风格")
    print(f"🌈 配色方案: 中国红 + 金色")
    print("\n💡 提示：")
    print("   - 这是设计模板海报，已可直接使用")
    print("   - 如需AI生成版本，请配置 OPENAI_API_KEY")
    print("   - 可在图像编辑软件中进一步优化细节")
    print("=" * 70)


def generate_wanli_newyear_poster():
    """生成万里书院2026元旦海报"""

    # 检查 API Key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("ℹ️  未找到 OPENAI_API_KEY，将生成设计模板海报\n")
        create_design_poster()
        return

    # 精心设计的中文海报提示词
    prompt = """
创建一张精美的中国新年海报，主题为"万里书院2026元旦快乐"：

视觉元素：
- 中国传统书院建筑风格，古色古香的亭台楼阁
- 2026新年元素：红灯笼、梅花、烟花、祥云
- 金色和红色为主色调，象征喜庆和吉祥
- 书卷、毛笔等文化元素点缀

文字内容：
- 主标题："万里书院" （优雅的中文书法字体）
- 副标题："2026元旦快乐" （醒目的喜庆字体）
- 装饰性元素：传统中国纹样、祥云图案

整体风格：
- 中国传统艺术与现代设计相结合
- 庄重典雅又充满节日气氛
- 16:9 横版海报构图
- 高品质、富有文化底蕴

A beautiful Chinese New Year poster for "Wanli Academy 2026 New Year Celebration":
Traditional Chinese academy architecture with pavilions, red lanterns, plum blossoms, fireworks, and auspicious clouds. Gold and red color scheme. Chinese calligraphy showing "万里书院" and "2026元旦快乐". Elegant blend of traditional and modern design. 16:9 landscape format.
"""

    # 创建输出目录
    output_dir = Path("./posters")
    output_dir.mkdir(exist_ok=True)

    # 输出文件路径
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"万里书院_2026元旦_{timestamp}.png"

    print("=" * 70)
    print("🎨 万里书院2026元旦海报生成器")
    print("=" * 70)
    print(f"\n📝 生成提示词：")
    print(f"{prompt[:200]}...")
    print(f"\n⏳ 正在调用 DALL-E 3 生成海报...")
    print("   （这可能需要 20-60 秒，请耐心等待）\n")

    try:
        # DALL-E 3 API 调用
        url = "https://api.openai.com/v1/images/generations"
        headers = {
            "Authorization": f"Bearer {openai_api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": "1792x1024",  # 16:9 横版
            "quality": "hd",      # 高清质量
            "style": "vivid"      # 生动风格
        }

        # 发送请求
        response = requests.post(url, headers=headers, json=data, timeout=120)

        if response.status_code == 200:
            result = response.json()
            image_url = result['data'][0]['url']
            revised_prompt = result['data'][0].get('revised_prompt', '')

            print("✅ 图像生成成功！")
            if revised_prompt:
                print(f"\n📋 AI优化后的提示词：")
                print(f"{revised_prompt[:300]}...\n")

            # 下载图像
            print("⏳ 正在下载图像...")
            img_response = requests.get(image_url, timeout=60)

            if img_response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(img_response.content)

                file_size = len(img_response.content) / 1024 / 1024  # MB

                print("=" * 70)
                print("🎉 海报生成成功！")
                print("=" * 70)
                print(f"\n📁 保存位置: {output_path}")
                print(f"📊 文件大小: {file_size:.2f} MB")
                print(f"📐 图像尺寸: 1792 x 1024 像素 (16:9)")
                print(f"🎨 图像质量: HD (高清)")
                print("\n💡 提示：")
                print("   - 如果不满意，可以再次运行生成不同版本")
                print("   - 海报已保存在 ./posters/ 目录")
                print("   - 可以在任何图像编辑软件中进一步调整")
                print("=" * 70)

            else:
                print(f"❌ 下载失败: HTTP {img_response.status_code}")

        else:
            error_data = response.json()
            error_msg = error_data.get('error', {}).get('message', '未知错误')
            print(f"❌ 生成失败: {error_msg}")
            print(f"   状态码: {response.status_code}")

    except requests.exceptions.Timeout:
        print("❌ 请求超时，请检查网络连接后重试")
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")


def main():
    """主函数"""
    generate_wanli_newyear_poster()


if __name__ == "__main__":
    main()

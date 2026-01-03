#!/usr/bin/env python3
"""
分镜可视化脚本
创建简单的分镜板（Storyboard）可视化图
使用 Pillow 库绘制基本的分镜框架
"""

import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import textwrap


class StoryboardVisualizer:
    """分镜可视化工具"""

    def __init__(self, design_file: str):
        """初始化

        Args:
            design_file: 完整设计文档 JSON 文件路径
        """
        self.design_file = design_file
        self.data = self.load_design()

        # 画布尺寸（单个分镜框）
        self.frame_width = 1920 // 2  # 960px
        self.frame_height = 1080 // 2  # 540px

        # 尝试加载中文字体
        self.title_font = self.load_font(48)
        self.text_font = self.load_font(24)
        self.small_font = self.load_font(18)
        self.tiny_font = self.load_font(14)

    def load_font(self, size: int):
        """加载字体

        Args:
            size: 字体大小

        Returns:
            字体对象
        """
        # 常见中文字体路径
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",  # macOS
            "/System/Library/Fonts/STHeiti Medium.ttc",  # macOS
            "C:/Windows/Fonts/msyh.ttc",  # Windows
            "C:/Windows/Fonts/simhei.ttf",  # Windows
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",  # Linux
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",  # Linux
        ]

        for font_path in font_paths:
            try:
                return ImageFont.truetype(font_path, size)
            except:
                continue

        # 如果都失败，使用默认字体
        print(f"⚠️  无法加载中文字体，使用默认字体")
        return ImageFont.load_default()

    def load_design(self) -> dict:
        """加载设计数据"""
        with open(self.design_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def hex_to_rgb(self, hex_color: str) -> tuple:
        """将十六进制颜色转换为 RGB

        Args:
            hex_color: 十六进制颜色（如 #FFFFFF）

        Returns:
            RGB 元组
        """
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def draw_single_frame(self, scene: dict, scene_number: int) -> Image.Image:
        """绘制单个分镜框

        Args:
            scene: 场景数据
            scene_number: 场景编号

        Returns:
            分镜框图像
        """
        # 创建画布
        img = Image.new('RGB', (self.frame_width, self.frame_height), 'white')
        draw = ImageDraw.Draw(img)

        # 获取颜色方案
        storyboard = scene.get('storyboard_notes', {})
        color_palette = storyboard.get('color_palette', {})

        # 提取颜色
        try:
            if isinstance(color_palette, dict):
                primary_color = self.hex_to_rgb(color_palette.get('primary', '#2C2C2C'))
                secondary_color = self.hex_to_rgb(color_palette.get('secondary', '#CCCCCC'))
                accent_color = self.hex_to_rgb(color_palette.get('accent', '#8B0000'))
            else:
                primary_color = (44, 44, 44)
                secondary_color = (204, 204, 204)
                accent_color = (139, 0, 0)
        except:
            primary_color = (44, 44, 44)
            secondary_color = (204, 204, 204)
            accent_color = (139, 0, 0)

        # 绘制背景渐变效果（简化版）
        for y in range(self.frame_height):
            alpha = y / self.frame_height
            color = tuple(
                int(secondary_color[i] + (255 - secondary_color[i]) * (1 - alpha))
                for i in range(3)
            )
            draw.line([(0, y), (self.frame_width, y)], fill=color)

        # 绘制边框
        border_width = 8
        draw.rectangle(
            [(0, 0), (self.frame_width - 1, self.frame_height - 1)],
            outline=primary_color,
            width=border_width
        )

        # 顶部区域：场景编号和 ID
        header_height = 80
        draw.rectangle(
            [(border_width, border_width),
             (self.frame_width - border_width, header_height)],
            fill=accent_color
        )

        # 场景编号
        scene_id = scene.get('scene_id', 'Unknown')
        header_text = f"场景 {scene_number}: {scene_id}"
        draw.text(
            (self.frame_width // 2, header_height // 2),
            header_text,
            fill='white',
            font=self.text_font,
            anchor='mm'
        )

        # 主要内容区域
        content_y = header_height + 20

        # 时长标签
        duration = scene.get('duration', 0)
        duration_text = f"⏱ {duration}秒"
        draw.text(
            (20, content_y),
            duration_text,
            fill=accent_color,
            font=self.small_font
        )

        content_y += 40

        # 镜头类型
        shot_type = storyboard.get('shot_type', '')
        if shot_type:
            draw.text(
                (20, content_y),
                f"📸 {shot_type}",
                fill=primary_color,
                font=self.small_font
            )
            content_y += 35

        # 关键视觉元素
        visual_elements = storyboard.get('visual_elements', [])
        if visual_elements:
            draw.text(
                (20, content_y),
                "🎨 关键元素:",
                fill=primary_color,
                font=self.small_font
            )
            content_y += 30

            for i, element in enumerate(visual_elements[:4], 1):  # 最多显示4个
                # 文字换行
                wrapped = textwrap.fill(element, width=40)
                lines = wrapped.split('\n')
                for line in lines[:2]:  # 最多2行
                    draw.text(
                        (40, content_y),
                        f"• {line}",
                        fill=primary_color,
                        font=self.tiny_font
                    )
                    content_y += 22

        # 底部区域：旁白
        footer_y = self.frame_height - 150
        draw.rectangle(
            [(border_width, footer_y),
             (self.frame_width - border_width, self.frame_height - border_width)],
            fill=(245, 245, 245)
        )

        # 旁白文字
        narration = scene.get('narration', '')
        if narration:
            # 换行处理
            wrapped_narration = textwrap.fill(narration, width=50)
            lines = wrapped_narration.split('\n')

            narration_y = footer_y + 15
            draw.text(
                (20, narration_y),
                "💬 旁白:",
                fill=accent_color,
                font=self.small_font
            )
            narration_y += 30

            for line in lines[:3]:  # 最多3行
                draw.text(
                    (20, narration_y),
                    line,
                    fill=primary_color,
                    font=self.tiny_font
                )
                narration_y += 22

        return img

    def create_storyboard_grid(self, output_path: str, columns: int = 3):
        """创建分镜网格图

        Args:
            output_path: 输出文件路径
            columns: 每行列数
        """
        scenes = self.data.get('scenes', [])
        total_scenes = len(scenes)

        print(f"📊 创建分镜网格图...")
        print(f"   场景数量: {total_scenes}")
        print(f"   网格布局: {columns}列")

        # 计算行数
        rows = (total_scenes + columns - 1) // columns

        # 创建大画布
        canvas_width = self.frame_width * columns + 40
        canvas_height = self.frame_height * rows + 40
        canvas = Image.new('RGB', (canvas_width, canvas_height), 'white')

        # 添加标题
        draw = ImageDraw.Draw(canvas)
        project_name = self.data.get('project', {}).get('name', '分镜设计')
        draw.text(
            (canvas_width // 2, 20),
            project_name,
            fill=(0, 0, 0),
            font=self.title_font,
            anchor='mt'
        )

        # 绘制每个分镜框
        for i, scene in enumerate(scenes):
            print(f"   绘制场景 {i+1}/{total_scenes}: {scene.get('scene_id', 'Unknown')}")

            row = i // columns
            col = i % columns

            # 生成单个分镜框
            frame = self.draw_single_frame(scene, i + 1)

            # 粘贴到画布
            x = col * self.frame_width + 20
            y = row * self.frame_height + 60
            canvas.paste(frame, (x, y))

        # 保存
        canvas.save(output_path, quality=95)
        print(f"✅ 分镜网格图已保存: {output_path}")

    def create_individual_frames(self, output_dir: str):
        """创建单独的分镜框图片

        Args:
            output_dir: 输出目录
        """
        scenes = self.data.get('scenes', [])
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        print(f"🎨 创建单独分镜框...")

        for i, scene in enumerate(scenes, 1):
            scene_id = scene.get('scene_id', f'scene_{i}')
            print(f"   [{i}/{len(scenes)}] {scene_id}")

            frame = self.draw_single_frame(scene, i)
            frame_path = output_path / f"{scene_id}_frame.png"
            frame.save(frame_path, quality=95)

        print(f"✅ 单独分镜框已保存到: {output_dir}")

    def create_timeline_view(self, output_path: str):
        """创建时间轴视图

        Args:
            output_path: 输出文件路径
        """
        scenes = self.data.get('scenes', [])
        total_duration = sum(s.get('duration', 0) for s in scenes)

        print(f"⏱️ 创建时间轴视图...")
        print(f"   总时长: {total_duration}秒")

        # 时间轴尺寸
        timeline_width = 1920
        timeline_height = len(scenes) * 120 + 200

        canvas = Image.new('RGB', (timeline_width, timeline_height), 'white')
        draw = ImageDraw.Draw(canvas)

        # 标题
        draw.text(
            (timeline_width // 2, 30),
            "视频时间轴",
            fill=(0, 0, 0),
            font=self.title_font,
            anchor='mt'
        )

        # 时间刻度
        scale_y = 100
        draw.line([(100, scale_y), (timeline_width - 100, scale_y)],
                  fill=(100, 100, 100), width=2)

        # 绘制时间刻度标记
        for i in range(0, int(total_duration) + 1, 10):
            x = 100 + (i / total_duration) * (timeline_width - 200)
            draw.line([(x, scale_y - 10), (x, scale_y + 10)],
                     fill=(100, 100, 100), width=2)
            draw.text((x, scale_y + 20), f"{i}s",
                     fill=(100, 100, 100), font=self.tiny_font, anchor='mt')

        # 绘制场景条
        current_time = 0
        bar_y = 150

        for i, scene in enumerate(scenes):
            duration = scene.get('duration', 0)
            scene_id = scene.get('scene_id', f'Scene {i+1}')

            # 计算条形位置
            start_x = 100 + (current_time / total_duration) * (timeline_width - 200)
            end_x = 100 + ((current_time + duration) / total_duration) * (timeline_width - 200)
            bar_width = end_x - start_x

            # 颜色
            storyboard = scene.get('storyboard_notes', {})
            color_palette = storyboard.get('color_palette', {})
            try:
                if isinstance(color_palette, dict):
                    bar_color = self.hex_to_rgb(color_palette.get('accent', '#8B0000'))
                else:
                    bar_color = (139, 0, 0)
            except:
                bar_color = (139, 0, 0)

            # 绘制条形
            draw.rectangle(
                [(start_x, bar_y), (end_x, bar_y + 80)],
                fill=bar_color,
                outline=(0, 0, 0),
                width=2
            )

            # 场景信息
            draw.text(
                (start_x + 5, bar_y + 10),
                scene_id,
                fill='white',
                font=self.tiny_font
            )
            draw.text(
                (start_x + 5, bar_y + 35),
                f"{duration}秒",
                fill='white',
                font=self.tiny_font
            )

            # 旁白预览
            narration = scene.get('narration', '')[:20] + '...'
            draw.text(
                (start_x + 5, bar_y + 55),
                narration,
                fill='white',
                font=self.tiny_font
            )

            current_time += duration
            bar_y += 100

        canvas.save(output_path, quality=95)
        print(f"✅ 时间轴视图已保存: {output_path}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="分镜可视化工具")
    parser.add_argument(
        "--design",
        default="./storyboards/文脉薪传/complete_storyboard_design.json",
        help="设计文档 JSON 文件路径"
    )
    parser.add_argument(
        "--output-dir",
        default="./storyboards/文脉薪传/visualizations",
        help="输出目录"
    )

    args = parser.parse_args()

    # 创建输出目录
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 创建可视化工具
    visualizer = StoryboardVisualizer(args.design)

    print("🎬 分镜可视化工具")
    print("=" * 60)

    # 1. 创建分镜网格图
    grid_path = output_path / "storyboard_grid.png"
    visualizer.create_storyboard_grid(str(grid_path), columns=3)

    # 2. 创建单独分镜框
    frames_dir = output_path / "individual_frames"
    visualizer.create_individual_frames(str(frames_dir))

    # 3. 创建时间轴视图
    timeline_path = output_path / "timeline_view.png"
    visualizer.create_timeline_view(str(timeline_path))

    print("\n" + "=" * 60)
    print("✅ 可视化完成！")
    print("=" * 60)
    print(f"\n📁 输出文件:")
    print(f"   1. 分镜网格图: {grid_path}")
    print(f"   2. 单独分镜框: {frames_dir}/")
    print(f"   3. 时间轴视图: {timeline_path}")


if __name__ == "__main__":
    main()

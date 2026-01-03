#!/usr/bin/env python3
"""
分镜设计图生成脚本
使用 AI 图像生成服务创建分镜头设计参考图
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, List
import anthropic
import base64


class StoryboardImageGenerator:
    """分镜设计图生成器"""

    def __init__(self, api_key: str = None):
        """初始化生成器

        Args:
            api_key: Anthropic API Key，如不提供则从环境变量读取
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            self.client = None
            print("⚠️  未提供 API Key，将仅生成模板文档（不含AI设计建议）")

    def load_script(self, script_path: str) -> Dict:
        """加载细化后的脚本文件

        Args:
            script_path: 脚本文件路径

        Returns:
            脚本数据字典
        """
        with open(script_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def extract_image_prompts(self, script_data: Dict) -> List[Dict]:
        """提取所有场景的图像生成提示词

        Args:
            script_data: 脚本数据

        Returns:
            包含场景ID和提示词的列表
        """
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

    def generate_image_with_claude(self, prompt: str, scene_id: str) -> str:
        """使用 Claude 生成图像描述并返回建议

        注意：Claude API 目前不直接支持图像生成，
        此方法返回详细的视觉设计建议，可用于：
        1. 指导美术设计师
        2. 作为 DALL-E/Midjourney 等工具的输入
        3. 生成设计规范文档

        Args:
            prompt: 图像生成提示词
            scene_id: 场景ID

        Returns:
            详细的视觉设计建议（JSON格式）
        """
        system_prompt = """你是一位专业的视觉设计师和分镜师。
根据提供的场景描述，生成详细的分镜设计建议，包括：
1. 画面构图详细说明
2. 色彩方案和色调
3. 光线布局
4. 关键视觉元素位置
5. 镜头运动方式
6. 参考艺术风格

请以JSON格式返回设计建议。"""

        message = self.client.messages.create(
            model="claude-opus-4-5-20251101",
            max_tokens=2000,
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": f"""场景ID: {scene_id}

场景描述提示词:
{prompt}

请生成详细的分镜设计建议，以JSON格式返回，包含以下字段：
- composition: 构图说明
- color_scheme: 色彩方案（包含主色、辅色、强调色的十六进制值）
- lighting: 光线设计
- key_elements: 关键视觉元素及其位置
- camera_work: 镜头运动
- art_style: 艺术风格参考
- technical_specs: 技术规格（分辨率、景别、焦距等）
- mood: 情绪氛围
"""
            }]
        )

        return message.content[0].text

    def generate_all_storyboards(self, script_path: str, output_dir: str = "./storyboards"):
        """生成所有场景的分镜设计建议

        Args:
            script_path: 脚本文件路径
            output_dir: 输出目录
        """
        # 加载脚本
        print(f"📖 加载脚本: {script_path}")
        script_data = self.load_script(script_path)

        # 提取场景
        scenes = self.extract_image_prompts(script_data)
        print(f"✅ 找到 {len(scenes)} 个场景")

        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 生成设计建议
        all_designs = []

        for i, scene in enumerate(scenes, 1):
            print(f"\n🎨 [{i}/{len(scenes)}] 生成场景设计: {scene['id']}")
            print(f"   时长: {scene['duration']}秒")
            print(f"   旁白: {scene['narration'][:50]}...")

            try:
                # 生成设计建议
                if self.client:
                    design_json = self.generate_image_with_claude(
                        scene['prompt'],
                        scene['id']
                    )

                    # 解析 JSON
                    try:
                        design_data = json.loads(design_json)
                    except json.JSONDecodeError:
                        # 如果不是标准JSON，保存原始文本
                        design_data = {"raw_design": design_json}
                else:
                    # 没有 API Key，使用模板
                    design_data = {
                        "note": "此为模板文档，需要 API Key 生成完整AI设计建议"
                    }

                # 添加原始场景信息
                design_data['scene_id'] = scene['id']
                design_data['original_prompt'] = scene['prompt']
                design_data['narration'] = scene['narration']
                design_data['duration'] = scene['duration']
                design_data['storyboard_notes'] = scene['storyboard']

                all_designs.append(design_data)

                # 保存单个场景设计
                scene_file = output_path / f"{scene['id']}_design.json"
                with open(scene_file, 'w', encoding='utf-8') as f:
                    json.dump(design_data, f, ensure_ascii=False, indent=2)

                print(f"   ✅ 设计已保存: {scene_file}")

            except Exception as e:
                print(f"   ❌ 生成失败: {str(e)}")
                continue

        # 保存完整设计文档
        complete_file = output_path / "complete_storyboard_design.json"
        with open(complete_file, 'w', encoding='utf-8') as f:
            json.dump({
                'project': script_data.get('project', {}),
                'total_scenes': len(scenes),
                'scenes': all_designs
            }, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 完整设计文档已保存: {complete_file}")

        # 生成 Markdown 设计文档
        self.generate_markdown_doc(all_designs, script_data, output_path)

    def generate_markdown_doc(self, designs: List[Dict], script_data: Dict, output_path: Path):
        """生成 Markdown 格式的设计文档

        Args:
            designs: 设计数据列表
            script_data: 原始脚本数据
            output_path: 输出路径
        """
        md_file = output_path / "分镜设计文档.md"

        with open(md_file, 'w', encoding='utf-8') as f:
            # 标题
            project_name = script_data.get('project', {}).get('name', '视频项目')
            f.write(f"# {project_name} - 分镜设计文档\n\n")

            # 项目信息
            f.write("## 项目信息\n\n")
            project = script_data.get('project', {})
            f.write(f"- **分辨率**: {project.get('resolution', 'N/A')}\n")
            f.write(f"- **帧率**: {project.get('fps', 'N/A')} FPS\n")
            f.write(f"- **配音**: {project.get('voice', 'N/A')}\n")
            f.write(f"- **码率**: {project.get('bitrate', 'N/A')}\n")
            f.write(f"- **场景数量**: {len(designs)}\n\n")

            # 制作说明
            if 'production_notes' in script_data:
                f.write("## 制作说明\n\n")
                notes = script_data['production_notes']
                for key, value in notes.items():
                    f.write(f"### {key}\n\n")
                    if isinstance(value, dict):
                        for k, v in value.items():
                            f.write(f"- **{k}**: {v}\n")
                    elif isinstance(value, list):
                        for item in value:
                            f.write(f"- {item}\n")
                    else:
                        f.write(f"{value}\n")
                    f.write("\n")

            # 分镜详情
            f.write("## 分镜详细设计\n\n")

            for i, design in enumerate(designs, 1):
                scene_id = design.get('scene_id', f'Scene {i}')
                f.write(f"### {i}. {scene_id}\n\n")

                # 基本信息
                f.write(f"**时长**: {design.get('duration', 'N/A')}秒\n\n")
                f.write(f"**旁白**:\n> {design.get('narration', 'N/A')}\n\n")

                # 分镜笔记
                if 'storyboard_notes' in design and design['storyboard_notes']:
                    f.write("#### 分镜笔记\n\n")
                    notes = design['storyboard_notes']
                    for key, value in notes.items():
                        if isinstance(value, list):
                            f.write(f"- **{key}**:\n")
                            for item in value:
                                f.write(f"  - {item}\n")
                        else:
                            f.write(f"- **{key}**: {value}\n")
                    f.write("\n")

                # AI 设计建议
                if 'composition' in design:
                    f.write("#### AI 设计建议\n\n")

                    if 'composition' in design:
                        f.write(f"**构图**: {design['composition']}\n\n")

                    if 'color_scheme' in design:
                        f.write("**色彩方案**:\n")
                        if isinstance(design['color_scheme'], dict):
                            for color_type, color_value in design['color_scheme'].items():
                                f.write(f"- {color_type}: {color_value}\n")
                        else:
                            f.write(f"{design['color_scheme']}\n")
                        f.write("\n")

                    if 'lighting' in design:
                        f.write(f"**光线设计**: {design['lighting']}\n\n")

                    if 'key_elements' in design:
                        f.write("**关键元素**:\n")
                        if isinstance(design['key_elements'], list):
                            for elem in design['key_elements']:
                                f.write(f"- {elem}\n")
                        else:
                            f.write(f"{design['key_elements']}\n")
                        f.write("\n")

                    if 'camera_work' in design:
                        f.write(f"**镜头运动**: {design['camera_work']}\n\n")

                    if 'art_style' in design:
                        f.write(f"**艺术风格**: {design['art_style']}\n\n")

                    if 'mood' in design:
                        f.write(f"**情绪氛围**: {design['mood']}\n\n")

                # 原始提示词
                f.write("#### 图像生成提示词\n\n")
                f.write("```\n")
                f.write(design.get('original_prompt', 'N/A'))
                f.write("\n```\n\n")

                # 占位图片区域
                f.write("#### 设计图\n\n")
                f.write(f"![{scene_id}](./{scene_id}_design.png)\n\n")
                f.write("*使用上述提示词通过 Midjourney/DALL-E/Stable Diffusion 生成设计图*\n\n")

                f.write("---\n\n")

        print(f"📄 Markdown 文档已生成: {md_file}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="生成分镜设计图和文档")
    parser.add_argument(
        "--script",
        default="./文脉薪传_细化脚本.yaml",
        help="细化脚本文件路径"
    )
    parser.add_argument(
        "--output",
        default="./storyboards",
        help="输出目录"
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="Anthropic API Key（可选，默认从环境变量读取）"
    )

    args = parser.parse_args()

    # 创建生成器
    generator = StoryboardImageGenerator(api_key=args.api_key)

    # 生成分镜设计
    generator.generate_all_storyboards(args.script, args.output)

    print("\n" + "="*60)
    print("✅ 分镜设计生成完成！")
    print("="*60)
    print("\n📁 输出内容：")
    print("  1. 各场景设计 JSON 文件")
    print("  2. 完整设计文档 JSON")
    print("  3. Markdown 格式设计文档")
    print("\n💡 后续步骤：")
    print("  1. 查看 Markdown 文档了解详细设计")
    print("  2. 使用提示词在 Midjourney/DALL-E 生成设计图")
    print("  3. 将生成的图片保存到 storyboards 目录")
    print("  4. 根据设计图进行视频制作")


if __name__ == "__main__":
    main()

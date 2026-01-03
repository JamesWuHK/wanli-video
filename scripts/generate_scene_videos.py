#!/usr/bin/env python3
"""
为每个分镜生成视频
每个分镜视频包含：
1. 从上个分镜的最后一帧过渡到当前分镜的开始帧
2. 从开始帧过渡到关键帧
3. 从关键帧过渡到下一个分镜的开始帧
"""

import os
import yaml
import subprocess
from pathlib import Path
from typing import List, Dict


class SceneVideoGenerator:
    """分镜视频生成器"""

    def __init__(self, script_path: str, image_dir: str, keyframe_dir: str, output_dir: str):
        """初始化"""
        self.script_path = script_path
        self.image_dir = Path(image_dir)
        self.keyframe_dir = Path(keyframe_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 加载脚本
        with open(script_path, 'r', encoding='utf-8') as f:
            self.script_data = yaml.safe_load(f)

        self.scenes = self.script_data.get('scenes', [])
        print(f"✅ 加载了 {len(self.scenes)} 个场景")

    def create_transition_video(
        self,
        img1_path: str,
        img2_path: str,
        output_path: str,
        duration: float = 1.0,
        transition_type: str = "fade"
    ):
        """创建两张图片之间的过渡视频"""

        if transition_type == "fade":
            # 淡入淡出过渡
            filter_complex = (
                f"[0:v]fade=t=out:st={duration-0.5}:d=0.5[v0];"
                f"[1:v]fade=t=in:st=0:d=0.5[v1];"
                f"[v0][v1]xfade=transition=fade:duration=0.5:offset={duration-0.5}"
            )
        elif transition_type == "slide":
            # 滑动过渡
            filter_complex = (
                f"[0:v][1:v]xfade=transition=slideleft:duration=0.8:offset={duration-0.8}"
            )
        elif transition_type == "zoom":
            # 缩放过渡
            filter_complex = (
                f"[0:v]scale=2048:1152,zoompan=z='min(zoom+0.0015,1.5)':d={int(duration*30)}:s=2048x1152[v0];"
                f"[1:v]fade=t=in:st=0:d=0.5[v1];"
                f"[v0][v1]blend=all_expr='A*(if(gte(T,{duration-0.5}),1-2*(T-{duration-0.5}),1))+B*(if(gte(T,{duration-0.5}),2*(T-{duration-0.5}),0))'"
            )
        else:
            # 默认淡入淡出
            filter_complex = f"[0:v][1:v]xfade=transition=fade:duration=0.5:offset={duration-0.5}"

        cmd = [
            'ffmpeg', '-y',
            '-loop', '1', '-t', str(duration), '-i', img1_path,
            '-loop', '1', '-t', str(duration), '-i', img2_path,
            '-filter_complex', filter_complex,
            '-t', str(duration * 2 - 0.5),
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-r', '30',
            output_path
        ]

        subprocess.run(cmd, check=True, capture_output=True)

    def create_scene_video(self, scene_index: int):
        """为单个场景创建视频"""
        scene = self.scenes[scene_index]
        scene_id = scene['id']
        duration = scene['duration']

        print(f"\n🎬 生成场景 {scene_index + 1}/{len(self.scenes)}: {scene_id}")
        print(f"   时长: {duration}秒")

        # 图片路径
        start_frame = self.image_dir / f"{scene_id}.png"
        keyframe = self.keyframe_dir / f"{scene_id}_keyframe.png"

        # 检查文件是否存在
        if not start_frame.exists():
            raise FileNotFoundError(f"开始帧不存在: {start_frame}")
        if not keyframe.exists():
            raise FileNotFoundError(f"关键帧不存在: {keyframe}")

        # 获取前后场景的图片
        prev_scene_id = self.scenes[scene_index - 1]['id'] if scene_index > 0 else None
        next_scene_id = self.scenes[scene_index + 1]['id'] if scene_index < len(self.scenes) - 1 else None

        prev_frame = self.keyframe_dir / f"{prev_scene_id}_keyframe.png" if prev_scene_id else start_frame
        next_frame = self.image_dir / f"{next_scene_id}.png" if next_scene_id else keyframe

        if not prev_frame.exists():
            prev_frame = start_frame
        if not next_frame.exists():
            next_frame = keyframe

        # 计算各部分时长（均匀分配）
        segment_duration = duration / 3

        # 临时视频文件
        temp_dir = self.output_dir / "temp"
        temp_dir.mkdir(exist_ok=True)

        segment1 = temp_dir / f"{scene_id}_seg1.mp4"
        segment2 = temp_dir / f"{scene_id}_seg2.mp4"
        segment3 = temp_dir / f"{scene_id}_seg3.mp4"

        print(f"   📝 片段1: {prev_frame.name} → {start_frame.name}")
        self.create_transition_video(
            str(prev_frame),
            str(start_frame),
            str(segment1),
            duration=segment_duration,
            transition_type="fade"
        )

        print(f"   📝 片段2: {start_frame.name} → {keyframe.name}")
        self.create_transition_video(
            str(start_frame),
            str(keyframe),
            str(segment2),
            duration=segment_duration,
            transition_type="zoom"
        )

        print(f"   📝 片段3: {keyframe.name} → {next_frame.name}")
        self.create_transition_video(
            str(keyframe),
            str(next_frame),
            str(segment3),
            duration=segment_duration,
            transition_type="fade"
        )

        # 合并三个片段
        concat_file = temp_dir / f"{scene_id}_concat.txt"
        with open(concat_file, 'w') as f:
            f.write(f"file '{segment1.absolute()}'\n")
            f.write(f"file '{segment2.absolute()}'\n")
            f.write(f"file '{segment3.absolute()}'\n")

        output_video = self.output_dir / f"{scene_id}.mp4"

        print(f"   🎞️  合并视频片段...")
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_file),
            '-c', 'copy',
            str(output_video)
        ]
        subprocess.run(cmd, check=True, capture_output=True)

        # 清理临时文件
        segment1.unlink(missing_ok=True)
        segment2.unlink(missing_ok=True)
        segment3.unlink(missing_ok=True)
        concat_file.unlink(missing_ok=True)

        print(f"   ✅ 完成: {output_video.name}")

    def generate_all_videos(self):
        """生成所有场景视频"""
        print("=" * 60)
        print("🎬 开始生成所有分镜视频")
        print("=" * 60)

        success_count = 0
        failed_scenes = []

        for i in range(len(self.scenes)):
            try:
                self.create_scene_video(i)
                success_count += 1
            except Exception as e:
                scene_id = self.scenes[i]['id']
                print(f"   ❌ 失败: {str(e)}")
                failed_scenes.append(scene_id)

        print("\n" + "=" * 60)
        print(f"✅ 完成！成功生成 {success_count}/{len(self.scenes)} 个视频")

        if failed_scenes:
            print(f"\n⚠️  失败场景：")
            for sid in failed_scenes:
                print(f"   - {sid}")

        print(f"\n📁 输出目录: {self.output_dir}")
        print("=" * 60)


def main():
    """主函数"""
    generator = SceneVideoGenerator(
        script_path='./文脉薪传_细化脚本.yaml',
        image_dir='./storyboards/文脉薪传/doubao_images',
        keyframe_dir='./storyboards/文脉薪传/keyframes',
        output_dir='./storyboards/文脉薪传/scene_videos'
    )

    generator.generate_all_videos()


if __name__ == "__main__":
    main()

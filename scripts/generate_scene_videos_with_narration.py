#!/usr/bin/env python3
"""
为每个分镜生成完整视频
包含：过渡动画 + 字幕 + 画外音解说
"""

import os
import yaml
import subprocess
import asyncio
from pathlib import Path
from typing import List, Dict
import edge_tts


class SceneVideoGenerator:
    """完整分镜视频生成器"""

    def __init__(self, script_path: str, image_dir: str, keyframe_dir: str, output_dir: str):
        """初始化"""
        self.script_path = script_path
        self.image_dir = Path(image_dir)
        self.keyframe_dir = Path(keyframe_dir)
        self.output_dir = Path(output_dir)
        self.audio_dir = self.output_dir / "audio"
        self.temp_dir = self.output_dir / "temp"

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # 加载脚本
        with open(script_path, 'r', encoding='utf-8') as f:
            self.script_data = yaml.safe_load(f)

        self.scenes = self.script_data.get('scenes', [])
        self.voice = self.script_data.get('project', {}).get('voice', 'zh-CN-YunxiNeural')

        print(f"✅ 加载了 {len(self.scenes)} 个场景")
        print(f"🎙️  使用语音: {self.voice}")

    async def generate_narration_audio(self, scene_id: str, narration: str) -> Path:
        """生成画外音音频"""
        audio_path = self.audio_dir / f"{scene_id}.mp3"

        if audio_path.exists():
            print(f"   ⏭️  音频已存在，跳过")
            return audio_path

        print(f"   🎙️  生成画外音...")

        communicate = edge_tts.Communicate(narration, self.voice)
        await communicate.save(str(audio_path))

        return audio_path

    def get_audio_duration(self, audio_path: Path) -> float:
        """获取音频时长"""
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            str(audio_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())

    def create_image_video_with_subtitle(
        self,
        image_path: Path,
        duration: float,
        subtitle_text: str,
        output_path: Path
    ):
        """从图片创建带字幕的视频片段"""

        # 字幕样式设置
        fontfile = '/System/Library/Fonts/PingFang.ttc'  # macOS中文字体
        fontsize = 32
        fontcolor = 'white'
        box = 1
        boxcolor = 'black@0.5'

        # 转义字幕文本中的特殊字符
        subtitle_escaped = subtitle_text.replace("'", "'\\''").replace(":", "\\:")

        filter_complex = (
            f"[0:v]scale=2048:1152,fps=30,"
            f"drawtext=text='{subtitle_escaped}':"
            f"fontfile='{fontfile}':"
            f"fontsize={fontsize}:"
            f"fontcolor={fontcolor}:"
            f"box={box}:"
            f"boxcolor={boxcolor}:"
            f"x=(w-text_w)/2:"
            f"y=h-100"
        )

        cmd = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', str(image_path),
            '-filter_complex', filter_complex,
            '-t', str(duration),
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-r', '30',
            str(output_path)
        ]

        subprocess.run(cmd, check=True, capture_output=True)

    def create_transition_video(
        self,
        img1_path: Path,
        img2_path: Path,
        duration: float,
        output_path: Path,
        transition_type: str = "fade"
    ):
        """创建过渡视频"""

        cmd = [
            'ffmpeg', '-y',
            '-loop', '1', '-t', str(duration), '-i', str(img1_path),
            '-loop', '1', '-t', str(duration), '-i', str(img2_path),
            '-filter_complex',
            f"[0:v][1:v]xfade=transition={transition_type}:duration=0.5:offset={duration-0.5}",
            '-t', str(duration * 2 - 0.5),
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-r', '30',
            str(output_path)
        ]

        subprocess.run(cmd, check=True, capture_output=True)

    def merge_video_audio(self, video_path: Path, audio_path: Path, output_path: Path):
        """合并视频和音频"""
        cmd = [
            'ffmpeg', '-y',
            '-i', str(video_path),
            '-i', str(audio_path),
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-shortest',
            str(output_path)
        ]
        subprocess.run(cmd, check=True, capture_output=True)

    async def create_scene_video(self, scene_index: int):
        """为单个场景创建完整视频"""
        scene = self.scenes[scene_index]
        scene_id = scene['id']
        duration = scene['duration']
        narration = scene['narration']

        print(f"\n🎬 场景 {scene_index + 1}/{len(self.scenes)}: {scene_id}")
        print(f"   ⏱️  时长: {duration}秒")
        print(f"   📝 旁白: {narration[:50]}...")

        # 1. 生成画外音
        audio_path = await self.generate_narration_audio(scene_id, narration)
        audio_duration = self.get_audio_duration(audio_path)

        # 使用音频时长作为实际视频时长（确保时间轴匹配）
        actual_duration = max(duration, audio_duration + 0.5)

        print(f"   🎙️  音频时长: {audio_duration:.2f}秒")
        print(f"   📹 实际视频时长: {actual_duration:.2f}秒")

        # 图片路径
        start_frame = self.image_dir / f"{scene_id}.png"
        keyframe = self.keyframe_dir / f"{scene_id}_keyframe.png"

        if not start_frame.exists() or not keyframe.exists():
            raise FileNotFoundError(f"图片不存在: {scene_id}")

        # 2. 创建带字幕的视频片段
        segment_duration = actual_duration / 2  # 均分为开始帧和关键帧两部分

        seg1_path = self.temp_dir / f"{scene_id}_seg1_subtitle.mp4"
        seg2_path = self.temp_dir / f"{scene_id}_seg2_subtitle.mp4"

        print(f"   🎨 创建开始帧视频（带字幕）...")
        self.create_image_video_with_subtitle(
            start_frame,
            segment_duration,
            narration,
            seg1_path
        )

        print(f"   🎨 创建关键帧视频（带字幕）...")
        self.create_image_video_with_subtitle(
            keyframe,
            segment_duration,
            narration,
            seg2_path
        )

        # 3. 创建过渡效果（开始帧到关键帧）
        print(f"   🔀 添加过渡效果...")
        transition_path = self.temp_dir / f"{scene_id}_transition.mp4"

        cmd = [
            'ffmpeg', '-y',
            '-i', str(seg1_path),
            '-i', str(seg2_path),
            '-filter_complex',
            '[0:v][1:v]xfade=transition=fade:duration=1:offset=' + str(segment_duration - 1),
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-r', '30',
            str(transition_path)
        ]
        subprocess.run(cmd, check=True, capture_output=True)

        # 4. 合并视频和音频
        output_video = self.output_dir / f"{scene_id}.mp4"

        print(f"   🎵 合并视频和音频...")
        self.merge_video_audio(transition_path, audio_path, output_video)

        # 清理临时文件
        seg1_path.unlink(missing_ok=True)
        seg2_path.unlink(missing_ok=True)
        transition_path.unlink(missing_ok=True)

        print(f"   ✅ 完成: {output_video.name}")
        return output_video

    async def generate_all_videos(self):
        """生成所有场景视频"""
        print("=" * 60)
        print("🎬 开始生成所有分镜视频（带画外音和字幕）")
        print("=" * 60)

        success_count = 0
        failed_scenes = []

        for i in range(len(self.scenes)):
            try:
                await self.create_scene_video(i)
                success_count += 1
            except Exception as e:
                scene_id = self.scenes[i]['id']
                print(f"   ❌ 失败: {str(e)}")
                failed_scenes.append((scene_id, str(e)))

        print("\n" + "=" * 60)
        print(f"✅ 完成！成功生成 {success_count}/{len(self.scenes)} 个视频")

        if failed_scenes:
            print(f"\n⚠️  失败场景：")
            for sid, error in failed_scenes:
                print(f"   - {sid}: {error[:50]}")

        print(f"\n📁 输出目录: {self.output_dir}")
        print("=" * 60)


async def main():
    """主函数"""
    generator = SceneVideoGenerator(
        script_path='./文脉薪传_细化脚本.yaml',
        image_dir='./storyboards/文脉薪传/doubao_images',
        keyframe_dir='./storyboards/文脉薪传/keyframes',
        output_dir='./storyboards/文脉薪传/scene_videos'
    )

    await generator.generate_all_videos()


if __name__ == "__main__":
    asyncio.run(main())

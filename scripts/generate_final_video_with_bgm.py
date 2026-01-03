#!/usr/bin/env python3
"""
重新生成最终视频，修复字幕显示问题并添加背景音乐
"""

import os
import yaml
import subprocess
import asyncio
from pathlib import Path
import edge_tts


class FinalVideoGenerator:
    """最终视频生成器 - 修复字幕 + 添加BGM"""

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

    async def generate_narration_audio(self, scene_id: str, narration: str) -> Path:
        """生成画外音音频"""
        audio_path = self.audio_dir / f"{scene_id}.mp3"

        if audio_path.exists():
            return audio_path

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

    def create_subtitle_file(self, scene_id: str, narration: str, duration: float) -> Path:
        """创建SRT字幕文件"""
        subtitle_path = self.temp_dir / f"{scene_id}.srt"

        # 创建SRT格式字幕
        with open(subtitle_path, 'w', encoding='utf-8') as f:
            f.write("1\n")
            f.write(f"00:00:00,000 --> 00:00:{int(duration):02d},{int((duration % 1) * 1000):03d}\n")
            f.write(f"{narration}\n")

        return subtitle_path

    def create_scene_video_with_subtitle(
        self,
        start_frame: Path,
        keyframe: Path,
        audio_path: Path,
        subtitle_path: Path,
        duration: float,
        output_path: Path
    ):
        """创建带字幕的场景视频"""

        # 字幕样式：使用subtitles滤镜
        # 优化字幕显示 - 无阴影、更透明、更小、更靠下
        # PrimaryColour: &HB3FFFFFF (30%透明的白色)
        # BackColour: &H00000000 (完全透明背景)
        # MarginV: 30 (距离底部更近，值越小越靠下)
        # FontSize: 20 (更小字体)
        # Shadow: 0 (无阴影)
        filter_complex = (
            # 输入1: 开始帧，显示一半时长
            f"[0:v]scale=2048:1152,fps=30,trim=duration={duration/2}[v0];"
            # 输入2: 关键帧，显示一半时长
            f"[1:v]scale=2048:1152,fps=30,trim=duration={duration/2}[v1];"
            # 淡入淡出过渡
            f"[v0][v1]xfade=transition=fade:duration=1:offset={duration/2-1}[v];"
            # 添加字幕 - 优化样式（无阴影、更透明）
            f"[v]subtitles='{subtitle_path}':force_style='FontName=PingFang SC,FontSize=20,PrimaryColour=&HB3FFFFFF,OutlineColour=&H000000,BackColour=&H00000000,Bold=0,Outline=1,Shadow=0,MarginV=30,Alignment=2'[vout]"
        )

        cmd = [
            'ffmpeg', '-y',
            '-loop', '1', '-t', str(duration), '-i', str(start_frame),
            '-loop', '1', '-t', str(duration), '-i', str(keyframe),
            '-i', str(audio_path),
            '-filter_complex', filter_complex,
            '-map', '[vout]',
            '-map', '2:a',
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-pix_fmt', 'yuv420p',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-shortest',
            str(output_path)
        ]

        subprocess.run(cmd, check=True, capture_output=True)

    async def create_scene_video(self, scene_index: int):
        """创建单个场景视频"""
        scene = self.scenes[scene_index]
        scene_id = scene['id']
        duration = scene['duration']
        narration = scene['narration']

        print(f"\n🎬 场景 {scene_index + 1}/{len(self.scenes)}: {scene_id}")

        # 1. 生成或获取画外音
        audio_path = await self.generate_narration_audio(scene_id, narration)
        audio_duration = self.get_audio_duration(audio_path)

        # 使用音频时长作为实际视频时长
        actual_duration = max(duration, audio_duration + 0.5)

        print(f"   🎙️  音频: {audio_duration:.2f}秒")
        print(f"   📹 视频: {actual_duration:.2f}秒")

        # 2. 创建字幕文件
        subtitle_path = self.create_subtitle_file(scene_id, narration, actual_duration)

        # 3. 获取图片
        start_frame = self.image_dir / f"{scene_id}.png"
        keyframe = self.keyframe_dir / f"{scene_id}_keyframe.png"

        if not start_frame.exists() or not keyframe.exists():
            raise FileNotFoundError(f"图片不存在: {scene_id}")

        # 4. 生成视频
        output_video = self.output_dir / f"{scene_id}.mp4"

        print(f"   🎨 生成视频（带字幕）...")
        self.create_scene_video_with_subtitle(
            start_frame,
            keyframe,
            audio_path,
            subtitle_path,
            actual_duration,
            output_video
        )

        print(f"   ✅ 完成: {output_video.name}")
        return output_video

    async def generate_all_scene_videos(self):
        """生成所有场景视频"""
        print("=" * 60)
        print("🎬 重新生成所有场景视频（修复字幕）")
        print("=" * 60)

        scene_videos = []
        for i in range(len(self.scenes)):
            try:
                video_path = await self.create_scene_video(i)
                scene_videos.append(video_path)
            except Exception as e:
                print(f"   ❌ 失败: {str(e)}")

        return scene_videos

    def merge_with_bgm(self, scene_videos: list, bgm_path: str, output_path: str):
        """合并视频并添加背景音乐"""
        print("\n" + "=" * 60)
        print("🎵 合并视频并添加背景音乐")
        print("=" * 60)

        # 1. 创建concat文件
        concat_file = self.temp_dir / "concat_list.txt"
        with open(concat_file, 'w') as f:
            for video in scene_videos:
                f.write(f"file '{video.absolute()}'\n")

        # 2. 先合并所有视频
        merged_video = self.temp_dir / "merged_no_bgm.mp4"

        print("\n📹 合并所有场景视频...")
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_file),
            '-c', 'copy',
            str(merged_video)
        ]
        subprocess.run(cmd, check=True, capture_output=True)

        # 3. 获取视频时长
        duration = self.get_audio_duration(merged_video)
        print(f"   总时长: {duration:.2f}秒")

        # 4. 添加背景音乐
        if bgm_path and Path(bgm_path).exists():
            print(f"\n🎵 添加背景音乐: {bgm_path}")

            # 混合原音和背景音乐（背景音乐音量降低）
            cmd = [
                'ffmpeg', '-y',
                '-i', str(merged_video),
                '-stream_loop', '-1',  # 循环播放BGM
                '-i', bgm_path,
                '-filter_complex',
                '[0:a]volume=1.0[a0];[1:a]volume=0.15[a1];[a0][a1]amix=inputs=2:duration=first[aout]',
                '-map', '0:v',
                '-map', '[aout]',
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-b:a', '192k',
                '-shortest',
                str(output_path)
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"   ✅ 完成！BGM已添加")
        else:
            print("\n⚠️  未提供BGM文件，仅合并视频")
            import shutil
            shutil.copy(merged_video, output_path)

        # 清理临时文件
        merged_video.unlink(missing_ok=True)
        concat_file.unlink()

        print(f"\n📁 输出: {output_path}")
        print("=" * 60)


async def main():
    """主函数"""

    generator = FinalVideoGenerator(
        script_path='./文脉薪传_细化脚本.yaml',
        image_dir='./storyboards/文脉薪传/doubao_images',
        keyframe_dir='./storyboards/文脉薪传/keyframes',
        output_dir='./storyboards/文脉薪传/final_videos'
    )

    # 1. 生成所有场景视频
    scene_videos = await generator.generate_all_scene_videos()

    # 2. 合并并添加BGM
    # 注意：需要准备一个BGM文件，或者设置为None
    bgm_path = None  # 如果有BGM文件，设置路径，例如：'./bgm/traditional_chinese.mp3'

    output_path = './storyboards/文脉薪传/文脉薪传_完整版_带BGM.mp4'

    generator.merge_with_bgm(scene_videos, bgm_path, output_path)

    print("\n✅ 全部完成！")
    print(f"📹 最终视频: {output_path}")


if __name__ == "__main__":
    asyncio.run(main())

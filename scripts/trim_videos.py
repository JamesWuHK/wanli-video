#!/usr/bin/env python3
"""
视频裁剪工具
裁剪视频，只保留前面指定秒数的内容
"""

import subprocess
from pathlib import Path


def trim_video(input_path, output_path, duration_seconds):
    """
    裁剪视频，只保留前 N 秒

    Args:
        input_path: 输入视频路径
        output_path: 输出视频路径
        duration_seconds: 保留的时长（秒）
    """
    input_file = Path(input_path)
    output_file = Path(output_path)

    if not input_file.exists():
        print(f"❌ 错误: 输入文件不存在: {input_path}")
        return False

    # 确保输出目录存在
    output_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*80}")
    print(f"裁剪视频")
    print(f"{'='*80}")
    print(f"📹 输入: {input_path}")
    print(f"💾 输出: {output_path}")
    print(f"⏱️  保留时长: {duration_seconds} 秒")

    # 使用 ffmpeg 裁剪视频
    # -i: 输入文件
    # -t: 持续时间
    # -c copy: 直接复制编码，不重新编码（快速）
    # -avoid_negative_ts 1: 避免负时间戳
    cmd = [
        'ffmpeg',
        '-i', str(input_file),
        '-t', str(duration_seconds),
        '-c', 'copy',
        '-avoid_negative_ts', '1',
        '-y',  # 覆盖输出文件
        str(output_file)
    ]

    try:
        print(f"\n🚀 开始裁剪...")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        # 检查输出文件
        if output_file.exists():
            file_size = output_file.stat().st_size / (1024 * 1024)  # MB
            print(f"✅ 裁剪成功!")
            print(f"📦 文件大小: {file_size:.2f} MB")
            return True
        else:
            print(f"❌ 裁剪失败: 输出文件未生成")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ ffmpeg 错误:")
        print(e.stderr)
        return False
    except Exception as e:
        print(f"❌ 裁剪失败: {e}")
        return False


def main():
    print("="*80)
    print("视频裁剪工具 - 保留视频前 N 秒")
    print("="*80)

    # 定义需要裁剪的视频
    videos_to_trim = [
        {
            "input": "videos/scene_02_ren_modern_runway.mp4",
            "output": "videos/scene_02_ren_modern_runway_trimmed.mp4",
            "duration": 2,
            "description": "scene_02 - 保留前2秒（有动作的部分）"
        },
        {
            "input": "videos/scene_05_zhi_modern_runway.mp4",
            "output": "videos/scene_05_zhi_modern_runway_trimmed.mp4",
            "duration": 2,
            "description": "scene_05 - 保留前2秒（字幕出现前）"
        }
    ]

    print(f"\n共需裁剪 {len(videos_to_trim)} 个视频")

    success_count = 0
    failed_count = 0

    for i, video in enumerate(videos_to_trim, 1):
        print(f"\n\n[{i}/{len(videos_to_trim)}] {video['description']}")

        if trim_video(video['input'], video['output'], video['duration']):
            success_count += 1
        else:
            failed_count += 1

    # 总结
    print(f"\n\n{'='*80}")
    print("裁剪完成")
    print(f"{'='*80}")
    print(f"✅ 成功: {success_count} 个")
    print(f"❌ 失败: {failed_count} 个")

    if success_count > 0:
        print(f"\n📁 裁剪后的视频保存在 videos/ 目录下，文件名带 '_trimmed' 后缀")


if __name__ == "__main__":
    main()

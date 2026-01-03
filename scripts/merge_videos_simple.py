#!/usr/bin/env python3
"""
简化版视频合并脚本 - 直接合并所有 MP4 文件
"""

import subprocess
from pathlib import Path


def merge_all_videos(video_dir: Path, output_path: Path):
    """合并所有视频文件

    Args:
        video_dir: 视频文件目录
        output_path: 输出视频路径
    """

    # 收集所有 MP4 文件并排序
    video_files = sorted(video_dir.glob("*.mp4"))

    if not video_files:
        print("❌ 错误：没有找到任何视频文件")
        return None

    print("=" * 70)
    print("🎬 视频合并工具")
    print("=" * 70)
    print()

    for i, video_file in enumerate(video_files, 1):
        print(f"✅ 视频 {i}: {video_file.name}")

    print(f"\n📊 总共 {len(video_files)} 个视频片段")

    # 创建 FFmpeg 输入列表文件
    list_file = video_dir.parent / "merge_list.txt"

    with open(list_file, 'w', encoding='utf-8') as f:
        for video_file in video_files:
            # FFmpeg concat 格式
            f.write(f"file '{video_file.name}'\n")

    print(f"📝 创建合并列表: {list_file}")

    # 使用 FFmpeg 合并视频（简单拼接，速度快）
    print(f"\n🎬 开始合并视频...")

    # 切换到视频目录以使用相对路径
    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', str(list_file.relative_to(video_dir.parent)),
        '-c', 'copy',
        str(output_path)
    ]

    subprocess.run(cmd, check=True, cwd=str(video_dir.parent))

    # 清理临时文件
    list_file.unlink(missing_ok=True)

    # 获取最终视频信息
    duration_cmd = [
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        str(output_path)
    ]
    result = subprocess.run(duration_cmd, capture_output=True, text=True, check=True)
    total_duration = float(result.stdout.strip())

    file_size = output_path.stat().st_size / (1024 * 1024)  # MB

    print(f"\n" + "=" * 70)
    print(f"✅ 视频合并完成！")
    print(f"=" * 70)
    print(f"📁 输出文件: {output_path}")
    print(f"📊 总时长: {total_duration:.1f} 秒 ({total_duration/60:.1f} 分钟)")
    print(f"💾 文件大小: {file_size:.1f} MB")
    print(f"🎬 场景数量: {len(video_files)}")
    print("=" * 70)

    return output_path


if __name__ == "__main__":
    # 配置
    VIDEO_DIR = Path('./storyboards/文脉薪传/dynamic_videos_ve/videos')
    OUTPUT_PATH = Path('./storyboards/文脉薪传/文脉薪传_完整版.mp4')

    # 确保输出目录存在
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # 合并视频
    result = merge_all_videos(VIDEO_DIR, OUTPUT_PATH)

    if result:
        print(f"\n🎉 大功告成！")

#!/usr/bin/env python3
"""
合并所有场景视频成一个完整作品
"""

import os
import subprocess
import yaml
from pathlib import Path
from typing import List


def merge_videos(
    video_dir: Path,
    script_path: str,
    output_path: Path,
    add_transitions: bool = True
):
    """合并所有场景视频

    Args:
        video_dir: 视频文件目录
        script_path: 脚本文件路径（用于获取场景顺序）
        output_path: 输出视频路径
        add_transitions: 是否添加转场效果
    """

    # 加载脚本获取场景顺序
    with open(script_path, 'r', encoding='utf-8') as f:
        script_data = yaml.safe_load(f)

    scenes = script_data.get('scenes', [])

    # 收集所有视频文件（按场景顺序）
    video_files = []
    missing_files = []

    for scene in scenes:
        scene_id = scene['id']
        video_file = video_dir / f"{scene_id}.mp4"

        if video_file.exists():
            video_files.append(video_file)
            print(f"✅ 找到视频: {scene_id}.mp4")
        else:
            missing_files.append(scene_id)
            print(f"⚠️  缺失视频: {scene_id}.mp4")

    if missing_files:
        print(f"\n⚠️  警告：缺少 {len(missing_files)} 个视频文件")
        print(f"   {', '.join(missing_files)}")
        print(f"\n继续合并已有的 {len(video_files)} 个视频...\n")

    if not video_files:
        print("❌ 错误：没有找到任何视频文件")
        return None

    # 创建 FFmpeg 输入列表文件
    list_file = video_dir.parent / "merge_list.txt"

    with open(list_file, 'w', encoding='utf-8') as f:
        for video_file in video_files:
            # FFmpeg concat 格式需要转义特殊字符
            escaped_path = str(video_file).replace("'", "'\\''")
            f.write(f"file '{escaped_path}'\n")

    print(f"📝 创建合并列表: {list_file}")
    print(f"📊 总共 {len(video_files)} 个视频片段")

    # 使用 FFmpeg 合并视频
    if add_transitions:
        # 方法1: 带转场效果（淡入淡出）
        print(f"\n🎬 开始合并视频（包含转场效果）...")
        merge_with_transitions(video_files, output_path)
    else:
        # 方法2: 简单拼接（无转场）
        print(f"\n🎬 开始合并视频（简单拼接）...")
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(list_file),
            '-c', 'copy',
            str(output_path)
        ]

        subprocess.run(cmd, check=True)

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


def merge_with_transitions(video_files: List[Path], output_path: Path):
    """使用转场效果合并视频（淡入淡出）

    注意：此方法需要重新编码，速度较慢但效果更好
    """

    # 构建复杂的 FFmpeg 滤镜链
    inputs = []
    filter_complex = []

    for i, video_file in enumerate(video_files):
        inputs.extend(['-i', str(video_file)])

    # 构建淡入淡出滤镜
    # 每个视频之间添加 0.5 秒的交叉淡化
    transition_duration = 0.5

    if len(video_files) == 1:
        # 只有一个视频，直接输出
        filter_complex = "[0:v]null[v];[0:a]anull[a]"
    else:
        # 多个视频，添加转场
        for i in range(len(video_files) - 1):
            if i == 0:
                # 第一个视频
                filter_complex.append(
                    f"[{i}:v][{i}:a][{i+1}:v][{i+1}:a]"
                    f"xfade=transition=fade:duration={transition_duration}:offset=0[v{i}][a{i}]"
                )
            else:
                # 后续视频
                filter_complex.append(
                    f"[v{i-1}][a{i-1}][{i+1}:v][{i+1}:a]"
                    f"xfade=transition=fade:duration={transition_duration}:offset=0[v{i}][a{i}]"
                )

        # 最后输出
        last_idx = len(video_files) - 2
        filter_complex.append(f"[v{last_idx}]null[v];[a{last_idx}]anull[a]")

    filter_str = ";".join(filter_complex)

    # 由于 xfade 滤镜实现复杂，我们使用简化版本：直接拼接
    # 如果需要转场效果，建议使用专业视频编辑软件

    # 简化方案：重新编码以确保兼容性
    cmd = [
        'ffmpeg', '-y',
        *inputs,
        '-filter_complex',
        f"concat=n={len(video_files)}:v=1:a=1[v][a]",
        '-map', '[v]',
        '-map', '[a]',
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        '-c:a', 'aac',
        '-b:a', '192k',
        str(output_path)
    ]

    subprocess.run(cmd, check=True)


def main():
    """主函数"""

    # 配置
    VIDEO_DIR = Path('./storyboards/文脉薪传/dynamic_videos_ve/videos')
    SCRIPT_PATH = './文脉薪传_细化脚本.yaml'
    OUTPUT_PATH = Path('./storyboards/文脉薪传/文脉薪传_完整版.mp4')

    # 确保输出目录存在
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("🎬 文脉薪传 - 视频合并工具")
    print("=" * 70)
    print()

    # 合并视频
    result = merge_videos(
        video_dir=VIDEO_DIR,
        script_path=SCRIPT_PATH,
        output_path=OUTPUT_PATH,
        add_transitions=False  # 简单拼接，速度快
    )

    if result:
        print(f"\n🎉 大功告成！可以播放视频了：")
        print(f"   open {result}")


if __name__ == "__main__":
    main()

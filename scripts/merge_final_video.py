#!/usr/bin/env python3
"""
合并所有分镜视频为最终完整视频
"""

import subprocess
from pathlib import Path
import yaml


def merge_scene_videos(scene_videos_dir: str, script_path: str, output_path: str):
    """合并所有分镜视频"""

    scene_dir = Path(scene_videos_dir)
    output = Path(output_path)

    # 加载脚本获取场景顺序
    with open(script_path, 'r', encoding='utf-8') as f:
        script_data = yaml.safe_load(f)

    scenes = script_data.get('scenes', [])

    print("=" * 60)
    print("🎬 合并所有分镜视频为最终作品")
    print("=" * 60)
    print(f"\n📁 输入目录: {scene_dir}")
    print(f"📊 场景数量: {len(scenes)}")

    # 检查所有视频文件是否存在
    video_files = []
    missing_videos = []

    for scene in scenes:
        scene_id = scene['id']
        video_path = scene_dir / f"{scene_id}.mp4"

        if video_path.exists():
            video_files.append(video_path)
            print(f"   ✅ {scene_id}.mp4")
        else:
            missing_videos.append(scene_id)
            print(f"   ❌ {scene_id}.mp4 (缺失)")

    if missing_videos:
        print(f"\n⚠️  警告：缺失 {len(missing_videos)} 个视频文件")
        for vid in missing_videos:
            print(f"   - {vid}")
        print("\n将继续合并已有的视频...")

    if not video_files:
        print("\n❌ 错误：没有找到任何视频文件")
        return

    # 创建concat文件列表
    concat_file = scene_dir / "concat_list.txt"

    with open(concat_file, 'w') as f:
        for video_file in video_files:
            f.write(f"file '{video_file.absolute()}'\n")

    print(f"\n📝 创建合并列表: {concat_file}")

    # 使用ffmpeg合并视频
    print(f"\n🎞️  正在合并视频...")

    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', str(concat_file),
        '-c', 'copy',
        str(output)
    ]

    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )

        print(f"\n✅ 合并成功！")
        print(f"📹 输出文件: {output}")

        # 获取视频信息
        probe_cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration,size',
            '-of', 'default=noprint_wrappers=1',
            str(output)
        ]

        probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
        print(f"\n📊 视频信息:")
        print(probe_result.stdout)

        # 清理临时文件
        concat_file.unlink()
        print("\n🧹 清理临时文件完成")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ 合并失败: {e}")
        print(f"错误输出: {e.stderr}")

    print("\n" + "=" * 60)
    print("✅ 处理完成！")
    print("=" * 60)


def main():
    """主函数"""

    # 配置路径
    scene_videos_dir = "./storyboards/文脉薪传/scene_videos"
    script_path = "./文脉薪传_细化脚本.yaml"
    output_path = "./storyboards/文脉薪传/文脉薪传_完整版.mp4"

    merge_scene_videos(scene_videos_dir, script_path, output_path)


if __name__ == "__main__":
    main()

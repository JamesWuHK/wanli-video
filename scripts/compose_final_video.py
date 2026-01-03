#!/usr/bin/env python3
"""
文脉薪传 - 完整视频合成脚本
将所有场景视频、音频和字幕组合成最终完整视频
"""

import json
import subprocess
from pathlib import Path
from datetime import timedelta


def format_time(seconds):
    """将秒数转换为 SRT 时间格式 (HH:MM:SS,mmm)"""
    td = timedelta(seconds=seconds)
    hours = int(td.total_seconds() // 3600)
    minutes = int((td.total_seconds() % 3600) // 60)
    secs = int(td.total_seconds() % 60)
    millis = int((td.total_seconds() % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def generate_srt(narrations, output_file):
    """生成完整的 SRT 字幕文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, item in enumerate(narrations, 1):
            f.write(f"{i}\n")
            f.write(f"{format_time(item['start'])} --> {format_time(item['end'])}\n")
            f.write(f"{item['text']}\n\n")
    print(f"✅ 字幕文件已生成: {output_file}")


def get_audio_duration(audio_file):
    """获取音频文件时长"""
    try:
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            str(audio_file)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except:
        return 0


def create_scene_with_audio(video_file, audio_file, output_file, duration=None):
    """
    为单个场景添加音频

    Args:
        video_file: 视频文件路径
        audio_file: 音频文件路径
        output_file: 输出文件路径
        duration: 指定时长（如果视频需要裁剪）
    """
    video_path = Path(video_file)
    audio_path = Path(audio_file)
    output_path = Path(output_file)

    if not video_path.exists():
        print(f"❌ 视频文件不存在: {video_file}")
        return False

    if not audio_path.exists():
        print(f"❌ 音频文件不存在: {audio_file}")
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 获取音频时长
    audio_duration = get_audio_duration(audio_file)

    # 构建 ffmpeg 命令
    cmd = ['ffmpeg', '-y']

    # 输入文件
    cmd.extend(['-i', str(video_path)])
    cmd.extend(['-i', str(audio_path)])

    # 视频处理
    if duration:
        # 如果指定了时长，裁剪视频
        cmd.extend(['-t', str(duration)])

    # 合并音视频
    cmd.extend([
        '-map', '0:v',  # 使用第一个输入的视频
        '-map', '1:a',  # 使用第二个输入的音频
        '-c:v', 'copy',  # 复制视频编码
        '-c:a', 'aac',   # 音频编码为 AAC
        '-b:a', '192k',  # 音频比特率
        '-shortest',     # 以最短的流为准
        str(output_path)
    ])

    try:
        subprocess.run(cmd, capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 处理失败: {e.stderr.decode()}")
        return False


def main():
    print("=" * 80)
    print("文脉薪传 - 最终视频合成")
    print("=" * 80)

    # 场景配置
    scenes = [
        # 注意：我们没有 scene_01_opening 的 runway 视频，需要确认
        {
            "id": "scene_02_ren_intro",
            "video": "videos/scene_02_ren_intro_runway.mp4",
            "audio": "storyboards/文脉薪传/final_videos/audio/scene_02_ren_intro.mp3",
            "narration": "仁，是爱人之心。子曰：'仁者爱人'。己欲立而立人，己欲达而达人。",
            "duration": None  # 使用原始时长
        },
        {
            "id": "scene_02_ren_modern",
            "video": "videos/scene_02_ren_modern_runway_trimmed.mp4",  # 使用裁剪后的2秒版本
            "audio": "storyboards/文脉薪传/final_videos/audio/scene_02_ren_modern.mp3",
            "narration": "从古至今，这份悲天悯人的情怀，化作无数善举，温暖人间。",
            "duration": 2  # 只保留2秒
        },
        {
            "id": "scene_03_yi_history",
            "video": "videos/scene_03_yi_history_runway.mp4",
            "audio": "storyboards/文脉薪传/final_videos/audio/scene_03_yi_history.mp3",
            "narration": "义，是正道而行。孟子曰：'生亦我所欲，义亦我所欲，二者不可得兼，舍生而取义者也。'",
            "duration": None
        },
        {
            "id": "scene_03_yi_modern",
            "video": "videos/scene_03_yi_modern_runway.mp4",
            "audio": "storyboards/文脉薪传/final_videos/audio/scene_03_yi_modern.mp3",
            "narration": "千年来，中国人以义为准则，择善而从。",
            "duration": None
        },
        {
            "id": "scene_04_li_tradition",
            "video": "videos/scene_04_li_tradition_runway.mp4",
            "audio": "storyboards/文脉薪传/final_videos/audio/scene_04_li_tradition.mp3",
            "narration": "礼，是秩序之美。'不学礼，无以立。'礼节规范行为，礼仪彰显尊重。",
            "duration": None
        },
        {
            "id": "scene_04_li_modern",
            "video": "videos/scene_04_li_modern_runway.mp4",
            "audio": "storyboards/文脉薪传/final_videos/audio/scene_04_li_modern.mp3",
            "narration": "这是中华民族代代相传的文明密码。",
            "duration": None
        },
        {
            "id": "scene_05_zhi_ancient",
            "video": "videos/scene_05_zhi_ancient_runway.mp4",
            "audio": "storyboards/文脉薪传/final_videos/audio/scene_05_zhi_ancient.mp3",
            "narration": "智，是求知不息。'学而不思则罔，思而不学则殆。'",
            "duration": None
        },
        {
            "id": "scene_05_zhi_modern",
            "video": "videos/scene_05_zhi_modern_runway_trimmed.mp4",  # 使用裁剪后的2秒版本
            "audio": "storyboards/文脉薪传/final_videos/audio/scene_05_zhi_modern.mp3",
            "narration": "从古代的智慧结晶，到今天的科技创新，中国人从未停止探索真理的脚步。",
            "duration": 2  # 只保留2秒
        },
        {
            "id": "scene_06_xin_principle",
            "video": "videos/scene_06_xin_principle_runway_v2.mp4",
            "audio": "storyboards/文脉薪传/final_videos/audio/scene_06_xin_principle.mp3",
            "narration": "信，是立身之本。'人而无信，不知其可也。'",
            "duration": None
        },
        {
            "id": "scene_06_xin_modern",
            "video": "videos/scene_06_xin_modern_runway.mp4",
            "audio": "storyboards/文脉薪传/final_videos/audio/scene_06_xin_modern.mp3",
            "narration": "诚实守信，一诺千金，这是中国人安身立命的根基，也是社会运行的基石。",
            "duration": None
        },
        {
            "id": "scene_07_heritage_education",
            "video": "videos/scene_07_heritage_education_runway.mp4",
            "audio": "storyboards/文脉薪传/final_videos/audio/scene_07_heritage_education.mp3",
            "narration": "仁义礼智信，五常之道，是我们的文化基因，是我们的精神家园。",
            "duration": None
        },
        {
            "id": "scene_07_grand_finale",
            "video": "videos/scene_07_grand_finale_runway.mp4",
            "audio": "storyboards/文脉薪传/final_videos/audio/scene_07_grand_finale.mp3",
            "narration": "让我们薪火相传，让这份千年智慧，在新时代绽放新的光芒。",
            "duration": None
        }
    ]

    # 步骤1：为每个场景合成音视频
    print(f"\n步骤1: 为每个场景合成音视频")
    print("=" * 80)

    temp_dir = Path("temp_scenes")
    temp_dir.mkdir(exist_ok=True)

    processed_scenes = []
    total_duration = 0
    narrations_timeline = []

    for i, scene in enumerate(scenes, 1):
        print(f"\n[{i}/{len(scenes)}] 处理场景: {scene['id']}")

        temp_output = temp_dir / f"{scene['id']}_with_audio.mp4"

        if create_scene_with_audio(
            scene['video'],
            scene['audio'],
            temp_output,
            scene['duration']
        ):
            # 获取处理后视频的实际时长
            duration = get_audio_duration(temp_output)
            if duration > 0:
                # 记录字幕时间轴
                narrations_timeline.append({
                    'start': total_duration,
                    'end': total_duration + duration,
                    'text': scene['narration']
                })

                processed_scenes.append({
                    'file': temp_output,
                    'duration': duration
                })

                total_duration += duration

                print(f"✅ 场景处理成功，时长: {duration:.2f}秒")
            else:
                print(f"❌ 无法获取视频时长")
        else:
            print(f"❌ 场景处理失败")

    if not processed_scenes:
        print("\n❌ 没有成功处理的场景，退出")
        return

    print(f"\n✅ 成功处理 {len(processed_scenes)} 个场景")
    print(f"总时长: {total_duration:.2f}秒 ({total_duration/60:.2f}分钟)")

    # 步骤2：生成字幕文件
    print(f"\n步骤2: 生成字幕文件")
    print("=" * 80)

    srt_file = Path("final_output/complete_video.srt")
    srt_file.parent.mkdir(parents=True, exist_ok=True)
    generate_srt(narrations_timeline, srt_file)

    # 步骤3：合并所有场景
    print(f"\n步骤3: 合并所有场景")
    print("=" * 80)

    # 创建文件列表
    concat_list = temp_dir / "concat_list.txt"
    with open(concat_list, 'w', encoding='utf-8') as f:
        for scene in processed_scenes:
            f.write(f"file '{scene['file'].absolute()}'\n")

    # 合并视频
    merged_video = Path("final_output/complete_video_no_subtitles.mp4")

    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', str(concat_list),
        '-c', 'copy',
        str(merged_video)
    ]

    print("🎬 正在合并视频...")
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        print(f"✅ 视频合并成功: {merged_video}")
    except subprocess.CalledProcessError as e:
        print(f"❌ 视频合并失败: {e.stderr.decode()}")
        return

    # 步骤4：添加字幕
    print(f"\n步骤4: 添加字幕到视频")
    print("=" * 80)

    final_video = Path("final_output/complete_video_final.mp4")

    cmd = [
        'ffmpeg', '-y',
        '-i', str(merged_video),
        '-vf', f"subtitles={srt_file.absolute()}:force_style='FontName=SimHei,FontSize=24,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=2'",
        '-c:a', 'copy',
        str(final_video)
    ]

    print("📝 正在添加字幕...")
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        print(f"✅ 字幕添加成功!")
    except subprocess.CalledProcessError as e:
        print(f"❌ 字幕添加失败: {e.stderr.decode()}")
        print("ℹ️  但无字幕版本已生成")

    # 总结
    print(f"\n{'=' * 80}")
    print("🎉 最终视频合成完成!")
    print("=" * 80)
    print(f"\n输出文件:")
    print(f"  📹 完整视频（带字幕）: {final_video}")
    print(f"  📹 完整视频（无字幕）: {merged_video}")
    print(f"  📝 字幕文件: {srt_file}")
    print(f"\n视频信息:")
    print(f"  总场景数: {len(processed_scenes)}")
    print(f"  总时长: {total_duration:.2f}秒 ({total_duration/60:.2f}分钟)")

    # 检查文件大小
    if final_video.exists():
        file_size = final_video.stat().st_size / (1024 * 1024)
        print(f"  文件大小: {file_size:.2f} MB")


if __name__ == "__main__":
    main()

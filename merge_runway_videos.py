#!/usr/bin/env python3
"""
整合 Runway 生成的视频片段，添加 BGM、画外音和字幕
"""

import os
import subprocess
import json
from pathlib import Path
from typing import List, Dict


def get_video_duration(video_path: str) -> float:
    """获取视频时长（秒）"""
    cmd = [
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'json',
        video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
    return float(data['format']['duration'])


def extend_short_video(input_path: Path, output_path: Path, target_duration: float = 10.0):
    """延长短视频：使用减速（不循环）让视频更自然

    Args:
        input_path: 输入视频路径
        output_path: 输出视频路径
        target_duration: 目标时长（秒）
    """
    current_duration = get_video_duration(str(input_path))

    # 计算减速系数
    speed_factor = current_duration / target_duration

    print(f"  延长视频: {input_path.name}")
    print(f"  当前时长: {current_duration:.2f}秒")
    print(f"  目标时长: {target_duration:.2f}秒")
    print(f"  播放速度: {speed_factor:.2f}x (减速)")

    # FFmpeg 命令：只减速，不循环（避免重复播放的奇怪效果）
    cmd = [
        'ffmpeg', '-y',
        '-i', str(input_path),
        '-filter:v', f'setpts={1/speed_factor}*PTS',
        '-filter:a', f'atempo={speed_factor}',
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        '-c:a', 'aac',
        '-b:a', '192k',
        str(output_path)
    ]

    subprocess.run(cmd, check=True, capture_output=True)
    actual_duration = get_video_duration(str(output_path))
    print(f"  ✅ 延长完成: {actual_duration:.2f}秒\n")


def create_video_list(videos_dir: Path, output_file: Path, temp_dir: Path) -> List[Dict]:
    """创建视频列表文件，按场景顺序排列"""

    # 定义场景顺序（根据 complete_storyboard_design.json）
    scene_order = [
        'scene_01_opening',
        'scene_02_ren_intro',
        'scene_02_ren_modern',
        'scene_03_yi_history',
        'scene_03_yi_modern',
        'scene_04_li_tradition',
        'scene_04_li_modern',
        'scene_05_zhi_ancient',
        'scene_05_zhi_modern',
        'scene_06_xin_principle',
        'scene_06_xin_modern',
        'scene_07_heritage_education',
        'scene_07_grand_finale',
    ]

    # 视频文件名映射（处理不同的命名变体）
    video_mapping = {
        'scene_01_opening': 'scene_01_opening_runway_test.mp4',
        'scene_02_ren_intro': 'scene_02_ren_intro_runway.mp4',
        'scene_02_ren_modern': 'scene_02_ren_modern_runway_trimmed.mp4',
        'scene_03_yi_history': 'scene_03_yi_history_runway.mp4',
        'scene_03_yi_modern': 'scene_03_yi_modern_runway.mp4',
        'scene_04_li_tradition': 'scene_04_li_tradition_runway.mp4',
        'scene_04_li_modern': 'scene_04_li_modern_runway.mp4',
        'scene_05_zhi_ancient': 'scene_05_zhi_ancient_runway.mp4',
        'scene_05_zhi_modern': 'scene_05_zhi_modern_runway_trimmed.mp4',
        'scene_06_xin_principle': 'scene_06_xin_principle_runway_v2.mp4',
        'scene_06_xin_modern': 'scene_06_xin_modern_runway.mp4',
        'scene_07_heritage_education': 'scene_07_heritage_education_runway.mp4',
        'scene_07_grand_finale': 'scene_07_grand_finale_runway.mp4',
    }

    # 需要延长的短片段
    short_clips = ['scene_02_ren_modern', 'scene_05_zhi_modern']

    video_list = []
    total_duration = 0.0

    # 创建临时目录存放延长的视频
    temp_dir.mkdir(parents=True, exist_ok=True)

    print("\n=== 准备视频片段 ===")
    print("\n处理短视频片段（延长到10秒）：")

    for scene_id in scene_order:
        video_filename = video_mapping.get(scene_id)
        if not video_filename:
            print(f"⚠️  场景 {scene_id} 没有映射的视频文件")
            continue

        video_path = videos_dir / video_filename
        if not video_path.exists():
            print(f"❌ 缺失: {video_filename}")
            continue

        # 检查是否是短片段，需要延长
        if scene_id in short_clips:
            extended_path = temp_dir / f"{scene_id}_extended.mp4"
            extend_short_video(video_path, extended_path, target_duration=10.0)
            video_path = extended_path

        duration = get_video_duration(str(video_path))
        total_duration += duration

        video_list.append({
            'scene_id': scene_id,
            'path': str(video_path),
            'duration': duration
        })

        if scene_id not in short_clips:
            print(f"✅ {scene_id}: {duration:.2f}秒 - {video_filename}")

    print(f"\n总时长: {total_duration:.2f}秒 ({total_duration/60:.2f}分钟)")
    print(f"视频片段数: {len(video_list)}")

    # 创建 ffmpeg concat 格式的文件列表
    with open(output_file, 'w', encoding='utf-8') as f:
        for video in video_list:
            # 转义路径中的特殊字符
            escaped_path = video['path'].replace("'", "'\\''")
            f.write(f"file '{escaped_path}'\n")

    return video_list


def merge_subtitles(storyboard_dir: Path, video_list: List[Dict], output_srt: Path, global_speed: float = 1.0):
    """合并所有字幕文件，调整时间戳（考虑全局减速）

    Args:
        storyboard_dir: 分镜目录
        video_list: 视频列表
        output_srt: 输出字幕文件
        global_speed: 全局播放速度（用于计算减速后的时间）
    """

    print("\n=== 合并字幕文件 ===")
    print(f"全局播放速度: {global_speed}x")

    subtitle_dir = storyboard_dir / 'final_videos' / 'temp'

    all_subtitles = []
    current_time = 0.0  # 这是减速后的时间

    for video in video_list:
        scene_id = video['scene_id']
        srt_file = subtitle_dir / f"{scene_id}.srt"

        # 计算减速后的时长
        original_duration = video['duration']
        slowed_duration = original_duration / global_speed

        if not srt_file.exists():
            print(f"⚠️  字幕缺失: {scene_id}.srt")
            current_time += slowed_duration
            continue

        # 读取字幕文件
        with open(srt_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()

        if not content:
            print(f"⚠️  字幕为空: {scene_id}.srt")
            current_time += slowed_duration
            continue

        # 解析字幕（简单解析，假设每个场景只有一条字幕）
        lines = content.split('\n')
        if len(lines) >= 3:
            subtitle_text = '\n'.join(lines[2:])  # 字幕文本

            # 添加到合并字幕列表，使用减速后的时间戳
            all_subtitles.append({
                'start': current_time,
                'end': current_time + slowed_duration,
                'text': subtitle_text,
                'scene_id': scene_id,
                'original_duration': original_duration,
                'slowed_duration': slowed_duration
            })

            print(f"✅ {scene_id}: {format_srt_time(current_time)} -> {format_srt_time(current_time + slowed_duration)} ({slowed_duration:.2f}s)")
            print(f"   {subtitle_text[:50]}...")

        current_time += slowed_duration

    # 写入合并后的字幕文件
    with open(output_srt, 'w', encoding='utf-8') as f:
        for i, sub in enumerate(all_subtitles, 1):
            start_time = format_srt_time(sub['start'])
            end_time = format_srt_time(sub['end'])

            f.write(f"{i}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{sub['text']}\n\n")

    print(f"\n✅ 字幕合并完成: {output_srt}")
    print(f"   共 {len(all_subtitles)} 条字幕")
    print(f"   总时长: {format_srt_time(current_time)}")


def format_srt_time(seconds: float) -> str:
    """将秒数转换为 SRT 时间格式 (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def merge_scene_narrations(video_list: List[Dict], audio_dir: Path, output_audio: Path, global_speed: float = 1.0):
    """合并所有场景的画外音，调整时间戳以匹配视频

    Args:
        video_list: 视频列表
        audio_dir: 场景音频目录
        output_audio: 输出音频文件
        global_speed: 全局播放速度
    """

    print("\n=== 合并场景画外音 ===")
    print(f"全局播放速度: {global_speed}x")

    # 创建临时目录存放调整速度后的音频
    temp_audio_dir = output_audio.parent / 'temp_audio'
    temp_audio_dir.mkdir(parents=True, exist_ok=True)

    # 创建音频列表文件
    audio_list_file = output_audio.parent / 'narration_list.txt'

    all_narrations = []
    current_time = 0.0

    for video in video_list:
        scene_id = video['scene_id']
        audio_file = audio_dir / f"{scene_id}.mp3"

        # 计算减速后的时长
        original_duration = video['duration']
        slowed_duration = original_duration / global_speed

        if not audio_file.exists():
            print(f"⚠️  画外音缺失: {scene_id}.mp3，将填充静音")
            # 创建静音音频
            silent_audio = temp_audio_dir / f"{scene_id}_silent.mp3"

            silence_cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', f'anullsrc=r=44100:cl=stereo',
                '-t', str(slowed_duration),
                '-c:a', 'libmp3lame',
                '-b:a', '192k',
                str(silent_audio)
            ]
            subprocess.run(silence_cmd, check=True, capture_output=True)
            audio_to_use = silent_audio
        else:
            # 调整音频速度以匹配视频（与视频减速同步），并裁剪/填充到精确时长
            slowed_audio = temp_audio_dir / f"{scene_id}_slowed.mp3"

            # 使用 atempo 调整速度，apad 填充静音，atrim 裁剪到精确时长
            slowdown_cmd = [
                'ffmpeg', '-y',
                '-i', str(audio_file),
                '-filter:a', f'atempo={global_speed},apad,atrim=0:{slowed_duration}',
                '-c:a', 'libmp3lame',
                '-b:a', '192k',
                str(slowed_audio)
            ]
            subprocess.run(slowdown_cmd, check=True, capture_output=True)
            audio_to_use = slowed_audio

        all_narrations.append({
            'path': str(audio_to_use),
            'scene_id': scene_id,
            'start': current_time,
            'duration': slowed_duration
        })

        print(f"✅ {scene_id}: {format_srt_time(current_time)} -> {format_srt_time(current_time + slowed_duration)}")
        current_time += slowed_duration

    # 创建 FFmpeg concat 格式的音频列表
    with open(audio_list_file, 'w', encoding='utf-8') as f:
        for narration in all_narrations:
            # 使用绝对路径，不需要转义（concat demuxer会正确处理）
            f.write(f"file '{narration['path']}'\n")

    # 合并所有画外音
    print(f"\n合并画外音到: {output_audio}")

    concat_cmd = [
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', str(audio_list_file),
        '-c:a', 'aac',
        '-b:a', '192k',
        str(output_audio)
    ]

    result = subprocess.run(concat_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ FFmpeg错误:\n{result.stderr}")
        raise subprocess.CalledProcessError(result.returncode, concat_cmd, result.stdout, result.stderr)

    # 清理临时文件
    audio_list_file.unlink(missing_ok=True)

    print(f"✅ 画外音合并完成")
    print(f"   总时长: {format_srt_time(current_time)}")


def merge_videos_with_audio_and_subtitles(
    video_list_file: Path,
    narration_file: Path,
    bgm_file: Path,
    subtitle_file: Path,
    output_file: Path,
    global_speed: float = 0.85
):
    """合并视频，添加画外音+BGM和字幕，并调整整体播放速度

    Args:
        video_list_file: 视频列表文件
        narration_file: 合并后的画外音文件
        bgm_file: BGM文件
        subtitle_file: 字幕文件
        output_file: 输出文件
        global_speed: 全局播放速度倍率（< 1 为减速，> 1 为加速）
    """

    print("\n=== 合并视频并添加音频和字幕 ===")
    print(f"全局播放速度: {global_speed}x (视频将{'减速' if global_speed < 1 else '加速'})")

    # FFmpeg 命令
    # 1. 使用 concat 协议合并视频
    # 2. 调整播放速度（减速到0.92x）
    # 3. 添加场景画外音（已减速对齐）+ 循环BGM
    # 4. 添加改进的字幕（使用实心清晰字体）

    cmd = [
        'ffmpeg', '-y',
        # 输入：视频列表
        '-f', 'concat',
        '-safe', '0',
        '-i', str(video_list_file),
        # 输入：画外音（已合并并减速，与视频场景对齐）
        '-i', str(narration_file),
        # 输入：BGM
        '-i', str(bgm_file),
        # 复杂滤镜：调整视频速度 + 添加字幕 + 混音（画外音 + BGM）
        '-filter_complex', (
            # 视频减速并添加字幕
            f"[0:v]setpts={1/global_speed}*PTS[v_slow];"
            f"[v_slow]subtitles={str(subtitle_file)}:"
            "force_style='"
            "FontName=PingFang SC,"  # 使用苹方字体
            "FontSize=26,"  # 字号稍大
            "Bold=1,"  # 粗体
            "PrimaryColour=&H00FFFFFF,"  # 白色
            "OutlineColour=&H00000000,"  # 黑色描边
            "BorderStyle=1,"  # 实心描边
            "Outline=3,"  # 加粗描边
            "Shadow=2,"  # 加深阴影
            "MarginV=15"  # 底部边距（从30减少到15，更靠近底部）
            "'[v_out];"
            # BGM循环并减速（与视频同步）
            f"[2:a]aloop=loop=5:size=2e+09,atempo={global_speed}[bgm_loop];"
            # 混音：画外音（已减速，音量100%）+ BGM（音量20%，作为背景）
            "[1:a][bgm_loop]amix=inputs=2:duration=first:weights=1.0 0.2[a_out]"
        ),
        '-map', '[v_out]',
        '-map', '[a_out]',
        # 视频编码
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        # 音频编码
        '-c:a', 'aac',
        '-b:a', '192k',
        '-shortest',  # 以视频长度为准
        str(output_file)
    ]

    print(f"\n执行 FFmpeg 命令...")
    print(f"输出: {output_file}")

    result = subprocess.run(cmd, check=True)

    if result.returncode == 0:
        print(f"\n✅ 视频合并成功！")

        # 获取最终视频信息
        duration = get_video_duration(str(output_file))
        file_size = output_file.stat().st_size / (1024 * 1024)  # MB

        print(f"\n" + "=" * 70)
        print(f"📁 输出文件: {output_file}")
        print(f"📊 总时长: {duration:.1f}秒 ({duration/60:.2f}分钟)")
        print(f"💾 文件大小: {file_size:.1f} MB")
        print("=" * 70)
    else:
        print(f"\n❌ 视频合并失败")


def main():
    """主函数"""

    # 配置路径
    VIDEOS_DIR = Path('/Users/wujames/cursor_prj/wanli-qingyun-project/videos')
    STORYBOARD_DIR = Path('/Users/wujames/cursor_prj/wanli-qingyun-project/storyboards/文脉薪传')
    AUDIO_DIR = STORYBOARD_DIR / 'final_videos' / 'audio'
    BGM_FILE = STORYBOARD_DIR / 'bgm' / 'china-chinese-asian-music-346568.mp3'
    OUTPUT_DIR = STORYBOARD_DIR

    # 临时文件目录
    TEMP_DIR = OUTPUT_DIR / 'temp_extended'
    VIDEO_LIST_FILE = OUTPUT_DIR / 'runway_merge_list.txt'
    MERGED_SUBTITLE = OUTPUT_DIR / 'merged_subtitles.srt'
    MERGED_NARRATION = OUTPUT_DIR / 'merged_narration.aac'

    # 最终输出
    OUTPUT_VIDEO = OUTPUT_DIR / '文脉薪传_Runway_最终版_V7.mp4'

    # 全局播放速度（0.92x减速，使~131秒变成~142秒≈2.4分钟）
    GLOBAL_SPEED = 0.92

    print("=" * 70)
    print("🎬 文脉薪传 - Runway 视频整合工具 V7")
    print("=" * 70)
    print(f"\n改进点：")
    print(f"  1. 🆕 字幕位置进一步下移（MarginV=15，贴近屏幕底部）")
    print(f"  2. 画外音与视频场景严格对齐（每个场景独立音频）")
    print(f"  3. 🎵 添加背景音乐（BGM）并与画外音混音")
    print(f"  4. 优化短片段处理：只减速不循环，避免重复播放")
    print(f"  5. 全局减速到 {GLOBAL_SPEED}x，目标时长约2.4分钟")
    print(f"  6. 改进字幕字体（加粗描边，更清晰）")
    print(f"  7. 字幕时间轴严格对齐视频分镜")

    # 1. 创建视频列表（包含延长短片段）
    video_list = create_video_list(VIDEOS_DIR, VIDEO_LIST_FILE, TEMP_DIR)

    if not video_list:
        print("\n❌ 没有找到任何视频文件")
        return

    # 2. 合并字幕（传入 global_speed 以正确计算减速后的时间轴）
    merge_subtitles(STORYBOARD_DIR, video_list, MERGED_SUBTITLE, global_speed=GLOBAL_SPEED)

    # 3. 合并场景画外音（按场景顺序拼接）
    merge_scene_narrations(video_list, AUDIO_DIR, MERGED_NARRATION, global_speed=GLOBAL_SPEED)

    # 4. 检查BGM是否存在
    if not BGM_FILE.exists():
        print(f"\n❌ BGM文件不存在: {BGM_FILE}")
        return

    # 5. 合并视频、画外音、BGM和字幕，应用全局减速
    merge_videos_with_audio_and_subtitles(
        VIDEO_LIST_FILE,
        MERGED_NARRATION,
        BGM_FILE,
        MERGED_SUBTITLE,
        OUTPUT_VIDEO,
        global_speed=GLOBAL_SPEED
    )

    # 清理临时文件
    VIDEO_LIST_FILE.unlink(missing_ok=True)
    # 保留 temp_extended 目录以便检查

    print(f"\n🎉 大功告成！")
    print(f"\n可以播放视频查看效果：")
    print(f"   open '{OUTPUT_VIDEO}'")
    print(f"\n临时延长的视频保存在: {TEMP_DIR}")


if __name__ == "__main__":
    main()

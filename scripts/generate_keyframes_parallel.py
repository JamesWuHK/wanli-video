#!/usr/bin/env python3
"""
并行为每个分镜生成关键帧图像
使用多线程加速生成过程
"""

import os
import yaml
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from generate_images_qingyun import QingyunImageGenerator


def create_keyframe_prompt(scene: dict) -> str:
    """根据场景创建关键帧提示词"""
    scene_id = scene['id']

    keyframe_prompts = {
        'scene_01_opening': '中国古代书院特写镜头："仁义礼智信"五个毛笔大字占满画面，笔画细节清晰可见，墨迹浓淡有致，金色光晕环绕，水墨画美学，16:9超高清。',
        'scene_02_ren_intro': '中国水墨画特写："仁"字书法笔画细节，墨迹渲染效果，周围有淡淡的中国传统花纹装饰，竹叶飘落，意境深远，16:9。',
        'scene_02_ren_modern': '中国志愿者和中国老人温馨画面特写：志愿者扶着老人的手臂，两人相视而笑，背景虚化的现代中国城市街道，温暖金色光线，感人至深，16:9。',
        'scene_03_yi_history': '岳飞背部特写："精忠报国"四个大字刺青清晰可见，周围环绕金色"义"字书法光影，史诗级电影光影，深红和金色配色，中国历史画卷风格，16:9。',
        'scene_03_yi_modern': '中国法官敲响法槌的瞬间特写：法槌击打的动感画面，周围散发正义光芒，中国法官坚毅的眼神，戏剧性光影对比，电影级构图，16:9。',
        'scene_04_li_tradition': '中国传统成人礼特写：冠冕加身的神圣时刻，中国年轻人双手合十行礼，周围环绕"礼"字书法光影，庄严肃穆，深蓝和金色配色，16:9。',
        'scene_04_li_modern': '中国晚辈为长辈敬茶的温馨特写：双手奉茶，茶杯冒着热气，中国长辈慈爱的微笑，温暖的家庭氛围，柔和光线，16:9。',
        'scene_05_zhi_ancient': '中国古代书房场景特写："智"字书法艺术，周围是中国古代典籍和文房四宝，烛光摇曳，金色光线，中国传统学术氛围，16:9。',
        'scene_05_zhi_modern': '中国航天器发射升空的壮观画面：火箭腾空而起，火焰和烟雾，周围环绕科技线条和数据流，中国航天梦，未来主义蓝色光线，16:9。',
        'scene_06_xin_principle': '中国传统红色印章按下的瞬间特写：印章泥印鲜红，"信"字清晰可见，墨迹未干的契约文书，稳重构图，中国传统诚信象征，16:9。',
        'scene_06_xin_modern': '两位中国人握手的温暖特写：手部握手动作，背景虚化，柔和光线照耀，信任和友谊的象征，现代中国生活场景，16:9。',
        'scene_07_heritage_education': '中国祖孙三代共读经典的温馨特写：古籍书页，三代人的手一起翻动书页，柔和金色光线，文化传承的温暖画面，16:9。',
        'scene_07_grand_finale': '中国壮丽山河日出全景：画面中央毛笔书法"文脉薪传 生生不息"八个大字，背景是中国山峦叠嶂，金色阳光，IMAX史诗级画面，16:9超高清。'
    }

    narration = scene.get('narration', '')
    return keyframe_prompts.get(scene_id, f'中国文化主题关键帧，{narration[:50]}的核心画面，电影级构图，16:9超高清。')


def generate_single_keyframe(scene: dict, keyframe_dir: Path, api_key: str) -> tuple:
    """生成单个关键帧"""
    scene_id = scene['id']
    keyframe_path = keyframe_dir / f"{scene_id}_keyframe.png"

    # 如果已存在，跳过
    if keyframe_path.exists():
        return (scene_id, True, "已存在")

    try:
        # 创建生成器（每个线程独立的生成器实例）
        generator = QingyunImageGenerator(api_key=api_key)

        # 生成关键帧提示词
        prompt = create_keyframe_prompt(scene)

        # 生成图像
        image_url = generator.generate_image(prompt)

        # 下载
        generator.download_image(image_url, str(keyframe_path))

        # 添加短暂延迟避免API限流
        time.sleep(1)

        return (scene_id, True, "成功")

    except Exception as e:
        return (scene_id, False, str(e))


def main():
    """主函数 - 并行生成"""
    print("=" * 60)
    print("🎬 并行生成所有关键帧图像")
    print("=" * 60)

    # 配置
    api_key = "sk-KfCX4tI7rDBtC7mynLmFj1z9D90HaO1oCQrVt61y9EXQ2vs1"
    script_path = './文脉薪传_细化脚本.yaml'
    keyframe_dir = Path('./storyboards/文脉薪传/keyframes')
    keyframe_dir.mkdir(parents=True, exist_ok=True)

    # 加载脚本
    with open(script_path, 'r', encoding='utf-8') as f:
        script_data = yaml.safe_load(f)

    scenes = script_data.get('scenes', [])
    print(f"\n✅ 找到 {len(scenes)} 个场景")
    print(f"🚀 使用 5 个并行线程加速生成")
    print(f"📁 输出目录: {keyframe_dir}\n")

    # 并行生成（使用5个线程）
    success_count = 0
    failed_scenes = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        # 提交所有任务
        future_to_scene = {
            executor.submit(generate_single_keyframe, scene, keyframe_dir, api_key): scene
            for scene in scenes
        }

        # 处理完成的任务
        for i, future in enumerate(as_completed(future_to_scene), 1):
            scene = future_to_scene[future]
            scene_id, success, message = future.result()

            status = "✅" if success else "❌"
            print(f"{status} [{i}/{len(scenes)}] {scene_id}: {message}")

            if success:
                success_count += 1
            else:
                failed_scenes.append((scene_id, message))

    print("\n" + "=" * 60)
    print(f"✅ 关键帧生成完成！成功 {success_count}/{len(scenes)} 张")

    if failed_scenes:
        print(f"\n⚠️  失败场景：")
        for sid, error in failed_scenes:
            print(f"   - {sid}: {error[:50]}")

    print(f"\n📁 输出目录: {keyframe_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()

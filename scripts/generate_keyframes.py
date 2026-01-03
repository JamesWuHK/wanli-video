#!/usr/bin/env python3
"""
为每个分镜生成关键帧图像
每个分镜除了开始帧，还需要一个关键帧（中间时刻的重要画面）
"""

import os
import yaml
from pathlib import Path
from generate_images_qingyun import QingyunImageGenerator


def create_keyframe_prompt(scene: dict) -> str:
    """根据场景创建关键帧提示词"""
    scene_id = scene['id']
    narration = scene['narration']

    # 为每个场景定制关键帧提示词（展现场景的核心动作或高潮时刻）
    keyframe_prompts = {
        'scene_01_opening': '中国古代书院特写镜头："仁义礼智信"五个毛笔大字占满画面，笔画细节清晰可见，墨迹浓淡有致，金色光晕环绕，水墨画美学，16:9超高清。',

        'scene_02_ren_intro': '中国水墨画特写："仁"字书法笔画细节，墨迹渲染效果，周围有淡淡的中国传统花纹装饰，竹叶飘落，意境深远，16:9。',

        'scene_02_ren_modern': '中国志愿者和中国老人温馨画面特写：志愿者扶着老人的手臂，两人相视而笑，背景虚化的现代中国城市街道，温暖金色光线，感人至深，16:9。',

        'scene_03_yi_history': '岳飞背部特写："精忠报国"四个大字刺青清晰可见，周围环绕金色"义"字书法光影，史诗级电影光影，深红和金色配色，中国历史画卷风格，16:9。',

        'scene_03_yi_modern': '中国法官敲响法槌的瞬间特写：法槌击打的动感画面，周围散发正义光芒，中国法官坚毅的眼神，戏剧性光影对比，电影级构图，16:9。',

        'scene_04_li_tradition': '中国传统成人礼特写：冠冕加身的神圣时刻，中国年轻人双手合十行礼，周围环绕"礼"字书法光影，庄严肃穆，深蓝和金色配色，16:9。',

        'scene_04_li_modern': '中国晚辈为长辈敬茶的温馨特写：双手奉茶，茶杯冒着热气，中国长辈慈爱的微笑，温暖的家庭氛围，柔和光线，16:9。',

        'scene_05_zhi_ancient': '中国四大发明特写画面：造纸术、印刷术、指南针、火药四样发明组合展示，周围环绕"智"字书法光影，烛光照耀，中国古代智慧结晶，16:9。',

        'scene_05_zhi_modern': '中国航天器发射升空的壮观画面：火箭腾空而起，火焰和烟雾，周围环绕科技线条和数据流，中国航天梦，未来主义蓝色光线，16:9。',

        'scene_06_xin_principle': '中国传统红色印章按下的瞬间特写：印章泥印鲜红，"信"字清晰可见，墨迹未干的契约文书，稳重构图，中国传统诚信象征，16:9。',

        'scene_06_xin_modern': '两位中国人握手的温暖特写：手部握手动作，背景虚化，柔和光线照耀，信任和友谊的象征，现代中国生活场景，16:9。',

        'scene_07_heritage_education': '中国祖孙三代共读经典的温馨特写：古籍书页，三代人的手一起翻动书页，柔和金色光线，文化传承的温暖画面，16:9。',

        'scene_07_grand_finale': '中国壮丽山河全景："文脉薪传 生生不息"八个毛笔大字占据画面中央，背景是日出东方的中国山河，金色阳光普照大地，IMAX史诗级画面，16:9超高清。'
    }

    return keyframe_prompts.get(scene_id, f'中国文化主题关键帧，{narration[:50]}的核心画面，电影级构图，16:9超高清。')


def main():
    """主函数"""
    print("=" * 60)
    print("🎬 为每个分镜生成关键帧图像")
    print("=" * 60)

    # 初始化生成器
    api_key = "sk-KfCX4tI7rDBtC7mynLmFj1z9D90HaO1oCQrVt61y9EXQ2vs1"
    generator = QingyunImageGenerator(api_key=api_key)

    # 加载脚本
    script_data = generator.load_script('./文脉薪传_细化脚本.yaml')
    scenes = generator.extract_scenes(script_data)

    # 输出目录
    keyframe_dir = Path('./storyboards/文脉薪传/keyframes')
    keyframe_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n✅ 找到 {len(scenes)} 个场景")
    print(f"🎨 为每个场景生成关键帧图像")
    print(f"📁 输出目录: {keyframe_dir}\n")

    success_count = 0
    failed_scenes = []

    for i, scene in enumerate(scenes, 1):
        scene_id = scene['id']
        keyframe_path = keyframe_dir / f"{scene_id}_keyframe.png"

        print(f"🎬 [{i}/{len(scenes)}] {scene_id}")

        if keyframe_path.exists():
            print(f"   ⏭️  关键帧已存在，跳过\n")
            success_count += 1
            continue

        try:
            # 生成关键帧提示词
            prompt = create_keyframe_prompt(scene)
            print(f"   📝 关键帧提示词: {prompt[:80]}...")

            # 生成图像
            print(f"   🚀 生成中...")
            image_url = generator.generate_image(prompt)

            # 下载
            print(f"   📥 下载中...")
            generator.download_image(image_url, str(keyframe_path))

            print(f"   ✅ 完成\n")
            success_count += 1

            # 等待一下避免API限流
            import time
            if i < len(scenes):
                print(f"   ⏳ 等待3秒...\n")
                time.sleep(3)

        except Exception as e:
            print(f"   ❌ 失败: {str(e)}\n")
            failed_scenes.append(scene_id)
            continue

    print("=" * 60)
    print(f"✅ 关键帧生成完成！成功 {success_count}/{len(scenes)} 张")

    if failed_scenes:
        print(f"\n⚠️  失败场景：")
        for sid in failed_scenes:
            print(f"   - {sid}")

    print(f"\n📁 输出目录: {keyframe_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()

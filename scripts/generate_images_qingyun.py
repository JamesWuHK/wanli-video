#!/usr/bin/env python3
"""
使用青云API生成分镜设计图 - 豆包模型版
使用 doubao-seedream-4-0-250828 模型（支持中文汉字准确渲染）
参考：https://api.qingyuntop.top/about
"""

import os
import json
import requests
import time
from pathlib import Path
from typing import Dict, List
import yaml


class QingyunImageGenerator:
    """青云API图像生成器 - 豆包模型（支持中文汉字）"""

    def __init__(self, api_key: str = None):
        """初始化"""
        self.api_key = api_key or os.getenv("QINGYUN_API_KEY")
        if not self.api_key:
            raise ValueError("需要提供 QINGYUN_API_KEY")

        self.base_url = "https://api.qingyuntop.top/v1"
        print(f"✅ 青云API已配置 - 豆包模型（汉字支持）")

    def load_script(self, script_path: str) -> Dict:
        """加载脚本"""
        with open(script_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def extract_scenes(self, script_data: Dict) -> List[Dict]:
        """提取场景"""
        scenes = []
        for scene in script_data.get('scenes', []):
            scenes.append({
                'id': scene['id'],
                'prompt_en': scene.get('image_generation_prompt', ''),
                'narration': scene.get('narration', ''),
                'storyboard': scene.get('storyboard', {})
            })
        return scenes

    def create_chinese_prompt(self, scene: Dict) -> str:
        """创建纯中文提示词 - 强调中国场景和中国人物"""
        scene_id = scene['id']
        narration = scene['narration']

        # 纯中文提示词，所有场景都是中国，人物都是中国人
        prompts = {
            'scene_01_opening': '中国古代书院，清晨阳光透过木质窗棂。中国老学者身穿传统长袍翻开古籍《论语》，书页上有工整的"仁义礼智信"五个毛笔大字。水墨画美学，暖色调，电影级光影，16:9超高清画面。',

            'scene_02_ren_intro': '中国传统水墨画风格，画面中央是优美的"仁"字书法。孔子和中国弟子们围坐在古树下论道，竹林背景，微风吹动竹叶。黑白水墨渲染，点缀翠绿色，中国传统绘画美学，16:9。',

            'scene_02_ren_modern': '中国现代温馨生活场景：中国志愿者扶中国老人过马路，中国医护人员救治中国病患，中国邻里互助共度佳节，中国年轻人献血。暖色调，金黄色光线，纪实摄影风格，现代中国城市背景，16:9。',

            'scene_03_yi_history': '中国历史画卷风格，画面中央是金色"义"字书法。中国历史人物：孟子端坐讲学、文天祥正气凛然、岳飞背刺"精忠报国"。史诗级电影光影，古铜金和深红色调，中国传统历史绘画美学，16:9。',

            'scene_03_yi_modern': '中国现代正义场景：中国法官敲响法槌公正判案，中国警察维护秩序，中国市民见义勇为帮助遇险者，中国律师坚定辩护。纪实摄影风格，强烈明暗对比，中国当代场景，电影级构图，16:9。',

            'scene_04_li_tradition': '中国传统礼仪场景，画面中央是工整楷书"礼"字。中国古代祭祀典礼，身穿传统服饰的中国人拱手作揖，成人礼冠冕加身。中轴对称构图，深蓝色和金色配色，中国传统礼仪美学，16:9。',

            'scene_04_li_modern': '中国现代文明礼仪场景：中国学生向中国老师鞠躬致敬，中国家庭聚餐晚辈为长辈敬茶，中国人在公共场所文明礼让，中国传统婚礼新人行礼。柔和暖色调，温馨氛围，中国现代生活场景，16:9。',

            'scene_05_zhi_ancient': '中国古代求学场景，画面中央是灵动行书"智"字。中国古代学子寒窗苦读，烛光摇曳，中国四大发明展示：造纸术、印刷术、指南针、火药。暗黑学术氛围，金色烛光，中国传统书房美学，16:9。',

            'scene_05_zhi_modern': '中国现代科技创新场景：中国学生在高科技图书馆学习，中国科研人员做实验，中国人工智能量子计算机，中国航天器发射升空。未来主义蓝色光线，科技线条和粒子效果，中国现代科技场景，16:9。',

            'scene_06_xin_principle': '中国诚信主题传统场景，画面中央是稳重隶书"信"字。中国古代商人一诺千金，握手签约，传统红色印章泥印鲜明。大地棕色和金色配色，稳重构图，中国传统诚信文化美学，16:9。',

            'scene_06_xin_modern': '中国现代生活场景：两位中国人友好握手互相信任，中国家庭成员之间温暖的信任眼神，朋友之间真诚的交流。柔和光线，温馨氛围，现代中国生活场景，16:9。',

            'scene_07_heritage_education': '中国文化传承场景：中国教师在课堂向中国学生讲述儒家文化，中国祖孙三代共读经典古籍，中国年轻人实践传统美德，中国老少同堂其乐融融。柔和金色光线，温馨家庭氛围，中国家庭文化传承场景，16:9。',

            'scene_07_grand_finale': '史诗级升华镜头：从中国温馨家庭画面拉远，展现中国壮丽山河。日出东方，金色阳光洒满中国大地。画面中央浮现毛笔书法"文脉薪传 生生不息"八个大字，背景是中国山河风光。IMAX电影级别，16:9超高清。'
        }

        return prompts.get(scene_id, f'中国传统文化主题，{narration[:100]}，中国场景，中国人物，电影级画面，16:9超高清。')

    def generate_image(self, prompt: str, model: str = "doubao-seedream-4-0-250828") -> str:
        """生成图像 - 使用豆包模型（支持中文汉字）"""
        url = f"{self.base_url}/images/generations"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # 豆包模型参数（根据API规范）
        data = {
            "model": model,
            "prompt": prompt[:2000],
            "n": 1,
            "size": "2048x1152",  # 16:9比例，适合视频
            "sequential_image_generation": "disabled",
            "watermark": True,
            "stream": False,
            "response_format": "url"
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=180)

            if response.status_code == 200:
                result = response.json()
                return result['data'][0]['url']
            else:
                error_msg = response.text
                try:
                    error_json = response.json()
                    error_msg = error_json.get('error', {}).get('message', error_msg)
                except:
                    pass
                raise Exception(f"API错误 ({response.status_code}): {error_msg}")

        except Exception as e:
            raise Exception(f"生成失败: {str(e)}")

    def download_image(self, url: str, output_path: str):
        """下载图像"""
        response = requests.get(url, timeout=60)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
        else:
            raise Exception(f"下载失败: {response.status_code}")

    def generate_all_images(self, script_path: str, output_dir: str, delay: int = 3):
        """生成所有图像"""
        print(f"\n📖 加载脚本: {script_path}")
        script_data = self.load_script(script_path)

        scenes = self.extract_scenes(script_data)
        print(f"✅ 找到 {len(scenes)} 个场景")
        print(f"🎨 使用模型: doubao-seedream-4-0-250828 (豆包)")
        print(f"💡 豆包模型支持准确渲染中文汉字")
        print(f"📐 图像尺寸: 2048x1152 (16:9)\n")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        success_count = 0
        failed_scenes = []

        for i, scene in enumerate(scenes, 1):
            scene_id = scene['id']
            print(f"🎨 [{i}/{len(scenes)}] {scene_id}")

            img_path = output_path / f"{scene_id}.png"

            if img_path.exists():
                print(f"   ⏭️  已存在，跳过\n")
                success_count += 1
                continue

            try:
                # 生成中英文混合提示词
                prompt = self.create_chinese_prompt(scene)
                print(f"   📝 提示词: {prompt[:80]}...")

                # 生成图像
                print(f"   🚀 生成中...")
                image_url = self.generate_image(prompt, "doubao-seedream-4-0-250828")

                # 下载
                print(f"   📥 下载中...")
                self.download_image(image_url, str(img_path))

                print(f"   ✅ 完成\n")
                success_count += 1

                if i < len(scenes):
                    print(f"   ⏳ 等待{delay}秒...\n")
                    time.sleep(delay)

            except Exception as e:
                print(f"   ❌ 失败: {str(e)}\n")
                failed_scenes.append(scene_id)
                continue

        print("=" * 60)
        print(f"✅ 完成！成功 {success_count}/{len(scenes)} 张")

        if failed_scenes:
            print(f"\n⚠️  失败场景：")
            for sid in failed_scenes:
                print(f"   - {sid}")

        print(f"\n📁 输出: {output_dir}")
        print("=" * 60)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--script", default="./文脉薪传_细化脚本.yaml")
    parser.add_argument("--output", default="./storyboards/文脉薪传/final_images")
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--delay", type=int, default=3)

    args = parser.parse_args()

    print("=" * 60)
    print("🎨 青云API图像生成器 - 豆包模型")
    print("=" * 60)

    try:
        generator = QingyunImageGenerator(api_key=args.api_key)
        generator.generate_all_images(args.script, args.output, args.delay)

        print("\n💡 说明：")
        print("  - 使用豆包 doubao-seedream-4-0-250828 模型")
        print("  - 豆包模型可以准确渲染中文汉字")
        print("  - 图像尺寸: 2048x1152 (16:9比例)")
        print("  - 中英文混合提示词，优化效果")

    except ValueError as e:
        print(f"\n❌ 错误: {e}")
        print("请设置 QINGYUN_API_KEY 或使用 --api-key 参数")


if __name__ == "__main__":
    main()

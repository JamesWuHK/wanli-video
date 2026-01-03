#!/usr/bin/env python3
"""
使用支持中文的图像生成服务
推荐: 豆包(Doubao)、通义万相、文心一格
这些模型对中文汉字的支持远好于DALL-E
"""

import os
import json
import requests
import time
from pathlib import Path
from typing import Dict, List
import yaml


class ChineseImageGenerator:
    """中文友好的图像生成器"""

    def __init__(self, api_key: str = None, service: str = "qingyun"):
        """初始化

        Args:
            api_key: API密钥
            service: 服务类型 (qingyun, tongyi, wenxin)
        """
        self.api_key = api_key or os.getenv("QINGYUN_API_KEY")
        if not self.api_key:
            raise ValueError("需要提供 API Key")

        self.service = service
        self.base_url = "https://api.qingyuntop.top/v1"

        print(f"✅ 使用服务: {service}")
        print(f"   密钥: {self.api_key[:15]}...")

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
                'duration': scene.get('duration', 0),
                'storyboard': scene.get('storyboard', {})
            })
        return scenes

    def translate_prompt_to_chinese(self, scene: Dict) -> str:
        """将提示词转换为中文，并突出汉字要求

        为中文模型优化的提示词，特别强调汉字的正确显示
        """
        scene_id = scene['id']
        narration = scene['narration']
        storyboard = scene['storyboard']

        # 根据场景ID定制中文提示词
        if 'opening' in scene_id:
            prompt = f"""
一个宁静的中国古代书院，清晨阳光透过传统木质窗棂。
画面中心：一位身穿传统长袍的老学者正在翻开泛黄的古籍《论语》。
镜头缓缓推进至书页上的五个毛笔大字："仁义礼智信"。
这五个汉字必须清晰、正确、工整，使用传统书法字体。
氛围：电影级光影，水墨画美学，温暖的棕褐色调。
画面比例16:9，高清细节，8K质量。
关键要求：汉字"仁义礼智信"必须准确无误！
"""
        elif 'ren' in scene_id and 'intro' in scene_id:
            prompt = f"""
中国传统水墨画风格。
画面中央："仁"字以优美的书法形式呈现，笔画清晰。
场景：孔子与弟子围坐在古树下讨论哲学，杏坛论道。
背景：竹林，微风吹动竹叶。
画风：水墨渲染，黑白为主，点缀翠绿色。
构图：留白艺术，中国传统绘画美学。
关键要求：汉字"仁"必须准确清晰！
"""
        elif 'ren' in scene_id and 'modern' in scene_id:
            prompt = f"""
温馨的现代生活场景蒙太奇：
1. 志愿者扶助老人过马路
2. 医护人员全力救治病患
3. 邻里之间互相帮助，共度佳节
4. 年轻人献血，关爱生命
暖色调，金黄色光线，纪实摄影风格。
中国人物，现代城市背景。
情感：温暖、感人。
"""
        elif 'yi' in scene_id and 'history' in scene_id:
            prompt = f"""
中国历史画卷风格。
画面中央："义"字以金色书法呈现，笔画刚劲有力。
历史人物：
- 孟子端坐讲学，神态坚毅
- 文天祥正气凛然
- 岳飞背刺"精忠报国"的剪影
史诗级电影光影，古铜金和深红色调。
画面比例16:9，传统中国历史绘画美学。
关键要求：汉字"义"和"精忠报国"必须准确！
"""
        elif 'yi' in scene_id and 'modern' in scene_id:
            prompt = f"""
现代正义主题场景：
1. 法官敲响法槌，公正判案
2. 警察维护秩序，保护群众
3. 普通市民见义勇为，帮助遇险者
4. 律师为弱者辩护的坚定眼神
纪实摄影风格，强烈明暗对比。
中国当代场景，电影级构图。
"""
        elif 'li' in scene_id and 'tradition' in scene_id:
            prompt = f"""
庄重的中国传统礼仪场景。
画面中央："礼"字以工整楷书呈现，对称美感。
场景：
- 古代祭祀典礼，仪式感庄重
- 传统拱手作揖，礼节到位
- 成人礼冠冕加身的神圣时刻
中轴对称构图，深蓝色和金色配色。
传统中国礼仪美学。
关键要求：汉字"礼"必须准确工整！
"""
        elif 'li' in scene_id and 'modern' in scene_id:
            prompt = f"""
温馨的现代文明礼仪场景：
1. 学生向老师鞠躬致敬
2. 家庭聚餐，晚辈为长辈敬茶
3. 公共场所文明礼让，排队有序
4. 传统婚礼，新人行礼
柔和暖色调，温馨生活氛围。
中国现代家庭和社会场景。
"""
        elif 'zhi' in scene_id and 'ancient' in scene_id:
            prompt = f"""
中国古代求学场景。
画面中央："智"字以灵动行书呈现，富有变化。
场景：
- 古代学子寒窗苦读，烛光摇曳
- 四大发明展示：造纸术、印刷术、指南针、火药
- 古籍经典翻动
暗黑学术氛围，金色烛光。
传统中国书房美学。
关键要求：汉字"智"必须准确！
"""
        elif 'zhi' in scene_id and 'modern' in scene_id:
            prompt = f"""
现代科技创新场景：
1. 学生在高科技图书馆专注学习
2. 科研人员做实验，数据可视化
3. 人工智能、量子计算机特写
4. 航天器发射升空
未来主义蓝色光线，科技线条和粒子效果。
中国现代科技场景，电影级科幻美学。
"""
        elif 'xin' in scene_id and 'principle' in scene_id:
            prompt = f"""
诚信主题的传统场景。
画面中央："信"字以稳重隶书呈现，笔画扎实。
场景：
- 古代商人一诺千金的场景
- 握手签约，象征承诺
- 传统红色印章，泥印鲜明
大地棕色和金色配色，稳重构图。
传统中国诚信文化美学。
关键要求：汉字"信"必须准确！
"""
        elif 'xin' in scene_id and 'modern' in scene_id:
            prompt = f"""
现代诚信社会场景：
1. 企业家诚信签约的庄重仪式
2. 店铺诚信经营，童叟无欺
3. 数字化社会信用体系可视化
4. 人与人之间信任的眼神
纪实摄影风格，温暖可信的光线。
中国当代社会场景。
"""
        elif 'heritage' in scene_id:
            prompt = f"""
温馨的文化传承场景：
1. 教师在课堂向学生讲述儒家文化
2. 祖孙三代共读经典古籍
3. 年轻人在日常生活中实践传统美德
4. 老少同堂，其乐融融
柔和金色光线，温暖家庭氛围。
中国家庭文化传承场景。
"""
        elif 'finale' in scene_id:
            prompt = f"""
史诗级升华镜头：
从温馨家庭画面拉远，展现中国壮丽山河。
日出东方，金色阳光洒满大地。
画面中央浮现毛笔书法："文脉薪传 生生不息"
这八个汉字必须清晰、工整、准确。
背景虚化的山河风光。
IMAX电影级别，8K质量。
关键要求：汉字"文脉薪传 生生不息"必须准确无误！
"""
        else:
            # 默认提示词
            prompt = f"""
中国传统文化主题场景。
旁白：{narration}
水墨画和现代影像融合风格。
16:9画面比例，高清细节。
"""

        return prompt.strip()

    def generate_with_model(self, prompt: str, model: str = "cogview-3-plus") -> str:
        """使用指定模型生成图像

        青云API支持的中文友好模型：
        - cogview-3-plus (智谱清言，中文很好)
        - wenxin (文心一格)
        - tongyi-wanxiang (通义万相)
        """
        url = f"{self.base_url}/images/generations"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": model,
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",  # 根据模型调整
            "response_format": "url"
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=120)

            if response.status_code == 200:
                result = response.json()
                image_url = result['data'][0]['url']
                return image_url
            else:
                error_msg = response.text
                try:
                    error_json = response.json()
                    error_msg = error_json.get('error', {}).get('message', error_msg)
                except:
                    pass
                raise Exception(f"生成失败 ({response.status_code}): {error_msg}")

        except Exception as e:
            raise Exception(f"API调用错误: {str(e)}")

    def download_image(self, url: str, output_path: str):
        """下载图像"""
        try:
            response = requests.get(url, timeout=60)
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return True
            else:
                raise Exception(f"下载失败: HTTP {response.status_code}")
        except Exception as e:
            raise Exception(f"下载错误: {str(e)}")

    def generate_all_images(
        self,
        script_path: str,
        output_dir: str,
        model: str = "cogview-3-plus",
        delay: int = 3
    ):
        """生成所有场景图像"""
        print(f"\n📖 加载脚本: {script_path}")
        script_data = self.load_script(script_path)

        scenes = self.extract_scenes(script_data)
        print(f"✅ 找到 {len(scenes)} 个场景")
        print(f"🎨 使用模型: {model} (支持中文汉字)")
        print(f"⏱️  生成间隔: {delay}秒\n")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        success_count = 0
        failed_scenes = []

        for i, scene in enumerate(scenes, 1):
            scene_id = scene['id']
            print(f"🎨 [{i}/{len(scenes)}] {scene_id}")
            print(f"   旁白: {scene['narration'][:50]}...")

            img_path = output_path / f"{scene_id}.png"

            if img_path.exists():
                print(f"   ⏭️  已存在，跳过\n")
                success_count += 1
                continue

            try:
                # 生成中文优化的提示词
                print(f"   📝 生成中文提示词...")
                prompt_cn = self.translate_prompt_to_chinese(scene)
                print(f"   提示词预览: {prompt_cn[:100]}...")

                # 生成图像
                print(f"   🚀 调用API生成图像...")
                image_url = self.generate_with_model(prompt_cn, model)

                # 下载图像
                print(f"   📥 下载图像...")
                self.download_image(image_url, str(img_path))

                print(f"   ✅ 成功保存\n")
                success_count += 1

                if i < len(scenes):
                    print(f"   ⏳ 等待 {delay} 秒...\n")
                    time.sleep(delay)

            except Exception as e:
                print(f"   ❌ 失败: {str(e)}\n")
                failed_scenes.append(scene_id)
                continue

        print("=" * 60)
        print(f"✅ 完成！成功生成 {success_count}/{len(scenes)} 张图像")

        if failed_scenes:
            print(f"\n⚠️  以下场景生成失败：")
            for scene_id in failed_scenes:
                print(f"   - {scene_id}")

        print(f"\n📁 输出目录: {output_dir}")
        print("=" * 60)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="使用中文友好模型生成图像")
    parser.add_argument("--script", default="./文脉薪传_细化脚本.yaml")
    parser.add_argument("--output", default="./storyboards/文脉薪传/chinese_ai_images")
    parser.add_argument(
        "--model",
        default="cogview-3-plus",
        help="模型: cogview-3-plus(推荐), wenxin, tongyi-wanxiang"
    )
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--delay", type=int, default=3)

    args = parser.parse_args()

    print("=" * 60)
    print("🎨 中文图像生成器 (汉字友好)")
    print("=" * 60)

    try:
        generator = ChineseImageGenerator(api_key=args.api_key)
        generator.generate_all_images(args.script, args.output, args.model, args.delay)

        print("\n💡 提示:")
        print("  - 本脚本使用中文优化的模型")
        print("  - 汉字显示准确率远高于DALL-E")
        print("  - 特别优化了'仁义礼智信'等关键汉字")

    except ValueError as e:
        print(f"\n❌ 错误: {e}")


if __name__ == "__main__":
    main()

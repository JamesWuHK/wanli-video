#!/usr/bin/env python3
"""
重新生成需要加强人物动作的场景视频
"""

import requests
import time
import base64
from pathlib import Path

API_KEY = "sk-hSsIao5zgH3uctxxJqWZOezaSW2HZWFTf8HHJQgL6mav6cpJ"
BASE_URL = "https://api.vectorengine.ai"

SCENES = [
    {
        "id": "scene_02_ren_intro",
        "image": "storyboards/文脉薪传/doubao_images/scene_02_ren_intro.png",
        "output": "videos/scene_02_ren_intro_runway_v2.mp4",
        "prompt": """A serene ink wash painting style scene depicting Confucius teaching under the ancient apricot tree. The great sage sits on a low wooden platform surrounded by students in traditional Han dynasty robes. The large Chinese character "仁" (benevolence) is prominently displayed in elegant calligraphy.

Dynamic character movements:
- Confucius's hands move expressively as he teaches, gesturing to emphasize key points
- His fingers open and close gracefully while explaining concepts
- Students actively lean forward, their heads nodding repeatedly in understanding
- Multiple students' hands move simultaneously - some taking notes with brushes, others adjusting sitting positions
- One student raises his hand to ask a question
- Confucius turns his head slightly to address different students
- Students' eyes follow the teacher's movements attentively
- Breathing motions visible in chest and shoulders of all figures
- Robes flutter noticeably from gentle breeze

Environmental movements:
- Ink wash clouds drift across the sky
- Bamboo leaves sway rhythmically in the background
- The character "仁" pulses with a soft glow
- Subtle ink diffusion effects spread at the edges
- Light shifts across the scene creating atmospheric depth

Camera movement:
- Slow zoom-in from wide view to closer emphasis on Confucius and "仁"
- Smooth, contemplative motion maintaining ink wash aesthetic
- Balanced composition highlighting both teacher and sacred character

Atmosphere:
- Tranquil scholarly mood with sepia tones and soft ink blacks
- Traditional Chinese ink painting aesthetic with flowing brushwork
- Misty, dreamlike quality suggesting ancient wisdom
- Warm gentle lighting creating timeless feeling
- Preserve all Chinese text exactly as shown, especially "仁"

Duration: 10 seconds"""
    },
    {
        "id": "scene_03_yi_history",
        "image": "storyboards/文脉薪传/doubao_images/scene_03_yi_history.png",
        "output": "videos/scene_03_yi_history_runway_v2.mp4",
        "prompt": """A dramatic historical scene depicting righteousness. Ancient Chinese warriors in traditional armor and robes stand firm in moral conviction. The large character "义" dominates the upper portion in bold calligraphy. Ink wash mountains and mist create a heroic backdrop.

Dynamic character movements:
- The main warrior's robes billow dramatically and continuously from strong wind
- His hand grips the sword hilt firmly, fingers adjusting grip multiple times
- He takes a strong stance, shifting weight purposefully
- His head turns slowly, surveying the landscape with determination
- Eyes blink and gaze shifts showing unwavering resolve
- Chest rises and falls with steady, resolute breathing
- His cape flows and whips in the wind
- Other warriors in background shift stances, maintaining vigilance
- Hands rest on weapons, ready for action
- One warrior steps forward, taking a defensive position

Environmental movements:
- Banners and flags wave vigorously in the wind
- Ink wash clouds drift across mountainous landscape
- The character "义" radiates with inner strength and glow effects
- Mist flows dramatically across lower portions
- Dust or particles swirl in the air

Camera movement:
- Dramatic push-in from wide heroic vista
- Moving closer to main figure and "义"
- Strong steady movement suggesting unwavering righteousness
- Slight upward tilt emphasizing nobility and moral high ground

Atmosphere:
- Heroic dramatic mood with strong contrast and deep blacks
- Traditional ink painting aesthetic with bold brushwork
- Misty mountain atmosphere suggesting lofty ideals
- Cool blue and gray tones mixed with warm highlights
- Preserve all Chinese text exactly as shown, especially "义"

Duration: 10 seconds"""
    },
    {
        "id": "scene_04_li_modern",
        "image": "storyboards/文脉薪传/doubao_images/scene_04_li_modern.png",
        "output": "videos/scene_04_li_modern_runway_v2.mp4",
        "prompt": """A contemporary multi-panel composition showing modern etiquette and propriety. Students bow respectfully to teachers, family members show courtesy at home, and formal occasions like weddings observe traditional manners. The character "礼" is displayed in modern styling.

Dynamic character movements:
- Students perform full bowing motions - bending forward at the waist, then straightening up
- Teacher nods acknowledgment with warm, appreciative gestures, hands moving
- Family members at dinner table actively pass dishes with careful hand movements
- Chopsticks move gracefully from dishes to bowls
- Wedding participants perform slow, graceful bowing ceremonies - multiple people bowing together
- Hands clasp together in respectful gestures, fingers interlacing
- People's faces show genuine smiles, eyes crinkling warmly
- Heads turn to make eye contact between people
- Bodies lean slightly toward each other showing engagement
- A child reaches up to receive something from an elder
- Clothing moves naturally with polite body language

Environmental movements:
- The character "礼" glows softly radiating warmth of mutual respect
- Slight depth of field shifts emphasizing different acts of courtesy
- Natural light shifts across faces highlighting emotions
- Soft shadows move with character movements

Camera movement:
- Gentle pan across various modern etiquette scenes
- Smooth transitions between home, school, and formal settings
- Warm approachable movement suggesting everyday civility
- Settles on harmonious composition unifying all forms of modern propriety

Atmosphere:
- Warm harmonious mood with contemporary color palette
- Natural inviting lighting in modern settings
- Clean bright aesthetic representing positive social interactions
- Emphasis on genuine human warmth and mutual respect
- Preserve all Chinese text exactly as shown, especially "礼"

Duration: 10 seconds"""
    },
    {
        "id": "scene_06_xin_principle",
        "image": "storyboards/文脉薪传/doubao_images/scene_06_xin_principle.png",
        "output": "videos/scene_06_xin_principle_runway_v2.mp4",
        "prompt": """A traditional marketplace depicting trustworthiness. Honest merchants conduct fair trades, customers and sellers exchange goods with integrity. The character "信" is displayed in trustworthy calligraphy. Traditional shop fronts, scales for fair measurement, and ledger books emphasize honest dealings.

Dynamic character movements:
- Merchant's hands actively place goods on scale, adjusting carefully
- Fingers count coins methodically one by one with transparent gestures
- Two hands reach out and shake firmly in agreement, moving up and down
- Shopkeeper's brush moves across ledger book writing careful entries
- Customer picks up goods, examines them closely, turning them over in hands
- Hands present products with open, honest welcoming gestures
- Merchant pours tea into cups for customers
- People bow slightly to each other in respectful greeting
- A customer nods head vigorously showing satisfaction with quality
- Hands reach out to pass goods from seller to buyer
- Sleeves and robes move with business transactions
- Eyes make direct contact showing mutual trust

Environmental movements:
- Shop signs and banners sway gently in the breeze
- The character "信" radiates with steady reliable light
- Steam rises from tea being served to seal agreements
- Incense smoke drifts in the shop
- Natural marketplace activity in background

Camera movement:
- Steady straightforward movement suggesting honesty and transparency
- Gentle pan across traditional marketplace scene
- Push-in to emphasize moments of trust and fair dealing
- Reliable consistent camera work matching theme of trustworthiness

Atmosphere:
- Warm trustworthy mood with earthy browns and honest golds
- Natural marketplace lighting suggesting open transparent dealings
- Traditional commercial aesthetic with attention to fair trade practices
- Sense of integrity, reliability, and keeping one's word
- Preserve all Chinese text exactly as shown, especially "信"

Duration: 10 seconds"""
    },
    {
        "id": "scene_07_grand_finale",
        "image": "storyboards/文脉薪传/doubao_images/scene_07_grand_finale.png",
        "output": "videos/scene_07_grand_finale_runway_v2.mp4",
        "prompt": """An epic majestic finale showing China's vast mountains and rivers at sunrise. Dramatic mountain ranges with morning mist, golden sunrise breaking over peaks, and powerful characters "文脉薪传 生生不息" displayed prominently. A FAMILY OF FOUR (parents and two children) stands in the foreground on a hilltop viewing the landscape.

Dynamic character movements:
- The father points toward the horizon, his arm extending fully
- Mother places her hand on one child's shoulder, patting gently
- Both children turn their heads looking up at parents then back to the view
- The younger child jumps slightly with excitement
- The older child raises their arm pointing at something in the distance
- All four figures' hair and clothing blow in the morning breeze
- Parents hold hands with children, arms swinging slightly
- Family members shift weight, adjusting stance on the hilltop
- One child leans forward excitedly while being held back gently by parent
- All figures breathe, chest and shoulders showing motion
- Heads turn as they take in the vast landscape

Environmental movements:
- Morning mist flows slowly through mountain valleys like rivers of cloud
- Rising sun gradually brightens, rays of light expanding across sky
- Clouds drift majestically across mountain peaks
- Light beams pierce through mist creating divine rays (crepuscular rays)
- Characters "文脉薪传 生生不息" glow with increasing intensity
- Mountain silhouettes become more defined as light increases
- Subtle atmospheric haze shifts and swirls in valleys
- Birds fly in the distance suggesting life and continuity
- Water surfaces reflect changing morning light with gentle ripples
- Scene gradually brightens from pre-dawn to full morning glory
- Ink wash effects at edges pulse gently

Camera movement:
- Majestic slow push-in starting from grand wide vista
- Reverent upward tilt following mountain peaks toward rising sun
- Smooth epic movement suggesting timelessness and grandeur
- Gradually centers on powerful characters against magnificent backdrop
- Ending with balanced powerful composition inspiring hope and continuity

Atmosphere:
- Epic inspiring mood with golden sunrise colors, deep blues, majestic purples
- Dramatic natural lighting from breaking dawn
- Blend of photorealistic landscape with traditional ink wash painting aesthetics
- Sense of timelessness, continuity, natural grandeur, and cultural pride
- Emotional crescendo suggesting eternal vitality of Chinese civilization
- Preserve all Chinese text exactly as shown, especially "文脉薪传 生生不息"

Duration: 10 seconds"""
    }
]

def image_to_base64(image_path):
    """将图片转换为 base64 编码的 data URL"""
    with open(image_path, 'rb') as f:
        image_data = f.read()
    base64_str = base64.b64encode(image_data).decode('utf-8')
    return f"data:image/png;base64,{base64_str}"

def submit_task(scene):
    """提交图生视频任务"""
    print(f"\n{'='*80}")
    print(f"正在处理场景: {scene['id']}")
    print(f"{'='*80}")

    image_path = Path(scene['image'])
    if not image_path.exists():
        print(f"❌ 错误: 图片文件不存在: {image_path}")
        return None

    print(f"📷 图片: {image_path}")
    print(f"📝 提示词: 英文版本，强化人物动作")

    image_data_url = image_to_base64(image_path)

    payload = {
        "promptImage": image_data_url,
        "model": "gen4_turbo",
        "promptText": scene['prompt'],
        "watermark": False,
        "duration": 10,
        "ratio": "1280:768"
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    print(f"\n🚀 提交任务到 Runway API...")
    try:
        response = requests.post(
            f"{BASE_URL}/runwayml/v1/image_to_video",
            headers=headers,
            json=payload,
            timeout=30
        )

        print(f"📡 响应状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            task_id = result.get('id')
            if task_id:
                print(f"✅ 任务提交成功!")
                print(f"📋 Task ID: {task_id}")
                return {
                    "scene_id": scene['id'],
                    "task_id": task_id,
                    "output_path": scene['output'],
                    "submit_time": time.time()
                }
            else:
                print(f"❌ 响应中没有找到 task_id")
                print(f"📄 响应内容: {response.text}")
                return None
        else:
            print(f"❌ 提交失败: HTTP {response.status_code}")
            print(f"📄 响应内容: {response.text}")
            return None

    except Exception as e:
        print(f"❌ 提交任务时出错: {e}")
        return None

def check_task_status(task_id):
    """查询任务状态"""
    headers = {"Authorization": f"Bearer {API_KEY}"}
    try:
        response = requests.get(
            f"{BASE_URL}/runwayml/v1/tasks/{task_id}",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

def download_video(video_url, output_path):
    """下载生成的视频"""
    try:
        response = requests.get(video_url, timeout=60)
        if response.status_code == 200:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'wb') as f:
                f.write(response.content)

            file_size = output_file.stat().st_size / (1024 * 1024)
            print(f"✅ 视频已保存: {output_path}")
            print(f"📦 文件大小: {file_size:.1f} MB")
            return True
        else:
            print(f"❌ 下载失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 下载视频时出错: {e}")
        return False

def main():
    print("="*80)
    print("文脉薪传 - 重新生成加强人物动作的视频")
    print("="*80)
    print(f"\n需要重新生成 {len(SCENES)} 个场景")
    print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # 批量提交任务
    print("\n" + "="*80)
    print("第一阶段：提交所有任务")
    print("="*80)

    tasks = []
    for i, scene in enumerate(SCENES, 1):
        print(f"\n[{i}/{len(SCENES)}] ", end="")
        task = submit_task(scene)
        if task:
            tasks.append(task)
        time.sleep(2)

    print(f"\n✅ 成功提交 {len(tasks)}/{len(SCENES)} 个任务")

    if not tasks:
        print("❌ 没有成功提交的任务")
        return

    # 监控任务
    print("\n" + "="*80)
    print("第二阶段：监控任务进度")
    print("="*80)

    completed_tasks = []
    failed_tasks = []
    max_wait_time = 600

    while tasks:
        for task in tasks[:]:
            elapsed = time.time() - task['submit_time']

            if elapsed > max_wait_time:
                print(f"\n⏱️ 任务 {task['scene_id']} 超时")
                failed_tasks.append(task)
                tasks.remove(task)
                continue

            result = check_task_status(task['task_id'])

            if result:
                status = result.get('status', 'UNKNOWN')

                if status in ['completed', 'succeed', 'success', 'SUCCEEDED']:
                    print(f"\n✅ 任务完成: {task['scene_id']}")

                    video_url = result.get('url') or result.get('video_url')
                    if not video_url and 'output' in result:
                        output = result.get('output')
                        if isinstance(output, list) and len(output) > 0:
                            video_url = output[0]
                        elif isinstance(output, dict):
                            video_url = output.get('video')

                    if video_url:
                        print(f"📥 开始下载视频...")
                        if download_video(video_url, task['output_path']):
                            completed_tasks.append(task)
                        else:
                            failed_tasks.append(task)
                    else:
                        print(f"❌ 未找到视频 URL")
                        failed_tasks.append(task)

                    tasks.remove(task)

                elif status in ['failed', 'FAILED', 'error', 'ERROR']:
                    print(f"\n❌ 任务失败: {task['scene_id']}")
                    failed_tasks.append(task)
                    tasks.remove(task)

                else:
                    progress = result.get('progress', 0)
                    print(f"\r⏳ {task['scene_id']}: {status} ({progress}%) - {elapsed:.0f}s", end="", flush=True)

        if tasks:
            time.sleep(5)

    # 总结
    print("\n\n" + "="*80)
    print("重新生成完成 - 总结报告")
    print("="*80)

    print(f"\n✅ 成功生成: {len(completed_tasks)} 个视频")
    for task in completed_tasks:
        print(f"   - {task['scene_id']}")

    if failed_tasks:
        print(f"\n❌ 失败: {len(failed_tasks)} 个视频")
        for task in failed_tasks:
            print(f"   - {task['scene_id']}")

    print(f"\n结束时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

if __name__ == "__main__":
    main()

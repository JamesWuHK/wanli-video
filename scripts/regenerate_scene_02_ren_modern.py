#!/usr/bin/env python3
"""
重新生成 scene_02_ren_modern 视频
只保留前2秒的动作效果，后面的镜头保持相对静止
"""

import requests
import time
import base64
import json
from pathlib import Path

# API 配置
API_KEY = "sk-hSsIao5zgH3uctxxJqWZOezaSW2HZWFTf8HHJQgL6mav6cpJ"
BASE_URL = "https://api.vectorengine.ai"

# 场景配置
SCENE = {
    "id": "scene_02_ren_modern",
    "image": "storyboards/文脉薪传/doubao_images/scene_02_ren_modern.png",
    "output": "videos/scene_02_ren_modern_runway_v2.mp4",
    # 调整后的提示词：减少后期的动作，保持相对静止
    "prompt": """一个现代多场景构图，展现当代的仁爱之举。场景包含三个关键片段：年轻志愿者帮助老年人，医护人员以同情心照顾患者，社区成员互相帮助。"仁"字以现代书法风格醒目地出现在构图中。

细微动作（仅在前2秒）：
- 志愿者轻柔地帮助老人站起来，手势充满关怀（前2秒）
- 医护人员以充满同情的肢体语言向患者倾身（前2秒）
- 手在各个画面中伸出，做出帮助和支持的手势（前2秒）
- 人们的头部微微转动进行眼神交流，展现人与人之间的联系（前2秒）

保持稳定（2秒后）：
- 镜头停留在温馨的画面上
- 人物保持相对静止的姿态
- "仁"字柔和发光，保持稳定
- 整体画面维持温暖、和谐的氛围
- 仅有非常轻微的呼吸起伏和自然摆动

镜头运动：
- 前2秒：轻微推进以强调人与人之间的联系和关爱行动
- 2秒后：镜头保持稳定，停留在平衡的构图上
- 整体运动非常缓慢、流畅

氛围：
- 温暖、充满希望的氛围，现代色彩调色
- 柔和的自然光线，暗示白天的社区活动
- 简洁现代的美学与传统价值观融合
- 通过光线强调情感温暖和人际联系
- 精确保留画面中所有中文文字，特别是"仁"字

时长：10秒"""
}


def image_to_base64(image_path):
    """将图片转换为 base64 编码的 data URL"""
    with open(image_path, 'rb') as f:
        image_data = f.read()
    base64_str = base64.b64encode(image_data).decode('utf-8')
    return f"data:image/png;base64,{base64_str}"


def submit_task():
    """提交图生视频任务"""
    print(f"{'='*80}")
    print(f"重新生成场景: {SCENE['id']}")
    print(f"{'='*80}")

    # 读取并编码图片
    image_path = Path(SCENE['image'])
    if not image_path.exists():
        print(f"❌ 错误: 图片文件不存在: {image_path}")
        return None

    print(f"📷 图片: {image_path}")
    print(f"📝 调整策略: 前2秒有动作，后面保持相对静止")
    print(f"📝 提示词长度: {len(SCENE['prompt'])} 字符")

    image_data_url = image_to_base64(image_path)

    # 构建请求
    payload = {
        "promptImage": image_data_url,
        "model": "gen4_turbo",
        "promptText": SCENE['prompt'],
        "watermark": False,
        "duration": 10,
        "ratio": "1280:768"
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # 提交任务
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
                return task_id
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
    headers = {
        "Authorization": f"Bearer {API_KEY}",
    }

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
        print(f"\n📥 开始下载视频...")
        print(f"🔗 视频URL: {video_url}")

        response = requests.get(video_url, timeout=60)
        if response.status_code == 200:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'wb') as f:
                f.write(response.content)

            file_size = output_file.stat().st_size / (1024 * 1024)  # MB
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
    print("重新生成 scene_02_ren_modern 视频")
    print("策略：前2秒保持动作，后面相对静止")
    print("="*80)
    print(f"\n开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # 提交任务
    task_id = submit_task()
    if not task_id:
        print("\n❌ 任务提交失败，程序退出")
        return

    # 监控任务状态
    print(f"\n{'='*80}")
    print("监控任务进度")
    print(f"{'='*80}")

    max_wait_time = 600  # 最多等待 10 分钟
    start_time = time.time()

    while True:
        elapsed = time.time() - start_time

        if elapsed > max_wait_time:
            print(f"\n⏱️ 任务超时 ({max_wait_time/60:.1f} 分钟)")
            return

        result = check_task_status(task_id)

        if result:
            status = result.get('status', 'UNKNOWN')

            if status in ['completed', 'succeed', 'success', 'SUCCEEDED']:
                print(f"\n\n✅ 任务完成!")

                # 获取视频 URL
                video_url = result.get('url') or result.get('video_url')
                if not video_url and 'output' in result:
                    output = result.get('output')
                    if isinstance(output, list) and len(output) > 0:
                        video_url = output[0]
                    elif isinstance(output, dict):
                        video_url = output.get('video')

                if video_url:
                    if download_video(video_url, SCENE['output']):
                        print(f"\n{'='*80}")
                        print("✅ 视频重新生成成功!")
                        print(f"{'='*80}")
                        print(f"\n输出文件: {SCENE['output']}")
                        print(f"结束时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                    else:
                        print(f"\n❌ 视频下载失败")
                else:
                    print(f"\n❌ 未找到视频 URL")
                    print(f"响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
                return

            elif status in ['failed', 'FAILED', 'error', 'ERROR']:
                print(f"\n❌ 任务失败")
                print(f"失败原因: {result.get('failure', result.get('failure_reason', '未知'))}")
                return

            else:
                # 任务仍在进行中
                progress = result.get('progress', 0)
                print(f"\r⏳ 状态: {status} | 进度: {progress}% | 已等待: {elapsed:.0f}s", end="", flush=True)

        time.sleep(5)  # 每 5 秒查询一次


if __name__ == "__main__":
    main()

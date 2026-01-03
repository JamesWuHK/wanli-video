#!/usr/bin/env python3
"""
Runway 首尾帧确定视频生成测试
场景1 → 场景2 过渡

使用 Runway 的正确 API 格式和查询端点
"""

import os
import sys
import time
import base64
import requests
from pathlib import Path

# API配置
API_KEY = "sk-hSsIao5zgH3uctxxJqWZOezaSW2HZWFTf8HHJQgL6mav6cpJ"
BASE_URL = "https://api.vectorengine.ai"

# 图片路径
FIRST_FRAME = Path("storyboards/文脉薪传/doubao_images/scene_01_opening.png")
LAST_FRAME = Path("storyboards/文脉薪传/doubao_images/scene_02_ren_intro.png")
OUTPUT = Path("scene_01_to_02_runway.mp4")

def encode_image(image_path: Path) -> str:
    """将图片编码为base64 data URL"""
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    return f"data:image/png;base64,{image_data}"

def generate_runway_video():
    """使用Runway生成首尾帧确定的视频"""

    print("=" * 60)
    print("🎬 Runway 首尾帧视频生成测试")
    print("=" * 60)

    # 编码图片
    print(f"\n📸 首帧: {FIRST_FRAME.name}")
    print(f"📸 尾帧: {LAST_FRAME.name}")

    first_image_url = encode_image(FIRST_FRAME)

    print(f"   ✅ 图片编码完成 (首帧: {len(first_image_url)//1024}KB)")

    # Runway提示词 - 描述从首帧到尾帧的过渡动作
    prompt = """从古代书院的宁静场景开始，古籍上的'仁义礼智信'五个大字清晰可见。
画面逐渐过渡为水墨晕染效果，墨色从书页中渗透扩散。
镜头缓慢拉远，场景转换为水墨画风格的孔子杏坛论道场景。
'仁'字从虚到实浮现，竹林背景渐显，完成从现实到水墨意境的优雅转场。
保持所有中文文字清晰可见，水墨过渡自然流畅。"""

    print(f"\n📝 提示词:")
    print(f"   {prompt[:80]}...")

    # 尝试不同的 Runway 模型配置
    test_configs = [
        {"model": "gen4_turbo", "duration": 10},
        {"model": "gen3a_turbo", "duration": 10},
        {"model": "gen4_turbo", "duration": 5},
    ]

    for config in test_configs:
        model = config["model"]
        duration = config["duration"]

        print(f"\n{'='*60}")
        print(f"🤖 尝试模型: {model} ({duration}秒)")
        print(f"{'='*60}")

        # 构建 Runway 格式的 payload
        payload = {
            "promptImage": first_image_url,
            "model": model,
            "promptText": prompt,
            "watermark": False,
            "duration": duration,
            "ratio": "1280:768"
        }

        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json'
        }

        endpoint = "/runwayml/v1/image_to_video"
        url = BASE_URL + endpoint

        print(f"\n🌐 端点: {endpoint}")
        print(f"   Model: {model}")
        print(f"   Duration: {duration}s")
        print(f"   Ratio: 1280:768")

        try:
            print(f"\n📤 发送请求...")
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=120
            )

            print(f"   状态码: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print(f"   📦 响应: {result}")

                # 检查任务ID
                task_id = result.get('id')

                if task_id:
                    print(f"\n✅ 任务创建成功: {task_id}")

                    # 轮询任务状态
                    video_path = poll_runway_task(task_id)
                    if video_path:
                        return video_path
                else:
                    print(f"   ⚠️  未找到任务ID，响应: {result}")

            else:
                print(f"   ❌ 请求失败: HTTP {response.status_code}")
                print(f"   响应: {response.text[:300]}")
                continue

        except requests.exceptions.RequestException as e:
            print(f"   ❌ 请求异常: {e}")
            continue
        except Exception as e:
            print(f"   ❌ 异常: {e}")
            import traceback
            traceback.print_exc()
            continue

    print(f"\n{'='*60}")
    print(f"❌ 所有模型均失败")
    print(f"{'='*60}")
    return None

def poll_runway_task(task_id: str):
    """轮询 Runway 任务状态"""

    print(f"\n⏳ 等待视频生成...")
    print(f"   任务ID: {task_id}")

    # Runway 任务查询端点（注意是 /tasks/ 复数，基于官方API文档）
    query_url = f"{BASE_URL}/runwayml/v1/tasks/{task_id}"

    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    max_retries = 180  # Runway 生成可能需要 3-5 分钟
    check_interval = 5  # 每5秒检查一次

    for i in range(max_retries):
        time.sleep(check_interval)

        try:
            response = requests.get(query_url, headers=headers, timeout=30)

            # 打印原始响应以便调试
            if i == 0:
                print(f"\n   查询URL: {query_url}")
                print(f"   首次响应状态: {response.status_code}")
                print(f"   响应内容: {response.text[:300]}")

            if response.status_code == 200:
                result = response.json()

                # VectorEngine API 格式：{"code": 0, "data": {...}}
                if result.get('code') == 0:
                    data = result.get('data', {})
                    task_status = data.get('task_status', 'unknown')

                    print(f"   [{i+1}/{max_retries}] 状态: {task_status}")

                    if task_status == 'succeed':
                        # 任务成功
                        video_url = data.get('video')

                        if video_url:
                            print(f"\n✅ 视频生成成功!")
                            print(f"   URL: {video_url}")

                            # 下载视频
                            return download_video(video_url)
                        else:
                            print(f"   ⚠️  任务完成但未找到视频URL")
                            print(f"   响应: {result}")
                            return None

                    elif task_status == 'failed':
                        error_msg = result.get('message', 'Unknown error')
                        print(f"\n❌ 生成失败: {error_msg}")
                        print(f"   完整响应: {result}")
                        return None

                    elif task_status in ['processing', 'pending', 'queued', 'submitted']:
                        # 继续等待
                        continue

                    else:
                        print(f"   ⚠️  未知状态: {task_status}")
                        continue
                else:
                    # 可能是直接返回的原始格式
                    # 尝试解析原始 Runway 格式
                    status = result.get('status', result.get('state', 'unknown'))

                    print(f"   [{i+1}/{max_retries}] 状态: {status}")

                    if status in ['completed', 'succeed', 'success']:
                        video_url = result.get('video') or result.get('url')

                        if video_url:
                            print(f"\n✅ 视频生成成功!")
                            print(f"   URL: {video_url}")
                            return download_video(video_url)
                        else:
                            print(f"   ⚠️  任务完成但未找到视频URL")
                            print(f"   响应: {result}")
                            return None

                    elif status in ['failed', 'error']:
                        print(f"\n❌ 生成失败")
                        print(f"   响应: {result}")
                        return None

                    elif status in ['processing', 'pending', 'queued', 'submitted']:
                        continue

                    else:
                        print(f"   ⚠️  未识别的响应格式")
                        print(f"   响应: {result}")
                        continue

            else:
                print(f"   ⚠️  状态查询失败: HTTP {response.status_code}")
                print(f"   响应: {response.text[:200]}")

        except Exception as e:
            print(f"   ⚠️  查询异常: {e}")

    print(f"\n❌ 等待超时 ({max_retries * check_interval}秒)")
    return None

def download_video(video_url: str):
    """下载视频"""

    print(f"\n📥 下载视频...")
    print(f"   URL: {video_url}")

    try:
        response = requests.get(video_url, timeout=300, stream=True)
        response.raise_for_status()

        OUTPUT.parent.mkdir(parents=True, exist_ok=True)

        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0

        with open(OUTPUT, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size:
                        progress = (downloaded / total_size) * 100
                        print(f"\r   下载进度: {progress:.1f}%", end='')

        print(f"\n   ✅ 视频已保存: {OUTPUT}")

        file_size = OUTPUT.stat().st_size / (1024 * 1024)
        print(f"   文件大小: {file_size:.1f}MB")

        # 检查视频时长
        import subprocess
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', str(OUTPUT)],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            duration = float(result.stdout.strip())
            print(f"   视频时长: {duration:.1f}秒")

        return OUTPUT

    except Exception as e:
        print(f"\n   ❌ 下载失败: {e}")
        return None

if __name__ == "__main__":
    result = generate_runway_video()

    if result:
        print(f"\n{'='*60}")
        print(f"🎉 成功！")
        print(f"{'='*60}")
        print(f"输出文件: {result}")
        print(f"\n使用以下命令查看:")
        print(f"open \"{result}\"")
    else:
        print(f"\n{'='*60}")
        print(f"❌ 失败")
        print(f"{'='*60}")
        sys.exit(1)

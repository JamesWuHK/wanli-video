#!/usr/bin/env python3
"""
Runway 首尾帧确定视频生成测试
场景1 → 场景2 过渡

使用 Runway 的正确 API 格式
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
OUTPUT = Path("scene_01_opening_runway_test.mp4")

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
    last_image_url = encode_image(LAST_FRAME)

    print(f"   ✅ 图片编码完成 (首帧: {len(first_image_url)//1024}KB, 尾帧: {len(last_image_url)//1024}KB)")

    # Runway提示词 - 基于实际设计图的详细描述
    prompt = """A serene ancient Chinese academy interior at dawn. An elderly scholar with white beard and traditional gray robes sits at a wooden desk, his weathered hands gently resting on the pages of an ancient yellowed book "The Analects" (论语). The book is open to a page displaying five large Chinese calligraphy characters "仁义礼智信" written in elegant brush strokes with ink black and cinnabar red accents.

Subtle movements:
- The scholar's fingers slowly trace along the calligraphy characters from right to left, following traditional reading direction
- His eyes move gently as he reads, showing deep contemplation
- Soft breathing motion in his chest and shoulders
- Warm golden morning sunlight streams through traditional wooden lattice windows (窗棂) from upper left, creating geometric patterns
- The sunbeams slowly shift across the book pages, highlighting the texture of aged paper
- Gentle dust motes float and drift in the rays of light
- Slight shadow movement as morning progresses
- Pages of the ancient book flutter very subtly from a gentle breeze

Camera movement:
- Slow, steady push-in shot starting from a medium-wide view showing the scholar and surrounding academy interior
- Gradually moving closer to focus on the book and the five characters "仁义礼智信"
- Ending in a close-up that reveals the brush stroke details and paper texture
- Smooth cinematic motion, maintaining focus on the calligraphy

Atmosphere:
- Tranquil, meditative mood with warm sepia and brown tones
- Soft diffused morning light creating peaceful ambiance
- Ink wash painting aesthetic blended with photorealistic detail
- Traditional Chinese cultural atmosphere
- High detail on the calligraphy preserving every brush stroke
- 8K cinematic quality, shallow depth of field

Duration: 15 seconds
Preserve all Chinese text exactly as shown in the image, especially "仁义礼智信" """

    print(f"\n📝 提示词:")
    print(f"   {prompt[:80]}...")

    # Runway 的正确 API 格式
    # 参考: https://api.vectorengine.ai/runwayml/v1/image_to_video

    # 测试15秒视频生成（匹配脚本要求）
    test_configs = [
        {"model": "gen4_turbo", "duration": 15},      # Gen-4 Turbo 15秒（优先）
        {"model": "gen3a_turbo", "duration": 15},     # Gen-3A Turbo 15秒（备用）
        {"model": "gen4_turbo", "duration": 10},      # Gen-4 Turbo 10秒（备用2）
    ]

    for config in test_configs:
        model = config["model"]
        duration = config["duration"]

        print(f"\n{'='*60}")
        print(f"🤖 尝试模型: {model} ({duration}秒)")
        print(f"{'='*60}")

        # 构建 Runway 格式的 payload
        payload = {
            "promptImage": first_image_url,  # 首帧图片
            "model": model,
            "promptText": prompt,
            "watermark": False,
            "duration": duration,
            "ratio": "1280:768"  # 接近 16:9
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
                task_id = result.get('id') or result.get('task_id') or result.get('taskId')

                if task_id:
                    print(f"\n✅ 任务创建成功: {task_id}")

                    # 轮询任务状态
                    video_path = poll_runway_task(task_id)
                    if video_path:
                        return video_path
                else:
                    print(f"   ⚠️  未找到任务ID，响应: {result}")

            elif response.status_code == 503:
                print(f"   ⚠️  服务不可用 (503)")
                error_data = response.json()
                print(f"   错误: {error_data.get('error', {}).get('message_zh', error_data)}")
                continue

            elif response.status_code == 500:
                print(f"   ⚠️  服务器错误 (500)")
                try:
                    error_data = response.json()
                    print(f"   错误: {error_data.get('error', error_data)}")
                except:
                    print(f"   响应: {response.text[:300]}")
                continue

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
    """轮�� Runway 任务状态"""

    print(f"\n⏳ 等待视频生成...")
    print(f"   任务ID: {task_id}")

    # Runway 任务查询端点（注意是 /tasks/ 复数）
    query_url = f"{BASE_URL}/runwayml/v1/tasks/{task_id}"

    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }

    max_retries = 180  # Runway 生成可能需要 3-5 分钟
    check_interval = 5  # 每5秒检查一次

    for i in range(max_retries):
        time.sleep(check_interval)

        try:
            response = requests.get(query_url, headers=headers, timeout=30)

            # 打印第一次查询的详细信息用于调试
            if i == 0:
                print(f"\n   查询URL: {query_url}")
                print(f"   首次响应状态: {response.status_code}")
                print(f"   响应内容: {response.text[:500]}")

            if response.status_code == 200:
                result = response.json()

                status = result.get('status', 'unknown')
                progress = result.get('progress', 0)

                print(f"   [{i+1}/{max_retries}] 状��: {status}, 进度: {progress}%")

                if status in ['completed', 'succeed', 'success', 'SUCCEEDED']:
                    # 任务成功 - 支持多种URL格式
                    video_url = result.get('url') or result.get('video_url')

                    # 检查 output 数组格式
                    if not video_url and 'output' in result:
                        output = result.get('output')
                        if isinstance(output, list) and len(output) > 0:
                            video_url = output[0]
                        elif isinstance(output, dict):
                            video_url = output.get('video')

                    if video_url:
                        print(f"\n✅ 视频生成成功!")
                        print(f"   URL: {video_url}")

                        # 下载视频
                        return download_video(video_url)
                    else:
                        print(f"   ⚠️  任务完成但未找到视频URL")
                        print(f"   响应: {result}")
                        return None

                elif status in ['failed', 'error', 'FAILED']:
                    error_msg = result.get('error', 'Unknown error')
                    print(f"\n❌ 生成失败: {error_msg}")
                    print(f"   完整响应: {result}")
                    return None

                elif status in ['processing', 'pending', 'queued', 'RUNNING']:
                    # 继续等待
                    continue

                else:
                    print(f"   ⚠️  未知状态: {status}")
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
        print(f"❌ 失败 - 服务器可能正在高峰期")
        print(f"{'='*60}")
        print(f"\n💡 建议:")
        print(f"1. 稍后再试（避开高峰期）")
        print(f"2. 或使用增强版 Ken Burns（零成本，100%保留文字）:")
        print(f"   export USE_AI=false")
        print(f"   python3 scripts/generate_dynamic_videos_vectorengine.py")
        sys.exit(1)

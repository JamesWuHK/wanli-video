#!/usr/bin/env python3
"""
Runway API 测试脚本 - 多种尝试方案

根据返回的 HTML，该 URL 是 Apifox 文档页面。
需要找到实际的 API 端点进行测试。
"""

import requests
import json


def test_endpoint_info():
    """
    分析给定的 URL 和 API Key
    """
    print("=" * 70)
    print("Runway API 端点分析")
    print("=" * 70)

    api_key = "sk-hSsIao5zgH3uctxxJqWZOezaSW2HZWFTf8HHJQgL6mav6cpJ"
    doc_url = "https://vectorengine.apifox.cn/api-349239177"

    print(f"\n提供的信息:")
    print(f"  API Key: {api_key}")
    print(f"  文档 URL: {doc_url}")

    print(f"\n分析结果:")
    print(f"  1. 该 URL 指向 Apifox 文档页面")
    print(f"  2. 'api-349239177' 可能是文档 ID，不是实际的 API 端点")
    print(f"  3. 需要在文档中找到实际的 API 请求地址")


def test_common_runway_endpoints():
    """
    尝试常见的 Runway API 端点格式
    """
    api_key = "sk-hSsIao5zgH3uctxxJqWZOezaSW2HZWFTf8HHJQgL6mav6cpJ"

    # 可能的端点列表
    possible_endpoints = [
        # 官方 Runway API
        {
            "name": "Runway 官方 Gen-3 API",
            "url": "https://api.runwayml.com/v1/gen-3/tasks",
            "method": "POST"
        },
        # 代理服务端点
        {
            "name": "向量引擎代理 - v1/images/generations",
            "url": "https://vectorengine.apifox.cn/v1/images/generations",
            "method": "POST"
        },
        {
            "name": "向量引擎代理 - v1/runway/generate",
            "url": "https://vectorengine.apifox.cn/v1/runway/generate",
            "method": "POST"
        },
        {
            "name": "向量引擎代理 - v1/video/generations",
            "url": "https://vectorengine.apifox.cn/v1/video/generations",
            "method": "POST"
        },
    ]

    print("\n" + "=" * 70)
    print("测试可能的 API 端点")
    print("=" * 70)

    for endpoint in possible_endpoints:
        print(f"\n测试: {endpoint['name']}")
        print(f"URL: {endpoint['url']}")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # 使用简单的测试数据
        test_payload = {
            "model": "runway-gen-3",
            "prompt": "A beautiful mountain landscape with moving clouds",
            "image_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4"
        }

        try:
            response = requests.post(
                endpoint['url'],
                headers=headers,
                json=test_payload,
                timeout=10
            )

            print(f"状态码: {response.status_code}")

            # 检查是否返回 HTML
            content_type = response.headers.get('Content-Type', '')
            if 'text/html' in content_type:
                print("❌ 返回 HTML 页面 (可能是错误的端点)")
            else:
                print(f"✓ 返回类型: {content_type}")
                try:
                    response_data = response.json()
                    print(f"响应数据:")
                    print(json.dumps(response_data, indent=2, ensure_ascii=False))
                except:
                    print(f"响应内容: {response.text[:500]}")

        except requests.exceptions.ConnectionError:
            print("❌ 连接错误 (端点可能不存在)")
        except requests.exceptions.Timeout:
            print("❌ 请求超时")
        except Exception as e:
            print(f"❌ 错误: {str(e)}")


def show_recommendations():
    """
    显示建议
    """
    print("\n" + "=" * 70)
    print("建议")
    print("=" * 70)
    print("""
1. 查看 Apifox 文档找到实际的 API 端点:
   - 访问: https://vectorengine.apifox.cn/api-349239177
   - 在文档中找到 "请求 URL" 或 "API 端点"

2. 常见的 Runway API 端点格式:
   - 文本生成视频: POST /v1/text-to-video
   - 图片生成视频: POST /v1/image-to-video
   - 任务查询: GET /v1/tasks/{task_id}

3. 如果使用代理服务，检查文档中的:
   - Base URL (基础地址)
   - API 路径
   - 请求参数格式

4. 联系 API 提供商获取:
   - 完整的 API 文档
   - 示例代码
   - 正确的端点地址
""")


def create_curl_examples():
    """
    生成 curl 命令示例
    """
    api_key = "sk-hSsIao5zgH3uctxxJqWZOezaSW2HZWFTf8HHJQgL6mav6cpJ"

    print("\n" + "=" * 70)
    print("可用的 curl 测试命令")
    print("=" * 70)

    examples = [
        {
            "name": "测试 Runway 官方 API",
            "curl": f"""curl -X POST https://api.runwayml.com/v1/tasks \\
  -H "Authorization: Bearer {api_key}" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "taskType": "gen3a_turbo.image_to_video",
    "internal": false,
    "options": {{
      "name": "Test Video",
      "image_prompt": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4",
      "text_prompt": "A beautiful mountain landscape with moving clouds",
      "duration": 5,
      "ratio": "16:9"
    }}
  }}'"""
        },
        {
            "name": "测试向量引擎代理",
            "curl": f"""curl -X POST https://vectorengine.apifox.cn/v1/video/generations \\
  -H "Authorization: Bearer {api_key}" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model": "runway-gen-3",
    "prompt": "A beautiful mountain landscape with moving clouds",
    "image_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4"
  }}'"""
        }
    ]

    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['name']}:")
        print(example['curl'])


if __name__ == "__main__":
    # 1. 分析端点
    test_endpoint_info()

    # 2. 尝试常见端点
    test_common_runway_endpoints()

    # 3. 显示建议
    show_recommendations()

    # 4. 生成 curl 示例
    create_curl_examples()

    print("\n" + "=" * 70)
    print("测试完成")
    print("=" * 70)

#!/usr/bin/env python3
"""
Runway API 辅助工具
帮助您找到并测试正确的 API 端点
"""

import requests
import json
import sys


class RunwayAPITester:
    def __init__(self, api_key):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })

    def test_endpoint(self, base_url, path, method="POST", payload=None):
        """
        测试一个 API 端点

        Args:
            base_url: 基础 URL，如 https://api.example.com
            path: API 路径，如 /v1/generate
            method: HTTP 方法
            payload: 请求数据
        """
        url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"

        print(f"\n{'='*70}")
        print(f"测试端点: {method} {url}")
        print(f"{'='*70}")

        if payload:
            print(f"\n请求数据:")
            print(json.dumps(payload, indent=2, ensure_ascii=False))

        try:
            if method.upper() == "POST":
                response = self.session.post(url, json=payload, timeout=30)
            elif method.upper() == "GET":
                response = self.session.get(url, timeout=30)
            else:
                print(f"不支持的方法: {method}")
                return None

            print(f"\n状态码: {response.status_code}")

            # 检查响应类型
            content_type = response.headers.get('Content-Type', '')
            print(f"Content-Type: {content_type}")

            if 'text/html' in content_type:
                print("\n⚠️  返回了 HTML 页面，这不是正确的 API 端点")
                print("这通常意味着：")
                print("  1. URL 路径不正确")
                print("  2. 这是一个文档页面而不是 API 端点")
                return None

            # 尝试解析 JSON
            try:
                data = response.json()
                print(f"\n✅ 响应数据 (JSON):")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                return data
            except json.JSONDecodeError:
                print(f"\n响应内容 (非 JSON):")
                print(response.text[:1000])
                return None

        except requests.exceptions.Timeout:
            print("\n❌ 请求超时")
            return None
        except requests.exceptions.ConnectionError as e:
            print(f"\n❌ 连接错误: {e}")
            return None
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            return None

    def interactive_test(self):
        """交互式测试"""
        print("\n" + "="*70)
        print("Runway API 交互式测试工具")
        print("="*70)

        print("\n请按照以下步骤操作：")
        print("1. 在浏览器中打开 Apifox 文档页面")
        print("2. 找到 Runway 视频生成相关的接口")
        print("3. 复制接口的完整 URL")

        print("\n提示：")
        print("  - 正确的 API URL 通常类似: https://xxx.com/v1/video/generate")
        print("  - 而不是文档 URL: https://xxx.com/api-349239177")

        while True:
            print("\n" + "-"*70)
            api_url = input("\n请输入 API 的完整 URL (或输入 'q' 退出): ").strip()

            if api_url.lower() == 'q':
                break

            if not api_url.startswith('http'):
                print("❌ URL 格式不正确，请输入完整的 URL")
                continue

            # 询问请求方法
            method = input("请求方法 (POST/GET，默认 POST): ").strip().upper() or "POST"

            # 默认的测试数据
            default_payload = {
                "prompt": "A beautiful mountain landscape with moving clouds",
                "image_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4",
                "duration": 5
            }

            use_custom = input("\n使用默认测试数据? (y/n，默认 y): ").strip().lower()

            if use_custom == 'n':
                print("\n请输入 JSON 格式的请求数据 (单行):")
                try:
                    payload_str = input()
                    payload = json.loads(payload_str)
                except json.JSONDecodeError:
                    print("❌ JSON 格式错误，使用默认数据")
                    payload = default_payload
            else:
                payload = default_payload if method == "POST" else None

            # 发送请求
            self.test_endpoint(api_url, "", method, payload)

            # 询问是否继续
            continue_test = input("\n是否测试其他端点? (y/n): ").strip().lower()
            if continue_test != 'y':
                break


def main():
    api_key = "sk-hSsIao5zgH3uctxxJqWZOezaSW2HZWFTf8HHJQgL6mav6cpJ"

    print("\n" + "="*70)
    print("欢迎使用 Runway API 测试工具")
    print("="*70)

    print(f"\nAPI Key: {api_key[:20]}...")

    tester = RunwayAPITester(api_key)

    print("\n选择测试模式:")
    print("1. 交互式测试 (推荐)")
    print("2. 快速测试常见端点")

    choice = input("\n请选择 (1/2，默认 1): ").strip() or "1"

    if choice == "1":
        tester.interactive_test()
    else:
        # 快速测试
        common_endpoints = [
            {
                "base": "https://vectorengine.apifox.cn",
                "path": "/v1/runway/image-to-video",
                "payload": {
                    "image_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4",
                    "prompt": "A beautiful mountain landscape with moving clouds"
                }
            },
            {
                "base": "https://api.runwayml.com",
                "path": "/v1/tasks",
                "payload": {
                    "taskType": "gen3a_turbo.image_to_video",
                    "options": {
                        "image_prompt": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4",
                        "text_prompt": "A beautiful mountain landscape"
                    }
                }
            }
        ]

        for endpoint in common_endpoints:
            tester.test_endpoint(
                endpoint['base'],
                endpoint['path'],
                "POST",
                endpoint['payload']
            )

    print("\n" + "="*70)
    print("测试完成")
    print("="*70)

    print("\n💡 提示:")
    print("如果所有测试都失败，建议：")
    print("1. 登录 Apifox 查看完整的 API 文档")
    print("2. 联系 API 提供商获取正确的端点信息")
    print("3. 查找文档中的 '在线调试' 或 'API 调用示例'")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已退出")
        sys.exit(0)

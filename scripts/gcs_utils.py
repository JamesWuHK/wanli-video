#!/usr/bin/env python3
"""
Google Cloud Storage 辅助工具
用于上传图片到GCS和从GCS下载生成的视频
"""

import os
from pathlib import Path
from typing import Optional
from google.cloud import storage


class GCSHelper:
    """GCS操作辅助类"""

    def __init__(self, bucket_name: str, project_id: Optional[str] = None):
        """初始化GCS客户端

        Args:
            bucket_name: GCS bucket名称 (不包含 gs:// 前缀)
            project_id: Google Cloud项目ID (可选，默认从环境变量读取)
        """
        self.bucket_name = bucket_name
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT')

        if not self.project_id:
            raise ValueError("需要设置 GOOGLE_CLOUD_PROJECT 环境变量")

        self.client = storage.Client(project=self.project_id)
        self.bucket = self.client.bucket(bucket_name)

        print(f"✅ GCS客户端初始化成功")
        print(f"   项目: {self.project_id}")
        print(f"   Bucket: {bucket_name}")

    def upload_image(self, local_path: Path, gcs_path: str) -> str:
        """上传图片到GCS

        Args:
            local_path: 本地图片路径
            gcs_path: GCS中的目标路径 (不包含bucket名称)

        Returns:
            完整的GCS URI (gs://bucket/path)
        """
        if not local_path.exists():
            raise FileNotFoundError(f"文件不存在: {local_path}")

        blob = self.bucket.blob(gcs_path)

        # 设置内容类型
        content_type = 'image/png' if local_path.suffix.lower() == '.png' else 'image/jpeg'
        blob.upload_from_filename(str(local_path), content_type=content_type)

        gcs_uri = f"gs://{self.bucket_name}/{gcs_path}"
        print(f"   ✅ 上传成功: {gcs_uri}")

        return gcs_uri

    def download_video(self, gcs_path: str, local_path: Path) -> Path:
        """从GCS下载视频

        Args:
            gcs_path: GCS中的文件路径 (可以是完整URI或相对路径)
            local_path: 本地保存路径

        Returns:
            本地文件路径
        """
        # 处理完整的GCS URI
        if gcs_path.startswith('gs://'):
            # 移除 gs://bucket-name/ 前缀
            gcs_path = gcs_path.replace(f"gs://{self.bucket_name}/", "")

        blob = self.bucket.blob(gcs_path)

        # 确保目录存在
        local_path.parent.mkdir(parents=True, exist_ok=True)

        blob.download_to_filename(str(local_path))
        print(f"   ✅ 下载成功: {local_path}")

        return local_path

    def upload_images_batch(
        self,
        local_dir: Path,
        gcs_prefix: str = "images",
        pattern: str = "*.png"
    ) -> dict:
        """批量上传图片

        Args:
            local_dir: 本地图片目录
            gcs_prefix: GCS中的前缀路径
            pattern: 文件匹配模式

        Returns:
            文件名到GCS URI的映射字典
        """
        print(f"\n📤 批量上传图片...")
        print(f"   源目录: {local_dir}")
        print(f"   GCS前缀: {gcs_prefix}")

        uploaded = {}
        images = list(local_dir.glob(pattern))

        for i, img_path in enumerate(images, 1):
            gcs_path = f"{gcs_prefix}/{img_path.name}"
            print(f"   [{i}/{len(images)}] {img_path.name}...", end=" ")

            try:
                gcs_uri = self.upload_image(img_path, gcs_path)
                uploaded[img_path.name] = gcs_uri
            except Exception as e:
                print(f"❌ 失败: {e}")

        print(f"\n✅ 完成！成功上传 {len(uploaded)}/{len(images)} 个文件")
        return uploaded

    def check_file_exists(self, gcs_path: str) -> bool:
        """检查GCS中文件是否存在

        Args:
            gcs_path: GCS路径

        Returns:
            文件是否存在
        """
        if gcs_path.startswith('gs://'):
            gcs_path = gcs_path.replace(f"gs://{self.bucket_name}/", "")

        blob = self.bucket.blob(gcs_path)
        return blob.exists()

    def list_files(self, prefix: str = "") -> list:
        """列出GCS中的文件

        Args:
            prefix: 路径前缀

        Returns:
            文件列表
        """
        blobs = self.bucket.list_blobs(prefix=prefix)
        return [blob.name for blob in blobs]


def setup_gcs_environment():
    """设置GCS环境（交互式）"""
    print("=" * 70)
    print("🔧 Google Cloud Storage 环境配置")
    print("=" * 70)

    # 检查环境变量
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    location = os.getenv('GOOGLE_CLOUD_LOCATION', 'global')

    if not project_id:
        print("\n⚠️  未检测到Google Cloud配置")
        print("\n请设置以下环境变量:")
        print("   export GOOGLE_CLOUD_PROJECT='your-project-id'")
        print("   export GOOGLE_CLOUD_LOCATION='global'")
        print("   export GOOGLE_GENAI_USE_VERTEXAI=True")
        print("\n或运行以下命令登录:")
        print("   gcloud auth application-default login")
        print("   gcloud config set project YOUR_PROJECT_ID")
        return False

    print(f"\n✅ 检测到Google Cloud配置:")
    print(f"   项目ID: {project_id}")
    print(f"   位置: {location}")

    # 检查认证
    try:
        client = storage.Client(project=project_id)
        buckets = list(client.list_buckets(max_results=1))
        print(f"   认证: ✅ 成功")
        return True
    except Exception as e:
        print(f"   认证: ❌ 失败")
        print(f"\n错误: {e}")
        print("\n请运行以下命令进行认证:")
        print("   gcloud auth application-default login")
        return False


def main():
    """主函数 - 示例用法"""
    import argparse

    parser = argparse.ArgumentParser(description='GCS辅助工具')
    parser.add_argument('action', choices=['setup', 'upload', 'download', 'list'])
    parser.add_argument('--bucket', help='GCS bucket名称')
    parser.add_argument('--local-path', help='本地路径')
    parser.add_argument('--gcs-path', help='GCS路径')
    parser.add_argument('--prefix', default='', help='GCS前缀')

    args = parser.parse_args()

    if args.action == 'setup':
        setup_gcs_environment()
        return

    if not args.bucket:
        print("❌ 需要指定 --bucket 参数")
        return

    helper = GCSHelper(args.bucket)

    if args.action == 'upload':
        if not args.local_path or not args.gcs_path:
            print("❌ 需要指定 --local-path 和 --gcs-path")
            return
        helper.upload_image(Path(args.local_path), args.gcs_path)

    elif args.action == 'download':
        if not args.gcs_path or not args.local_path:
            print("❌ 需要指定 --gcs-path 和 --local-path")
            return
        helper.download_video(args.gcs_path, Path(args.local_path))

    elif args.action == 'list':
        files = helper.list_files(args.prefix)
        print(f"\n📁 文件列表 (前缀: {args.prefix or '/'}):")
        for f in files:
            print(f"   - {f}")


if __name__ == "__main__":
    main()

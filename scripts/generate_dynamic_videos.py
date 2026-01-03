#!/usr/bin/env python3
"""
混合方案动态视频生成器
- 关键分镜：使用 VEO3 AI 生成真实动态视频
- 普通分镜：使用增强版 Ken Burns 效果（缩放、平移、动态模糊）
"""

import os
import yaml
import subprocess
import asyncio
import time
from pathlib import Path
from typing import List, Dict, Optional
from google import genai
from google.genai.types import GenerateVideosConfig, Image
import edge_tts
from gcs_utils import GCSHelper


class DynamicVideoGenerator:
    """混合方案动态视频生成器"""

    def __init__(
        self,
        script_path: str,
        image_dir: str,
        keyframe_dir: str,
        output_dir: str,
        gcs_bucket: str = None,
        use_veo: bool = True
    ):
        """初始化

        Args:
            script_path: 脚本文件路径
            image_dir: 起始帧图片目录
            keyframe_dir: 关键帧图片目录
            output_dir: 输出目录
            gcs_bucket: Google Cloud Storage bucket (用于VEO3, 格式: gs://bucket-name/prefix)
            use_veo: 是否启用VEO3 (默认True，关键分镜使用AI)
        """
        self.script_path = script_path
        self.image_dir = Path(image_dir)
        self.keyframe_dir = Path(keyframe_dir)
        self.output_dir = Path(output_dir)
        self.gcs_bucket = gcs_bucket
        self.use_veo = use_veo and gcs_bucket is not None

        # 创建子目录
        self.video_dir = self.output_dir / "videos"
        self.audio_dir = self.output_dir / "audio"
        self.temp_dir = self.output_dir / "temp"
        self.veo_cache_dir = self.output_dir / "veo_cache"

        for d in [self.video_dir, self.audio_dir, self.temp_dir, self.veo_cache_dir]:
            d.mkdir(parents=True, exist_ok=True)

        # 加载脚本
        with open(script_path, 'r', encoding='utf-8') as f:
            self.script_data = yaml.safe_load(f)

        self.scenes = self.script_data.get('scenes', [])
        self.voice = self.script_data.get('project', {}).get('voice', 'zh-CN-YunxiNeural')

        # 初始化VEO客户端和GCS helper
        if self.use_veo:
            try:
                self.veo_client = genai.Client()

                # 解析bucket名称
                bucket_name = gcs_bucket.replace('gs://', '').split('/')[0]
                self.gcs_prefix = '/'.join(gcs_bucket.replace('gs://', '').split('/')[1:])
                self.gcs_helper = GCSHelper(bucket_name)

                print(f"✅ VEO3 客户端初始化成功")
                print(f"   GCS Bucket: {bucket_name}")
                print(f"   GCS Prefix: {self.gcs_prefix}")
            except Exception as e:
                print(f"⚠️  VEO3 初始化失败: {e}")
                print(f"   将回退到纯本地处理")
                self.use_veo = False

        print(f"✅ 加载了 {len(self.scenes)} 个场景")
        print(f"🎙️  使用语音: {self.voice}")
        print(f"🎬 VEO3 状态: {'启用' if self.use_veo else '禁用'}")

    def is_key_scene(self, scene: Dict) -> bool:
        """判断是否为关键分镜（需要使用AI生成）

        判断标准：
        1. 场景标记为 'key': true
        2. 时长 >= 4秒
        3. 场景描述包含动作词汇
        """
        # 显式标记
        if scene.get('key', False):
            return True

        # 时长判断
        if scene.get('duration', 0) >= 4:
            return True

        # 动作词汇判断
        action_keywords = ['飞行', '移动', '奔跑', '跳跃', '旋转', '飘动', '流动', '生长']
        description = scene.get('description', '') + scene.get('narration', '')

        for keyword in action_keywords:
            if keyword in description:
                return True

        return False

    async def generate_narration_audio(self, scene_id: str, narration: str) -> Path:
        """生成画外音音频"""
        audio_path = self.audio_dir / f"{scene_id}.mp3"

        if audio_path.exists():
            return audio_path

        communicate = edge_tts.Communicate(narration, self.voice)
        await communicate.save(str(audio_path))

        return audio_path

    def get_audio_duration(self, audio_path: Path) -> float:
        """获取音频时长"""
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            str(audio_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())

    async def generate_veo_video(
        self,
        image_path: Path,
        prompt: str,
        duration: float,
        scene_id: str
    ) -> Optional[Path]:
        """使用VEO3生成动态视频

        Args:
            image_path: 输入图片路径
            prompt: 视频生成提示词
            duration: 视频时长（秒）
            scene_id: 场景ID

        Returns:
            生成的视频路径，失败返回None
        """
        if not self.use_veo:
            return None

        output_video = self.veo_cache_dir / f"{scene_id}_veo.mp4"

        # 检查缓存
        if output_video.exists():
            print(f"   ⏭️  VEO视频已存在，使用缓存")
            return output_video

        try:
            print(f"   🤖 调用VEO3生成视频...")
            print(f"      提示词: {prompt[:60]}...")

            # 上传图片到GCS
            gcs_image_path = f"{self.gcs_prefix}/images/{scene_id}.png"
            print(f"   📤 上传图片到GCS...")
            gcs_image_uri = self.gcs_helper.upload_image(image_path, gcs_image_path)

            # 调用VEO3 API
            operation = self.veo_client.models.generate_videos(
                model="veo-3.1-generate-001",
                prompt=prompt,
                image=Image(
                    gcs_uri=gcs_image_uri,
                    mime_type="image/png",
                ),
                config=GenerateVideosConfig(
                    aspect_ratio="16:9",
                    output_gcs_uri=f"gs://{self.gcs_helper.bucket_name}/{self.gcs_prefix}/videos/",
                ),
            )

            # 等待生成完成
            print(f"   ⏳ 等待VEO3生成（可能需要几分钟）...")
            retry_count = 0
            max_retries = 120  # 最多等待30分钟

            while not operation.done and retry_count < max_retries:
                time.sleep(15)
                operation = self.veo_client.operations.get(operation)
                retry_count += 1

                if retry_count % 4 == 0:  # 每分钟打印一次
                    print(f"      等待中... ({retry_count * 15}秒)")

            if operation.response:
                video_gcs_uri = operation.result.generated_videos[0].video.uri
                print(f"   ✅ VEO3生成完成: {video_gcs_uri}")

                # 下载视频
                print(f"   📥 下载视频到本地...")
                self.gcs_helper.download_video(video_gcs_uri, output_video)

                return output_video
            else:
                print(f"   ❌ VEO3生成超时")
                return None

        except Exception as e:
            print(f"   ⚠️  VEO3生成失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def create_ken_burns_video(
        self,
        image_path: Path,
        duration: float,
        output_path: Path,
        effect: str = "zoom_in"
    ):
        """创建Ken Burns效果视频（缩放+平移）

        Args:
            image_path: 输入图片
            duration: 视频时长
            output_path: 输出路径
            effect: 效果类型 (zoom_in, zoom_out, pan_left, pan_right, diagonal)
        """

        # 定义不同的Ken Burns效果
        effects = {
            "zoom_in": {
                "scale": "scale='if(eq(iw/ih,16/9),iw,ih*16/9)':'if(eq(iw/ih,16/9),ih,iw*9/16)',zoompan=z='min(zoom+0.001,1.3)':d={frames}:s=2048x1152:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
                "description": "缓慢放大"
            },
            "zoom_out": {
                "scale": "scale='if(eq(iw/ih,16/9),iw,ih*16/9)':'if(eq(iw/ih,16/9),ih,iw*9/16)',zoompan=z='if(lte(zoom,1.0),1.3,max(1.0,zoom-0.001))':d={frames}:s=2048x1152:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
                "description": "缓慢缩小"
            },
            "pan_right": {
                "scale": "scale='if(eq(iw/ih,16/9),iw,ih*16/9)':'if(eq(iw/ih,16/9),ih,iw*9/16)',zoompan=z='1.2':d={frames}:s=2048x1152:x='min(iw/zoom/2,iw-iw/zoom-iw/zoom*t/{duration})':y='ih/2-(ih/zoom/2)'",
                "description": "向右平移"
            },
            "pan_left": {
                "scale": "scale='if(eq(iw/ih,16/9),iw,ih*16/9)':'if(eq(iw/ih,16/9),ih,iw*9/16)',zoompan=z='1.2':d={frames}:s=2048x1152:x='iw-iw/zoom-min(iw/zoom/2,iw-iw/zoom-iw/zoom*t/{duration})':y='ih/2-(ih/zoom/2)'",
                "description": "向左平移"
            },
            "diagonal": {
                "scale": "scale='if(eq(iw/ih,16/9),iw,ih*16/9)':'if(eq(iw/ih,16/9),ih,iw*9/16)',zoompan=z='min(zoom+0.0008,1.2)':d={frames}:s=2048x1152:x='iw/2-(iw/zoom/2)-iw/zoom*0.3*t/{duration}':y='ih/2-(ih/zoom/2)-ih/zoom*0.2*t/{duration}'",
                "description": "对角线移动"
            }
        }

        frames = int(duration * 30)
        effect_config = effects.get(effect, effects["zoom_in"])
        filter_str = effect_config["scale"].format(frames=frames, duration=duration)

        cmd = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', str(image_path),
            '-vf', filter_str,
            '-t', str(duration),
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-r', '30',
            str(output_path)
        ]

        subprocess.run(cmd, check=True, capture_output=True)

    def add_subtitle_to_video(
        self,
        video_path: Path,
        subtitle_text: str,
        output_path: Path
    ):
        """为视频添加字幕"""

        fontfile = '/System/Library/Fonts/PingFang.ttc'
        fontsize = 32
        fontcolor = 'white'
        box = 1
        boxcolor = 'black@0.5'

        subtitle_escaped = subtitle_text.replace("'", "'\\''").replace(":", "\\:")

        filter_str = (
            f"drawtext=text='{subtitle_escaped}':"
            f"fontfile='{fontfile}':"
            f"fontsize={fontsize}:"
            f"fontcolor={fontcolor}:"
            f"box={box}:"
            f"boxcolor={boxcolor}:"
            f"x=(w-text_w)/2:"
            f"y=h-100"
        )

        cmd = [
            'ffmpeg', '-y',
            '-i', str(video_path),
            '-vf', filter_str,
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-c:a', 'copy',
            str(output_path)
        ]

        subprocess.run(cmd, check=True, capture_output=True)

    def merge_video_audio(
        self,
        video_path: Path,
        audio_path: Path,
        output_path: Path
    ):
        """合并视频和音频"""
        cmd = [
            'ffmpeg', '-y',
            '-i', str(video_path),
            '-i', str(audio_path),
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-shortest',
            str(output_path)
        ]
        subprocess.run(cmd, check=True, capture_output=True)

    async def create_scene_video(self, scene_index: int):
        """为单个场景创建动态视频"""
        scene = self.scenes[scene_index]
        scene_id = scene['id']
        duration = scene['duration']
        narration = scene.get('narration', '')
        description = scene.get('description', '')

        print(f"\n🎬 场景 {scene_index + 1}/{len(self.scenes)}: {scene_id}")
        print(f"   ⏱️  时长: {duration}秒")
        print(f"   📝 描述: {description[:50]}...")

        # 判断是否为关键分镜
        is_key = self.is_key_scene(scene)
        print(f"   {'🔑 关键分镜 (使用VEO3)' if is_key else '📹 普通分镜 (使用Ken Burns)'}")

        # 1. 生成画外音
        audio_path = await self.generate_narration_audio(scene_id, narration)
        audio_duration = self.get_audio_duration(audio_path)
        actual_duration = max(duration, audio_duration + 0.5)

        # 获取图片
        keyframe = self.keyframe_dir / f"{scene_id}_keyframe.png"
        if not keyframe.exists():
            raise FileNotFoundError(f"关键帧不存在: {keyframe}")

        # 2. 生成视频（VEO3 或 Ken Burns）
        video_no_subtitle = self.temp_dir / f"{scene_id}_no_subtitle.mp4"

        if is_key and self.use_veo:
            # 使用VEO3生成
            veo_prompt = f"{description}。画面需要有自然的动态效果。"
            veo_video = await self.generate_veo_video(
                keyframe,
                veo_prompt,
                actual_duration,
                scene_id
            )

            if veo_video and veo_video.exists():
                # 成功使用VEO
                video_no_subtitle = veo_video
            else:
                # VEO失败，回退到Ken Burns
                print(f"   ⚠️  回退到Ken Burns效果")
                self.create_ken_burns_video(
                    keyframe,
                    actual_duration,
                    video_no_subtitle,
                    effect="zoom_in"
                )
        else:
            # 使用Ken Burns效果
            # 根据场景选择不同效果
            effects = ["zoom_in", "zoom_out", "pan_right", "pan_left", "diagonal"]
            effect = effects[scene_index % len(effects)]

            print(f"   🎨 应用Ken Burns效果: {effect}")
            self.create_ken_burns_video(
                keyframe,
                actual_duration,
                video_no_subtitle,
                effect=effect
            )

        # 3. 添加字幕
        video_with_subtitle = self.temp_dir / f"{scene_id}_subtitle.mp4"

        print(f"   📝 添加字幕...")
        self.add_subtitle_to_video(
            video_no_subtitle,
            narration,
            video_with_subtitle
        )

        # 4. 合并音频
        output_video = self.video_dir / f"{scene_id}.mp4"

        print(f"   🎵 合并音频...")
        self.merge_video_audio(
            video_with_subtitle,
            audio_path,
            output_video
        )

        # 清理临时文件
        if video_no_subtitle != output_video:
            video_no_subtitle.unlink(missing_ok=True)
        video_with_subtitle.unlink(missing_ok=True)

        print(f"   ✅ 完成: {output_video.name}")
        return output_video

    async def generate_all_videos(self):
        """生成所有场景视频"""
        print("=" * 70)
        print("🎬 混合方案动态视频生成")
        print("=" * 70)

        success_count = 0
        failed_scenes = []
        key_scenes_count = sum(1 for s in self.scenes if self.is_key_scene(s))

        print(f"\n📊 统计:")
        print(f"   总场景数: {len(self.scenes)}")
        print(f"   关键分镜: {key_scenes_count} (使用VEO3)")
        print(f"   普通分镜: {len(self.scenes) - key_scenes_count} (使用Ken Burns)")
        print()

        for i in range(len(self.scenes)):
            try:
                await self.create_scene_video(i)
                success_count += 1
            except Exception as e:
                scene_id = self.scenes[i]['id']
                print(f"   ❌ 失败: {str(e)}")
                failed_scenes.append((scene_id, str(e)))

        print("\n" + "=" * 70)
        print(f"✅ 完成！成功生成 {success_count}/{len(self.scenes)} 个视频")

        if failed_scenes:
            print(f"\n⚠️  失败场景：")
            for sid, error in failed_scenes:
                print(f"   - {sid}: {error[:60]}")

        print(f"\n📁 输出目录: {self.video_dir}")
        print("=" * 70)


async def main():
    """主函数"""

    # 配置
    GCS_BUCKET = os.getenv('GCS_BUCKET')  # 从环境变量读取
    USE_VEO = os.getenv('USE_VEO', 'true').lower() == 'true'

    if not GCS_BUCKET:
        print("⚠️  未设置 GCS_BUCKET 环境变量")
        print("   将禁用VEO3功能，仅使用Ken Burns效果")
        print("   如需启用VEO3，请设置:")
        print("   export GCS_BUCKET='gs://your-bucket/prefix'")
        print()

    generator = DynamicVideoGenerator(
        script_path='./文脉薪传_细化脚本.yaml',
        image_dir='./storyboards/文脉薪传/doubao_images',
        keyframe_dir='./storyboards/文脉薪传/keyframes',
        output_dir='./storyboards/文脉薪传/dynamic_videos',
        gcs_bucket=GCS_BUCKET,
        use_veo=USE_VEO
    )

    await generator.generate_all_videos()


if __name__ == "__main__":
    asyncio.run(main())

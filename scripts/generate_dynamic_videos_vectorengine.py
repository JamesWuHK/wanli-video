#!/usr/bin/env python3
"""
使用 VectorEngine (sora-2) 的混合方案动态视频生成器
- 关键分镜：使用 sora-2 AI 生成（¥0.030/次，最便宜）
- 普通分镜：使用增强版 Ken Burns 效果
"""

import os
import yaml
import subprocess
import asyncio
from pathlib import Path
from typing import List, Dict, Optional
import edge_tts
from vectorengine_client import VectorEngineClient


class DynamicVideoGeneratorVE:
    """使用 VectorEngine 的混合方案动态视频生成器"""

    def __init__(
        self,
        script_path: str,
        image_dir: str,
        keyframe_dir: str,
        output_dir: str,
        api_key: str = None,
        model: str = "sora-2",
        use_ai: bool = True
    ):
        """初始化

        Args:
            script_path: 脚本文件路径
            image_dir: 起始帧图片目录
            keyframe_dir: 关键帧图片目录
            output_dir: 输出目录
            api_key: VectorEngine API密钥
            model: AI模型名称 (sora-2, veo_3_1-fast, grok-video-3)
            use_ai: 是否启用AI生成
        """
        self.script_path = script_path
        self.image_dir = Path(image_dir)
        self.keyframe_dir = Path(keyframe_dir)
        self.output_dir = Path(output_dir)
        self.model = model
        self.use_ai = use_ai

        # 创建子目录
        self.video_dir = self.output_dir / "videos"
        self.audio_dir = self.output_dir / "audio"
        self.temp_dir = self.output_dir / "temp"
        self.ai_cache_dir = self.output_dir / "ai_cache"

        for d in [self.video_dir, self.audio_dir, self.temp_dir, self.ai_cache_dir]:
            d.mkdir(parents=True, exist_ok=True)

        # 加载脚本
        with open(script_path, 'r', encoding='utf-8') as f:
            self.script_data = yaml.safe_load(f)

        self.scenes = self.script_data.get('scenes', [])
        self.voice = self.script_data.get('project', {}).get('voice', 'zh-CN-YunxiNeural')

        # 初始化 VectorEngine 客户端
        if self.use_ai:
            try:
                self.ve_client = VectorEngineClient(api_key=api_key)
                print(f"✅ VectorEngine 客户端初始化成功")
                print(f"   模型: {self.model}")
            except Exception as e:
                print(f"⚠️  VectorEngine 初始化失败: {e}")
                print(f"   将回退到纯本地处理")
                self.use_ai = False

        print(f"✅ 加载了 {len(self.scenes)} 个场景")
        print(f"🎙️  使用语音: {self.voice}")
        print(f"🎬 AI 状态: {'启用 (' + self.model + ')' if self.use_ai else '禁用'}")

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

    def generate_ai_video(
        self,
        image_path: Path,
        prompt: str,
        duration: float,
        scene_id: str
    ) -> Optional[Path]:
        """使用 VectorEngine 生成动态视频

        Args:
            image_path: 输入图片路径
            prompt: 视频生成提示词
            duration: 视频时长（秒）
            scene_id: 场景ID

        Returns:
            生成的视频路径，失败返回None
        """
        if not self.use_ai:
            return None

        output_video = self.ai_cache_dir / f"{scene_id}_{self.model}.mp4"

        # 检查缓存
        if output_video.exists():
            print(f"   ⏭️  AI视频已存在，使用缓存")
            return output_video

        # 调用 VectorEngine API
        result = self.ve_client.generate_video_from_image(
            image_path=image_path,
            prompt=prompt,
            model=self.model,
            duration=int(duration),
            output_path=output_video
        )

        return result

    def create_ken_burns_video(
        self,
        image_path: Path,
        duration: float,
        output_path: Path,
        effect: str = "zoom_in"
    ):
        """创建增强版Ken Burns效果视频（缩放+平移+缓动曲线）"""

        # ��义不同的增强版Ken Burns效果
        # 使用标准数学函数实现缓动曲线，让动画更自然，模拟电影感镜头运动
        effects = {
            "zoom_in": {
                # 缓慢推进 - 使用二次缓动曲线 (easeInOut)
                # t = on/duration 从 0 到 1，使用 t^2 让开始和结束都变慢
                "scale": "scale='if(eq(iw/ih,16/9),iw,ih*16/9)':'if(eq(iw/ih,16/9),ih,iw*9/16)',zoompan=z='1.0+0.4*pow(on/{duration},2)':d={frames}:s=2048x1152:fps=30:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
            },
            "zoom_out": {
                # 缓慢拉远 - 使用反向二次曲线
                "scale": "scale='if(eq(iw/ih,16/9),iw,ih*16/9)':'if(eq(iw/ih,16/9),ih,iw*9/16)',zoompan=z='1.4-0.4*pow(on/{duration},2)':d={frames}:s=2048x1152:fps=30:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
            },
            "pan_right": {
                # 右移 + 轻微缩放 - 使用正弦波增加动感
                "scale": "scale='if(eq(iw/ih,16/9),iw,ih*16/9)':'if(eq(iw/ih,16/9),ih,iw*9/16)',zoompan=z='1.1+0.05*sin(on/{duration}*PI)':d={frames}:s=2048x1152:fps=30:x='(iw/2-(iw/zoom/2))+200*pow(on/{duration},1.5)':y='ih/2-(ih/zoom/2)'",
            },
            "pan_left": {
                # 左移 + 轻微缩放
                "scale": "scale='if(eq(iw/ih,16/9),iw,ih*16/9)':'if(eq(iw/ih,16/9),ih,iw*9/16)',zoompan=z='1.1+0.05*sin(on/{duration}*PI)':d={frames}:s=2048x1152:fps=30:x='(iw/2-(iw/zoom/2))-200*pow(on/{duration},1.5)':y='ih/2-(ih/zoom/2)'",
            },
            "pan_up": {
                # 上移 + 缩放 - 营造升腾感
                "scale": "scale='if(eq(iw/ih,16/9),iw,ih*16/9)':'if(eq(iw/ih,16/9),ih,iw*9/16)',zoompan=z='1.0+0.3*pow(on/{duration},1.2)':d={frames}:s=2048x1152:fps=30:x='iw/2-(iw/zoom/2)':y='(ih/2-(ih/zoom/2))-150*pow(on/{duration},1.5)'",
            },
            "diagonal_in": {
                # 对角线推进（右下到左上）- 经典电影镜头
                "scale": "scale='if(eq(iw/ih,16/9),iw,ih*16/9)':'if(eq(iw/ih,16/9),ih,iw*9/16)',zoompan=z='1.0+0.35*pow(on/{duration},2)':d={frames}:s=2048x1152:fps=30:x='(iw/2-(iw/zoom/2))-120*pow(on/{duration},1.5)':y='(ih/2-(ih/zoom/2))-80*pow(on/{duration},1.5)'",
            },
            "circular": {
                # 圆周运动 + 缩放 - 增加动态感
                "scale": "scale='if(eq(iw/ih,16/9),iw,ih*16/9)':'if(eq(iw/ih,16/9),ih,iw*9/16)',zoompan=z='1.15+0.05*sin(on/{duration}*2*PI)':d={frames}:s=2048x1152:fps=30:x='(iw/2-(iw/zoom/2))+100*sin(on/{duration}*2*PI)':y='(ih/2-(ih/zoom/2))+60*cos(on/{duration}*2*PI)'",
            },
            "breathe": {
                # 呼吸感缩放（慢-快-慢）- 用正弦波实现自然节奏
                "scale": "scale='if(eq(iw/ih,16/9),iw,ih*16/9)':'if(eq(iw/ih,16/9),ih,iw*9/16)',zoompan=z='1.0+0.15*sin(on/{duration}*PI)':d={frames}:s=2048x1152:fps=30:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
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
            '-preset', 'slow',  # 更好的压缩质量
            '-crf', '18',  # 高质量（0-51，越小越好）
            '-pix_fmt', 'yuv420p',
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

        # 根据系统选择字体文件
        import platform
        if platform.system() == 'Darwin':  # macOS
            fontfile = '/System/Library/Fonts/PingFang.ttc'
        else:  # Linux (Docker)
            fontfile = '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc'

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
            '-c:a', 'copy' if video_path.suffix == '.mp4' else 'aac',
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
        image_prompt = scene.get('image_generation_prompt', '')

        print(f"\n🎬 场景 {scene_index + 1}/{len(self.scenes)}: {scene_id}")
        print(f"   ⏱️  时长: {duration}秒")
        print(f"   📝 提示词: {image_prompt[:80]}...")

        # 判断是否为关键分镜
        is_key = self.is_key_scene(scene)
        method = f'AI ({self.model})' if is_key and self.use_ai else 'Ken Burns'
        print(f"   {'🔑 关键分镜' if is_key else '📹 普通分镜'} - 使用 {method}")

        # 1. 生成画外音
        audio_path = await self.generate_narration_audio(scene_id, narration)
        audio_duration = self.get_audio_duration(audio_path)
        actual_duration = max(duration, audio_duration + 0.5)

        # 获取图片（优先使用 doubao_images 中的设计图，包含正确的中文字体）
        image_path = self.image_dir / f"{scene_id}.png"
        if not image_path.exists():
            # 回退到 keyframes
            image_path = self.keyframe_dir / f"{scene_id}_keyframe.png"
            if not image_path.exists():
                raise FileNotFoundError(f"图片不存在: {image_path}")

        # 2. 生成视频（AI 或 Ken Burns）
        video_no_subtitle = self.temp_dir / f"{scene_id}_no_subtitle.mp4"

        if is_key and self.use_ai:
            # 使用 AI 生成
            ai_prompt = image_prompt if image_prompt else narration
            ai_video = self.generate_ai_video(
                image_path,
                ai_prompt,
                actual_duration,
                scene_id
            )

            if ai_video and ai_video.exists():
                # 成功使用 AI
                video_no_subtitle = ai_video
            else:
                # AI 失败，回退到 Ken Burns
                print(f"   ⚠️  AI生成失败，回退到 Ken Burns 效果")
                self.create_ken_burns_video(
                    image_path,
                    actual_duration,
                    video_no_subtitle,
                    effect="zoom_in"
                )
        else:
            # 使用增强版 Ken Burns 效果
            # 根据场景内容智能选择效果
            effects = [
                "zoom_in",      # 推进
                "zoom_out",     # 拉远
                "pan_right",    # 右移
                "pan_left",     # 左移
                "pan_up",       # 上移
                "diagonal_in",  # 对角线
                "circular",     # 圆周
                "breathe"       # 呼吸
            ]

            # 根据场景序号和描述选择合适的效果
            if 'opening' in scene_id or 'grand' in scene_id:
                effect = "zoom_in"  # 开场和结尾用推进
            elif 'intro' in scene_id or 'history' in scene_id:
                effect = "zoom_out"  # 介绍性场景用拉远
            elif 'modern' in scene_id:
                effect = "pan_right"  # 现代场景用平移
            else:
                effect = effects[scene_index % len(effects)]

            print(f"   🎨 应用增强版 Ken Burns 效果: {effect}")
            self.create_ken_burns_video(
                image_path,
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
        if video_no_subtitle != output_video and video_no_subtitle.parent == self.temp_dir:
            video_no_subtitle.unlink(missing_ok=True)
        video_with_subtitle.unlink(missing_ok=True)

        print(f"   ✅ 完成: {output_video.name}")
        return output_video

    async def generate_all_videos(self, max_concurrent: int = 3):
        """生成所有场景视频（支持并发）

        Args:
            max_concurrent: 最大并发数（默认3个，避免API限流）
        """
        print("=" * 70)
        print("🎬 VectorEngine 混合方案动态视频生成 (并发模式)")
        print("=" * 70)

        key_scenes_count = sum(1 for s in self.scenes if self.is_key_scene(s))

        print(f"\n📊 统计:")
        print(f"   总场景数: {len(self.scenes)}")
        print(f"   关键分镜: {key_scenes_count} (使用 {self.model})")
        print(f"   普通分镜: {len(self.scenes) - key_scenes_count} (使用 Ken Burns)")
        print(f"   🚀 并发数: {max_concurrent} 个场景同时生成")
        if self.use_ai:
            estimated_cost = key_scenes_count * 0.078  # veo_3_1-fast 价格
            print(f"   预估成本: ¥{estimated_cost:.2f}")
        print()

        # 使用信号量控制并发数
        semaphore = asyncio.Semaphore(max_concurrent)

        async def create_with_semaphore(index):
            async with semaphore:
                try:
                    return await self.create_scene_video(index), None
                except Exception as e:
                    scene_id = self.scenes[index]['id']
                    print(f"   ❌ {scene_id} 失败: {str(e)}")
                    return None, (scene_id, str(e))

        # 并发执行所有场景
        results = await asyncio.gather(*[create_with_semaphore(i) for i in range(len(self.scenes))])

        # 统计结果
        success_count = sum(1 for r, e in results if r is not None)
        failed_scenes = [e for r, e in results if e is not None]

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
    API_KEY = os.getenv('VECTORENGINE_API_KEY')  # 从环境变量读取
    MODEL = os.getenv('AI_MODEL', 'sora-2')  # 默认使用 sora-2
    USE_AI = os.getenv('USE_AI', 'true').lower() == 'true'

    if not API_KEY and USE_AI:
        print("⚠️  未设置 VECTORENGINE_API_KEY 环境变量")
        print("   将禁用AI功能，仅使用Ken Burns效果")
        print("   如需启用AI，请设置:")
        print("   export VECTORENGINE_API_KEY='your-api-key'")
        print()
        USE_AI = False

    generator = DynamicVideoGeneratorVE(
        script_path='./文脉薪传_细化脚本.yaml',
        image_dir='./storyboards/文脉薪传/doubao_images',
        keyframe_dir='./storyboards/文脉薪传/keyframes',
        output_dir='./storyboards/文脉薪传/dynamic_videos_ve',
        api_key=API_KEY,
        model=MODEL,
        use_ai=USE_AI
    )

    await generator.generate_all_videos()


if __name__ == "__main__":
    asyncio.run(main())

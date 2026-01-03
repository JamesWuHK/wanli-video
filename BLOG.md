# AI驱动的视频制作完整实践：从创意到成品的143秒之旅

> 使用Runway Gen-3、Azure TTS、FFmpeg等工具，完成"文脉薪传：儒家五常的传承"文化宣传片制作全过程记录

## 前言

在AI技术飞速发展的今天，视频制作的门槛正在被极大地降低。作为一名技术爱好者，我最近完成了一个完整的AI视频制作项目——制作了一部143秒的文化传播短片"文脉薪传：儒家五常的传承"。整个过程经历了7次迭代优化，最终实现了画外音、字幕、BGM的完美融合。

这篇文章将详细分享我的制作经验、遇到的问题以及解决方案，希望能帮助更多想要尝试AI视频制作的朋友。

## 项目概览

**最终成果**:
- 视频时长: 143秒 (2分23秒)
- 场景数量: 13个完整场景
- 技术栈: Runway Gen-3 + Azure TTS + FFmpeg
- 文件大小: 18.7 MB (1080p)
- 迭代次数: 7个版本
- 开发时长: 约15-20小时

**核心特点**:
- ✅ 画外音与视频精确同步（帧级对齐）
- ✅ BGM与情感基调完美融合（20%音量）
- ✅ 字幕样式清晰美观（实心描边）
- ✅ 完全自动化制作流程（一键生成）

## 一、项目规划：好的开始是成功的一半

### 1.1 主题确定

我选择了"儒家五常"（仁、义、礼、智、信）作为主题，原因有三：

1. **文化价值**: 传统文化值得用现代技术传播
2. **结构清晰**: 五常分明，便于分镜设计
3. **情感丰富**: 每个概念都有古今对照，适合视觉呈现

### 1.2 分镜脚本设计

我将整个视频分为13个场景：

```
场景01: 开场 - 孔子创立儒学
场景02-03: 仁 - 爱人之心（古代+现代）
场景04-05: 义 - 正道而行（古代+现代）
场景06-07: 礼 - 秩序之美（古代+现代）
场景08-09: 智 - 求知不息（古代+现代）
场景10-11: 信 - 立身之本（古代+现代）
场景12: 传承 - 薪火相传
场景13: 结尾 - 文脉薪传，生生不息
```

**关键设计原则**:
- 每个场景10-15秒，符合观众注意力节奏
- 古今对照，增强叙事层次
- 情感递进，从理性到感性

### 1.3 技术选型

| 工具 | 用途 | 选择理由 |
|------|------|----------|
| Runway Gen-3 | AI视频生成 | 画面质量高，运动自然 |
| Azure TTS | 文字转语音 | 中文发音自然，可控性强 |
| FFmpeg | 视频处理 | 强大的开源工具，灵活性高 |
| Python | 自动化脚本 | 便于流程自动化 |

## 二、素材生成：AI的力量与人工的智慧

### 2.1 AI视频生成（Runway Gen-3）

**Prompt工程技巧**:

每个场景我都精心设计了提示词，以scene_01为例：

```
A serene ancient Chinese academy at dawn,
warm sunlight streaming through traditional wooden lattice windows.
An elderly scholar in traditional robes opening ancient book 'The Analects'.
Camera slowly zooms into calligraphy characters '仁义礼智信'.
Cinematic lighting, ink wash painting aesthetic,
warm sepia tones, highly detailed, 8K quality.
```

**关键要素**:
- 主体描述: 学者、书籍、书法
- 环境设定: 书院、晨光、窗棂
- 镜头运动: 缓慢推进
- 视觉风格: 水墨画美学、暖色调
- 质量要求: 电影级光线、8K质量

**生成经验**:
- 每个场景生成2-3个候选，选择最佳
- 保持视觉风格一致性（同一色调、同一画风）
- 不满意立即重新生成，不要凑合

### 2.2 画外音生成（Azure TTS）

**配置参数**:
```python
voice_config = {
    "voice": "zh-CN-YunxiNeural",  # 选择男声，符合文化主题
    "rate": "0%",                   # 正常语速
    "pitch": "0%",                  # 正常音调
    "output_format": "audio-48khz-192kbitrate-mono-mp3"
}
```

**技巧总结**:
- 选择符合主题气质的声音（严肃/亲切/专业）
- 为每个场景单独生成音频文件（便于后期对齐）
- 添加适当停顿：句号后0.5秒，段落后1秒

### 2.3 字幕制作

我使用SRT格式，手动创建了13个字幕文件。每个场景对应一个SRT：

```srt
1
00:00:00,000 --> 00:00:10,960
两千五百年前，孔子创立儒学。仁义礼智信，五常之道，
如薪火相传，照亮中华文明的前行之路。
```

**字幕样式优化**（这是后期调试重点）：
```python
subtitle_style = (
    "FontName=PingFang SC,"      # 苹方字体
    "FontSize=26,"               # 字号
    "Bold=1,"                    # 粗体
    "PrimaryColour=&H00FFFFFF,"  # 白色
    "OutlineColour=&H00000000,"  # 黑色描边
    "BorderStyle=1,"             # 实心描边
    "Outline=3,"                 # 描边宽度3px
    "Shadow=2,"                  # 阴影
    "MarginV=15"                 # 底部边距15px
)
```

## 三、技术难点：从90秒到143秒的完美对齐

### 3.1 问题1: 视频时长不足

**初始问题**: V1版本只有92秒，远低于目标的120秒。

**原因分析**: 参考音频只有89秒，FFmpeg的`-shortest`参数导致视频被裁剪。

**解决方案**:
```python
# 使用aloop循环音频
f"[1:a]aloop=loop=2:size=2e+09[a_out]"
```

**结果**: V2达到142秒 ✅

### 3.2 问题2: 字幕时间轴不对齐

**问题描述**: 字幕显示时间与实际场景不匹配，"义"的字幕溢出到下一个场景。

**根本原因**: 字幕时间戳基于原始视频时长，没有考虑全局减速（0.92x）。

**核心代码**:
```python
# 计算减速后的时长
original_duration = video['duration']
slowed_duration = original_duration / global_speed  # 关键！

# 使用减速后的时间戳
all_subtitles.append({
    'start': current_time,
    'end': current_time + slowed_duration,
    'text': subtitle_text
})
```

**结果**: V3实现精确对齐 ✅

### 3.3 问题3: 短片段处理奇怪

**问题描述**: 2秒短片通过循环播放延长到10秒，出现明显重复，效果很奇怪。

**初始方案**（失败）:
```python
# 循环播放5次
-stream_loop 5 -i short_video.mp4
```

**优化方案**（成功）:
```python
# 使用减速而非循环
speed_factor = current_duration / target_duration  # 2/10 = 0.2x

cmd = [
    'ffmpeg', '-y', '-i', input_video,
    '-filter:v', f'setpts={1/speed_factor}*PTS',  # 视频减速5倍
    '-filter:a', f'atempo={speed_factor}',        # 音频减速
    output_video
]
```

**效果**: 0.2x慢动作，缓慢优雅，无重复感 ✅

### 3.4 问题4: 画外音不同步

**问题描述**: V4中字幕准确了，但画外音与画面不匹配。

**根本原因**: 使用了整体参考音频，而非场景独立音频。

**解决方案**: 为每个场景独立处理音频

```python
def merge_scene_narrations(video_list, audio_dir, output_audio, global_speed):
    for video in video_list:
        scene_id = video['scene_id']
        audio_file = audio_dir / f"{scene_id}.mp3"

        # 计算减速后的时长
        slowed_duration = video['duration'] / global_speed

        # 调整音频速度并填充到精确时长
        slowdown_cmd = [
            'ffmpeg', '-y', '-i', audio_file,
            '-filter:a', f'atempo={global_speed},apad,atrim=0:{slowed_duration}',
            '-c:a', 'libmp3lame', '-b:a', '192k',
            slowed_audio
        ]
```

**核心技术点**:
- `atempo`: 调整速度（0.92x）
- `apad`: 填充静音
- `atrim`: 裁剪到精确时长

**结果**: V5完美同步 ✅

### 3.5 问题5: BGM消失了

**问题**: V5修复音频同步时，不小心删掉了BGM。

**解决**: 添加BGM混音

```python
# BGM循环并减速
f"[2:a]aloop=loop=5:size=2e+09,atempo={global_speed}[bgm_loop];"

# 混音：画外音100% + BGM 20%
"[1:a][bgm_loop]amix=inputs=2:duration=first:weights=1.0 0.2[a_out]"
```

**权重选择**:
- 画外音: 1.0 (100%) - 主角
- BGM: 0.2 (20%) - 配角，营造氛围

### 3.6 问题6-7: 字幕位置微调

用户反馈字幕位置太高，经过两次调整：

- V6: `MarginV=30` (适中)
- V7: `MarginV=15` (贴近底部，最终版) ✅

## 四、核心代码：500行Python的智慧

### 4.1 架构设计

```python
# 主流程（main函数）
1. create_video_list()        # 准备视频列表，处理短片段
2. merge_subtitles()           # 合并字幕，调整时间轴
3. merge_scene_narrations()    # 合并画外音，精确对齐
4. merge_videos_with_audio_and_subtitles()  # 最终合成
```

### 4.2 精确时间轴管理

这是整个项目最核心的技术点：

```python
def merge_subtitles(storyboard_dir, video_list, output_srt, global_speed=0.92):
    current_time = 0.0  # 累积时间（减速后）

    for video in video_list:
        # 每个场景独立计算
        original_duration = video['duration']
        slowed_duration = original_duration / global_speed

        # 添加字幕条目
        all_subtitles.append({
            'start': current_time,
            'end': current_time + slowed_duration,
            'text': subtitle_text
        })

        # 累加时间
        current_time += slowed_duration
```

**关键点**:
- 使用数学计算，不靠估算
- 每个场景独立处理
- 累积时间精确到毫秒

### 4.3 FFmpeg滤镜链

最终合成使用了复杂的FFmpeg滤镜链：

```python
'-filter_complex', (
    # 1. 视频减速
    f"[0:v]setpts={1/global_speed}*PTS[v_slow];"

    # 2. 烧录字幕
    f"[v_slow]subtitles={subtitle_file}:force_style='...'[v_out];"

    # 3. BGM循环并减速
    f"[2:a]aloop=loop=5:size=2e+09,atempo={global_speed}[bgm_loop];"

    # 4. 音频混音
    "[1:a][bgm_loop]amix=inputs=2:duration=first:weights=1.0 0.2[a_out]"
)
```

## 五、迭代历程：从V1到V7的进化

| 版本 | 时长 | 主要问题 | 解决方案 |
|------|------|----------|----------|
| V1 | 92秒 | 时长过短 | 添加音频循环 |
| V2 | 142秒 | 字幕时间轴不对齐 | 计算减速后时长 |
| V3 | 142秒 | 短片段循环奇怪 | 改用减速 |
| V4 | 143秒 | 画外音不同步 | 场景独立音频 |
| V5 | 143秒 | BGM消失 | 添加混音 |
| V6 | 143秒 | 字幕位置偏高 | MarginV=30 |
| **V7** | **143秒** | **完美** ✅ | **MarginV=15** |

**版本迭代启示**:
- 预期需要5-7个版本才能达到满意效果
- 每次迭代解决1-2个核心问题
- 保持耐心，细节决定成败

## 六、成本与收益分析

### 6.1 时间成本

```
创意策划与脚本撰写      3小时
AI图像生成（13场景）    2小时
AI视频生成（13片段）    4小时
画外音生成             30分钟
字幕制作               1小时
视频合成与调试         3小时
多轮迭代优化           3小时
──────────────────────────
总计                   16.5小时
```

### 6.2 经济成本

- **Runway Gen-3**: 约$30 (13个视频片段)
- **Azure TTS**: 约$5 (13个音频文件)
- **FFmpeg**: 免费 ✅
- **Python**: 免费 ✅
- **总计**: ~$35

### 6.3 学习收益

**技术能力**:
- ✅ 掌握AI视频生成的Prompt工程
- ✅ 精通FFmpeg视频处理技术
- ✅ 理解音视频同步原理
- ✅ 学会Python自动化脚本开发

**可复用资产**:
- ✅ 500+行生产级Python脚本
- ✅ 5000+字技术文档
- ✅ 13个场景的分镜设计
- ✅ 完整的工作流程模板

## 七、经验总结与最佳实践

### 7.1 规划优先

> "前期充分规划胜过后期反复返工"

- 完整的分镜脚本是成功的基础
- 明确每个场景的视觉、音频、文字元素
- 预留足够的迭代时间

### 7.2 素材质量把控

> "AI生成素材需要人工筛选"

- 不满意的素材立即重新生成
- 保持视觉风格的一致性至关重要
- 每个场景生成2-3个候选，择优选用

### 7.3 精确的时间轴管理

> "使用数学计算而非估算"

- 每个场景独立处理音频
- 公式: `slowed_duration = original_duration / global_speed`
- 字幕、画外音、视频三者严格对齐

### 7.4 迭代优化思维

> "预期需要5-7个版本"

- 每次迭代解决1-2个核心问题
- 保留版本历史，便于回溯
- 用户反馈驱动优化方向

### 7.5 自动化工具链

> "Python脚本实现完整工作流自动化"

- 模块化设计：素材准备、音频同步、视频合成独立
- 便于调试和重复执行
- 一键生成最终成品

## 八、技术细节速查表

### 8.1 FFmpeg常用命令

```bash
# 1. 视频减速
ffmpeg -i input.mp4 -filter:v "setpts=1.087*PTS" output.mp4

# 2. 音频填充与裁剪
ffmpeg -i input.mp3 -af "apad,atrim=0:10.5" output.mp3

# 3. 音频混音
ffmpeg -i narration.aac -i bgm.mp3 \
  -filter_complex "[0:a][1:a]amix=inputs=2:duration=first:weights=1.0 0.2" \
  output.aac

# 4. 字幕烧录
ffmpeg -i video.mp4 \
  -vf "subtitles=subtitle.srt:force_style='FontName=PingFang SC,FontSize=26'" \
  output.mp4

# 5. 视频拼接
ffmpeg -f concat -safe 0 -i list.txt -c copy output.mp4
```

### 8.2 Python核心代码片段

```python
# 获取视频时长
def get_video_duration(video_path):
    cmd = ['ffprobe', '-v', 'error',
           '-show_entries', 'format=duration',
           '-of', 'json', video_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    return float(data['format']['duration'])

# SRT时间格式转换
def format_srt_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
```

### 8.3 字幕样式参数

| 参数 | 值 | 说明 |
|------|-----|------|
| FontName | PingFang SC | 苹方字体 |
| FontSize | 26 | 字号 |
| Bold | 1 | 粗体 |
| PrimaryColour | &H00FFFFFF | 白色 |
| OutlineColour | &H00000000 | 黑色描边 |
| BorderStyle | 1 | 实心描边 |
| Outline | 3 | 描边宽度3px |
| Shadow | 2 | 阴影深度 |
| MarginV | 15 | 底部边距15px |

## 九、常见问题与解决方案

### Q1: 视频时长不符合预期

**原因**: `-shortest`参数导致以最短轨道为准

**解决**: 确保音频轨道（画外音+BGM）时长 ≥ 视频时长

### Q2: 画外音与画面不同步

**原因**: 原始音频时长 ≠ 视频时长

**解决**: 为每个场景单独调整音频速度并填充/裁剪

```python
'-filter:a', f'atempo={global_speed},apad,atrim=0:{slowed_duration}'
```

### Q3: 字幕显示位置不理想

**解决方案**:
- 60px: 偏高
- 30px: 适中
- 15px: 贴近底部（推荐）

### Q4: BGM过响或过轻

**解决**: 调整amix权重

```python
# 画外音:BGM 权重比例
"amix=inputs=2:duration=first:weights=1.0 0.2"  # 标准
# 调整范围：0.1-0.3 之间
```

### Q5: 短视频片段处理

**问题**: 2秒片段需延长到10秒

**方案对比**:
- ❌ 循环播放：显得重复
- ✅ 减速播放：0.2x，缓慢优雅

## 十、未来优化方向

### 10.1 技术层面

1. **支持更多AI平台**: Pika, Kling, Sora等
2. **转场效果**: 添加淡入淡出、擦除等过渡效果
3. **批量处理**: 支持多个项目并行生成
4. **实时预览**: 在合成前预览效果

### 10.2 工作流优化

1. **模板化**: 建立不同主题的脚本模板
2. **素材库**: 复用背景音乐、转场效果
3. **云端协作**: 支持团队协作编辑
4. **版本管理**: Git集成，便于回溯

### 10.3 应用场景扩展

- **教育培训**: 在线课程、知识科普
- **企业宣传**: 品牌故事、产品演示
- **文化传播**: 历史故事、艺术解读
- **社交媒体**: 抖音、B站短视频

## 十一、开源分享

我已将完整的代码和文档开源到GitHub：

**仓库地址**: https://github.com/JamesWuHK/wanli-video

**包含内容**:
- ✅ 主合成脚本（merge_runway_videos.py）
- ✅ 完整技能文档（video-production.md）
- ✅ 分镜设计配置
- ✅ 辅助工具脚本
- ✅ 详细使用说明

欢迎Star、Fork和提Issue！

## 结语

这次AI视频制作之旅，让我深刻体会到：

1. **AI降低门槛，但不能替代创意**
   - AI帮我们生成素材，但创意策划仍需人工
   - 好的提示词工程需要对视觉美学的理解

2. **细节决定成败**
   - 7个版本的迭代，只为字幕位置下移15px
   - 音频同步精确到毫秒，才有专业效果

3. **工具链的重要性**
   - FFmpeg的强大功能值得深入学习
   - Python自动化大大提升效率

4. **分享让知识增值**
   - 记录过程帮助他人，也巩固自己
   - 开源代码推动技术进步

如果你也对AI视频制作感兴趣，希望这篇文章能给你一些启发。欢迎交流讨论！

---

**作者**: James Wu
**GitHub**: [@JamesWuHK](https://github.com/JamesWuHK)
**项目地址**: [wanli-video](https://github.com/JamesWuHK/wanli-video)
**发布日期**: 2026-01-03

**关键词**: #AI视频制作 #Runway #FFmpeg #Azure-TTS #Python自动化 #视频后期

---

> 如果这篇文章对你有帮助，请给GitHub项目一个Star ⭐️
> 有任何问题欢迎在评论区或GitHub Issue中交流！

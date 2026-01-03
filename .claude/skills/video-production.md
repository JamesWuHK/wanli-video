# AI视频制作完整流程 (video-production)

## 技能描述
完整的AI驱动视频制作工作流，从创意策划到最终成品的全流程自动化解决方案。适用于文化传播、教育、营销等多种场景的短视频制作。

## 适用场景
- 文化传播类短视频（2-3分钟）
- 教育科普视频
- 品牌宣传片
- 产品介绍视频
- 社交媒体内容

## 完整工作流程

### 阶段一：创意策划与脚本设计

#### 1. 确定主题与目标
```yaml
项目定位:
  - 主题: 明确视频要传达的核心信息
  - 受众: 目标观众群体
  - 时长: 建议2-3分钟（适合社交媒体传播）
  - 风格: 文化/科技/温情/专业等
```

**成功经验**：
- 文化类视频需要深厚的主题积淀（如"仁义礼智信"五常文化）
- 明确叙事结构：开场引入 → 主体展开 → 情感升华 → 总结呼应

#### 2. 撰写详细脚本
创建结构化的分镜脚本（JSON格式）：

```json
{
  "project": {
    "name": "项目名称",
    "resolution": [1920, 1080],
    "fps": 30,
    "target_duration": 120
  },
  "scenes": [
    {
      "scene_id": "scene_01_opening",
      "duration": 12,
      "narration": "画外音文本",
      "visual_prompt": "详细的视觉描述，用于AI图像生成",
      "storyboard_notes": {
        "shot_type": "镜头类型（推镜/拉镜/特写等）",
        "visual_elements": ["视觉元素列表"],
        "color_palette": {"主色调配置"},
        "emotional_tone": "情感基调"
      }
    }
  ]
}
```

**成功经验**：
- 每个场景10-15秒为佳（符合观众注意力节奏）
- 视觉提示词要具体：包含场景、人物、动作、光影、风格
- 预留转场时间（0.5-1秒淡入淡出）

### 阶段二：素材生成

#### 3. AI图像生成
使用MidJourney/Stable Diffusion/DALL-E等工具：

**Prompt工程要点**：
```
基础结构: [主体] + [环境] + [光影] + [风格] + [质量修饰]

示例:
"An elderly Chinese scholar in traditional robes opening ancient book
'The Analects' in serene academy at dawn, warm sunlight through wooden
lattice windows, ink wash painting aesthetic, cinematic lighting,
8K quality, highly detailed"
```

**成功经验**：
- 为每个场景生成2-3个候选图像，选择最佳
- 保持视觉风格一致性（同一color palette、同一艺术风格）
- 生成尺寸建议：1792x1024 (适合横屏视频)

#### 4. AI视频生成
使用Runway Gen-3/Pika/Kling等视频生成工具：

**关键参数**：
```yaml
分辨率: 1280x720 或 1920x1080
时长: 5-10秒/段
运动幅度: 适中（避免过度运动导致失真）
关键帧: 使用生成的静态图作为首帧
```

**成功经验**：
- Runway Gen-3：适合文化、人文类内容，运动自然
- 每段视频生成后立即检查：
  - 画面稳定性
  - 人物/物体变形情况
  - 运动方向是否符合预期
- 不满意立即重新生成，不要凑合

#### 5. 画外音生成
使用Azure TTS/ElevenLabs等文字转语音服务：

```python
# Azure TTS示例
voice_config = {
    "voice": "zh-CN-YunxiNeural",  # 选择合适的声音
    "rate": "0%",                   # 语速（-50%到+200%）
    "pitch": "0%",                  # 音调
    "output_format": "audio-48khz-192kbitrate-mono-mp3"
}
```

**成功经验**：
- 选择符合主题气质的声音（严肃/亲切/专业）
- 为每个场景单独生成音频文件（便于后期对齐）
- 添加适当停顿：句号后0.5秒，段落后1秒

#### 6. 字幕生成
创建SRT格式字幕文件：

```srt
1
00:00:00,000 --> 00:00:10,960
两千五百年前，孔子创立儒学。仁义礼智信，五常之道，
如薪火相传，照亮中华文明的前行之路。

2
00:00:10,960 --> 00:00:21,920
仁，是爱人之心。子曰：'仁者爱人'。
己欲立而立人，己欲达而达人。
```

**字幕样式参数**：
```
字体: PingFang SC (苹方) / Source Han Sans (思源黑体)
字号: 24-28
加粗: 是
描边: 3px黑色
阴影: 2px
底部边距: 15-30px（根据画面内容调整）
```

### 阶段三：视频合成与后期

#### 7. 视频素材预处理

**处理短片段**：
```python
# 使用FFmpeg减速延长（不循环，更自然）
def extend_short_video(input_path, output_path, target_duration=10.0):
    current_duration = get_video_duration(input_path)
    speed_factor = current_duration / target_duration

    cmd = [
        'ffmpeg', '-y',
        '-i', input_path,
        '-filter:v', f'setpts={1/speed_factor}*PTS',
        '-filter:a', f'atempo={speed_factor}',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
        output_path
    ]
```

**成功经验**：
- 2秒短片延长到10秒：使用0.2x减速（缓慢优雅）
- 避免循环播放（会产生明显重复，显得不自然）

#### 8. 音频同步对齐

**画外音处理**：
```python
# 为每个场景调整音频速度，匹配视频时长
def sync_narration_to_video(audio_file, video_duration, global_speed=0.92):
    slowed_duration = video_duration / global_speed

    cmd = [
        'ffmpeg', '-y',
        '-i', audio_file,
        '-filter:a', f'atempo={global_speed},apad,atrim=0:{slowed_duration}',
        '-c:a', 'libmp3lame', '-b:a', '192k',
        output_audio
    ]
```

**成功经验**：
- 每个场景独立处理音频，确保严格对齐
- 使用apad填充静音，atrim精确裁剪
- 全局速度调整（0.92x）：让节奏更舒缓，适合文化类内容

#### 9. BGM混音

**音频混合策略**：
```python
# BGM音量20%，画外音音量100%
filter_complex = (
    "[narration][bgm]amix=inputs=2:duration=first:weights=1.0 0.2[audio_out]"
)
```

**BGM选择要点**：
- 风格匹配：中国风视频用古典/民乐BGM
- 节奏舒缓：避免抢戏
- 循环无缝：使用aloop确保BGM覆盖全片

#### 10. 字幕烧录

**FFmpeg字幕滤镜**：
```python
subtitle_style = (
    "force_style='"
    "FontName=PingFang SC,"
    "FontSize=26,"
    "Bold=1,"
    "PrimaryColour=&H00FFFFFF,"      # 白色
    "OutlineColour=&H00000000,"      # 黑色描边
    "BorderStyle=1,"
    "Outline=3,"
    "Shadow=2,"
    "MarginV=15"                     # 底部边距
    "'"
)
```

**成功经验**：
- 实心描边（BorderStyle=1）比透明更清晰
- 描边宽度3px：在各种背景上都清晰可读
- 底部边距15-30px：不遮挡画面重要内容

#### 11. 最终合成

**完整合成流程**：
```python
def merge_final_video(
    video_segments,      # 视频片段列表
    narration_track,     # 合成的画外音
    bgm_track,          # 背景音乐
    subtitle_file,      # 字幕文件
    output_file,
    global_speed=0.92   # 全局速度调整
):
    cmd = [
        'ffmpeg', '-y',
        # 输入
        '-f', 'concat', '-safe', '0', '-i', video_list,
        '-i', narration_track,
        '-i', bgm_track,

        # 滤镜链
        '-filter_complex', (
            # 1. 视频减速
            f"[0:v]setpts={1/global_speed}*PTS[v_slow];"
            # 2. 烧录字幕
            f"[v_slow]subtitles={subtitle_file}:{subtitle_style}[v_out];"
            # 3. BGM循环并减速
            f"[2:a]aloop=loop=5:size=2e+09,atempo={global_speed}[bgm_loop];"
            # 4. 音频混音
            "[1:a][bgm_loop]amix=inputs=2:duration=first:weights=1.0 0.2[a_out]"
        ),

        # 输出映射
        '-map', '[v_out]',
        '-map', '[a_out]',

        # 编码参数
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
        '-c:a', 'aac', '-b:a', '192k',
        '-shortest',
        output_file
    ]
```

### 阶段四：质量控制与优化

#### 12. 多轮迭代检查清单

**视觉检查**：
- [ ] 画面稳定，无抖动
- [ ] 转场自然流畅
- [ ] 色彩风格统一
- [ ] 字幕清晰可读，位置合适
- [ ] 无明显AI生成瑕疵

**音频检查**：
- [ ] 画外音与画面严格同步
- [ ] BGM音量适中，不抢戏
- [ ] 无爆音、破音
- [ ] 整体音量均衡

**节奏检查**：
- [ ] 总时长符合目标（±10秒）
- [ ] 每个场景时长合理（10-15秒）
- [ ] 叙事节奏流畅，无拖沓
- [ ] 高潮部分情感饱满

**版本管理**：
```
V1: 初始合成（发现问题：音频不同步）
V2: 修复音频循环（发现问题：时长过短）
V3: 调整时间轴对齐（发现问题：字幕溢出）
V4: 优化短片段处理（发现问题：画外音不匹配）
V5: 重构音频同步方案（发现问题：字幕位置太高）
V6: 调整字幕位置（发现问题：仍需下移）
V7: 最终版本 ✓
```

## 技术工具链

### 必备工具
- **FFmpeg**: 视频/音频处理核心工具
- **Python 3.8+**: 自动化脚本
- **Azure TTS / ElevenLabs**: 文字转语音
- **Runway Gen-3 / Pika**: AI视频生成
- **MidJourney / DALL-E**: AI图像生成

### Python依赖库
```python
# requirements.txt
pathlib          # 路径处理
subprocess       # FFmpeg调用
json            # 配置文件解析
typing          # 类型提示
```

### FFmpeg关键技术

#### 视频速度调整
```bash
# 减速到0.92x
ffmpeg -i input.mp4 -filter:v "setpts=1.087*PTS" -filter:a "atempo=0.92" output.mp4
```

#### 音频填充与裁剪
```bash
# 填充静音并裁剪到精确时长
ffmpeg -i input.mp3 -af "apad,atrim=0:10.5" output.mp3
```

#### 音频混音
```bash
# 两轨混音，控制音量比例
ffmpeg -i narration.aac -i bgm.mp3 \
  -filter_complex "[0:a][1:a]amix=inputs=2:duration=first:weights=1.0 0.2" \
  output.aac
```

#### 字幕烧录
```bash
ffmpeg -i video.mp4 -vf "subtitles=subtitle.srt:force_style='FontName=PingFang SC,FontSize=26,Bold=1,MarginV=15'" output.mp4
```

## 核心成功经验总结

### 1. 规划优先
- **前期充分规划胜过后期反复返工**
- 完整的分镜脚本是成功的基础
- 明确每个场景的视觉、音频、文字元素

### 2. 素材质量把控
- **AI生成素材需要人工筛选**
- 不满意的素材立即重新生成
- 保持视觉风格的一致性至关重要

### 3. 精确的时间轴管理
- **每个场景独立处理音频**
- 使用数学计算而非估算（duration / global_speed）
- 字幕、画外音、视频三者严格对齐

### 4. 迭代优化思维
- **预期需要5-7个版本才能达到满意效果**
- 每次迭代解决1-2个核心问题
- 保留版本历史，便于回溯

### 5. 用户反馈驱动
- **"时间不够不要勉强，效果第一"**
- 细节调整（如字幕位置）需多次微调
- 最终效果以观众体验为准

### 6. 自动化工具链
- **Python脚本实现完整工作流自动化**
- 模块化设计：素材准备、音频同步、视频合成独立
- 便于调试和重复执行

## 输出规格建议

### 技术参数
```yaml
视频:
  分辨率: 1920x1080 (1080p)
  帧率: 24-30 fps
  编码: H.264 (libx264)
  码率: CRF 23 (高质量)

音频:
  编码: AAC
  码率: 192 kbps
  采样率: 44.1kHz / 48kHz

文件:
  格式: MP4
  预期大小: 15-20 MB/分钟
  目标时长: 120-180秒
```

## 常见问题与解决方案

### Q1: 视频时长不符合预期
**原因**: `-shortest`参数导致以最短轨道为准
**解决**: 确保音频轨道（画外音+BGM）时长≥视频时长

### Q2: 画外音与画面不同步
**原因**: 原始音频时长≠视频时长
**解决**: 为每个场景单独调整音频速度并填充/裁剪

### Q3: 字幕显示位置不理想
**原因**: MarginV值设置不当
**解决**:
- 60px: 偏高（适合画面下方有重要内容）
- 30px: 适中
- 15px: 贴近底部（推荐）

### Q4: BGM过响或过轻
**原因**: amix权重比例不当
**解决**:
- 画外音:BGM = 1.0:0.2（标准）
- 调整范围：0.1-0.3之间

### Q5: 短视频片段处理
**原因**: 2秒片段需延长到10秒
**解决**:
- ✗ 循环播放（显得重复）
- ✓ 减速播放（0.2x，缓慢优雅）

## 项目文件结构示例

```
project/
├── storyboards/
│   └── 文脉薪传/
│       ├── complete_storyboard_design.json   # 分镜脚本
│       ├── final_videos/
│       │   ├── audio/                        # 场景音频
│       │   │   ├── scene_01_opening.mp3
│       │   │   └── ...
│       │   └── temp/                         # 字幕文件
│       │       ├── scene_01_opening.srt
│       │       └── ...
│       ├── bgm/
│       │   └── china-chinese-music.mp3       # 背景音乐
│       ├── merged_subtitles.srt              # 合并字幕
│       ├── merged_narration.aac              # 合并画外音
│       └── 文脉薪传_最终版_V7.mp4             # 最终成品
├── videos/
│   ├── scene_01_opening_runway.mp4           # AI生成视频
│   ├── scene_02_ren_intro_runway.mp4
│   └── ...
├── merge_runway_videos.py                    # 主合成脚本
└── README.md
```

## 时间成本估算

```
阶段                    时间投入
────────────────────────────────
创意策划与脚本撰写      2-4小时
AI图像生成（13场景）    2-3小时
AI视频生成（13片段）    3-5小时
画外音生成             30分钟
字幕制作               1小时
视频合成与调试         2-4小时
多轮迭代优化           2-3小时
────────────────────────────────
总计                   12-20小时
```

## 成本优化建议

### 降低成本
- 使用开源工具（Stable Diffusion替代MidJourney）
- 批量生成素材，减少API调用次数
- 复用视觉风格和提示词模板

### 提升效率
- 建立素材库（背景音乐、转场效果）
- 脚本模板化（不同主题复用结构）
- 自动化工具链（一键生成）

## 扩展应用场景

### 教育培训
- 在线课程开场视频
- 知识点讲解动画
- 学习总结短片

### 企业宣传
- 品牌故事视频
- 产品功能演示
- 员工培训材料

### 文化传播
- 传统文化科普
- 历史故事讲述
- 艺术作品解读

### 社交媒体
- 抖音/快手短视频
- 公众号推文配图
- B站UP主内容

## 版本历史与演进

本技能基于真实项目"文脉薪传：儒家五常的传承"视频制作经验总结。

**项目亮点**：
- ✓ 13个场景完整叙事
- ✓ 画外音与视频精确同步
- ✓ BGM与情感基调完美融合
- ✓ 字幕样式清晰美观
- ✓ 总时长143秒（2分23秒），符合目标
- ✓ 7个版本迭代，持续优化

**最终成果**：
- 文件大小：18.7 MB
- 视频质量：1080p, 24fps
- 技术实现：完全自动化流程

---

**作者**: Claude (Anthropic)
**日期**: 2026-01-03
**版本**: 1.0
**项目参考**: 文脉薪传视频制作项目

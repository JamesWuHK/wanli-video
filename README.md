# 🎬 Wanli Video - AI驱动的视频制作完整流程

[![GitHub](https://img.shields.io/badge/GitHub-wanli--video-blue)](https://github.com/JamesWuHK/wanli-video)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> 从创意策划到最终成品的全流程自动化视频制作解决方案

## ✨ 项目亮点

本项目展示了完整的AI驱动视频制作流程，使用 **Runway Gen-3**、**Azure TTS**、**FFmpeg** 等工具，完成了"文脉薪传：儒家五常的传承"文化宣传片制作。

### 核心成果

- ✅ **13个场景完整叙事** - 从开场到结尾的流畅叙事
- ✅ **画外音与视频精确同步** - 每个场景独立音频处理，帧级精准对齐
- ✅ **BGM与情感基调完美融合** - 20%音量背景音乐，不抢戏
- ✅ **字幕样式清晰美观** - 实心描边，在各种背景上清晰可读
- ✅ **完全自动化制作流程** - 从脚本配置到成品输出一键生成
- ✅ **最终时长** - 143秒 (2分23秒) 高质量视频

## 🎯 为什么选择这个项目？

### 1. 完整的制作流程文档

我们将整个视频制作过程总结成可复用的技能文档：

📖 **[视频制作完整流程](.claude/skills/video-production.md)** - 从零到一的详细指南

包含：
- 四个阶段的完整工作流
- FFmpeg核心技术详解
- 常见问题与解决方案
- 成本与时间估算

### 2. 生产级的Python脚本

🔧 **[merge_runway_videos.py](merge_runway_videos.py)** - 主合成脚本

核心功能：
- 视频片段智能拼接
- 音频精确同步（atempo + apad + atrim）
- 字幕时间轴对齐
- BGM混音（权重控制）
- 全局速度调整

### 3. 真实项目案例

📺 **"文脉薪传：儒家五常的传承"**

- 主题：中华传统文化传播
- 规模：13个场景，143秒
- 迭代：7个版本优化
- 技术：Runway Gen-3 AI视频生成

## 🚀 快速开始

### 环境要求

```bash
# Python 3.8+
python --version

# FFmpeg (必须)
ffmpeg -version

# 可选：Azure TTS / ElevenLabs API密钥
```

### 运行示例

```bash
# 克隆仓库
git clone https://github.com/JamesWuHK/wanli-video.git
cd wanli-video

# 运行主合成脚本（需要准备好视频素材）
python3 merge_runway_videos.py
```

### 查看完整文档

```bash
# 查看视频制作技能文档
cat .claude/skills/video-production.md

# 查看项目说明
cat storyboards/文脉薪传/使用指南.md
```

## 📂 项目结构

```
wanli-video/
├── 🎯 核心文件
│   ├── merge_runway_videos.py          # 主合成脚本（最重要）
│   ├── .claude/skills/
│   │   └── video-production.md         # 视频制作完整流程文档
│   └── .gitignore                      # Git配置（排除大文件）
│
├── 📜 脚本配置
│   ├── 文脉薪传_细化脚本.yaml           # 场景脚本配置
│   └── storyboards/文脉薪传/
│       └── complete_storyboard_design.json  # 完整分镜设计
│
├── 🛠️ 辅助脚本
│   └── scripts/
│       ├── generate_scene_videos.py              # 场景视频生成
│       ├── generate_scene_videos_with_narration.py  # 带画外音生成
│       ├── merge_videos.py                       # 视频合并工具
│       └── runway_batch_generate.py              # Runway批量生成
│
├── 📖 文档
│   ├── README.md                       # 项目说明（本文件）
│   ├── CLEANUP_RECOMMENDATION.md       # 清理建议
│   └── docs/                           # 其他文档
│
└── 🎨 素材（.gitignore已排除）
    ├── videos/                         # Runway生成的视频片段
    ├── storyboards/文脉薪传/
    │   ├── final_videos/audio/         # 场景画外音
    │   ├── final_videos/temp/          # 字幕文件
    │   ├── bgm/                        # 背景音乐
    │   └── 文脉薪传_Runway_最终版_V7.mp4  # 最终成品
    └── （这些大文件不会提交到Git）
```

## 🔑 核心技术亮点

### 1. 精确的时间轴管理

每个场景独立处理音频，确保画外音、字幕、视频三者严格对齐：

```python
# 计算减速后的时长
original_duration = video['duration']
slowed_duration = original_duration / global_speed

# 调整音频速度并填充到精确时长
slowdown_cmd = [
    'ffmpeg', '-y', '-i', audio_file,
    '-filter:a', f'atempo={global_speed},apad,atrim=0:{slowed_duration}',
    '-c:a', 'libmp3lame', '-b:a', '192k',
    output_audio
]
```

### 2. 短片段智能处理

2秒短片延长到10秒，使用减速而非循环，避免重复感：

```python
speed_factor = current_duration / target_duration  # 2/10 = 0.2x
cmd = [
    'ffmpeg', '-y', '-i', input_video,
    '-filter:v', f'setpts={1/speed_factor}*PTS',  # 视频减速
    '-filter:a', f'atempo={speed_factor}',        # 音频减速
    output_video
]
```

### 3. 音频混音控制

画外音与BGM完美融合，互不干扰：

```python
filter_complex = (
    # BGM循环并减速
    f"[2:a]aloop=loop=5:size=2e+09,atempo={global_speed}[bgm_loop];"
    # 混音：画外音100% + BGM 20%
    "[1:a][bgm_loop]amix=inputs=2:duration=first:weights=1.0 0.2[a_out]"
)
```

### 4. 字幕样式优化

实心描边 + 加粗阴影，在各种背景上清晰可读：

```python
subtitle_style = (
    "FontName=PingFang SC,"
    "FontSize=26,"
    "Bold=1,"
    "PrimaryColour=&H00FFFFFF,"      # 白色
    "OutlineColour=&H00000000,"      # 黑色描边
    "BorderStyle=1,"                 # 实心描边
    "Outline=3,"                     # 加粗描边
    "Shadow=2,"                      # 阴影
    "MarginV=15"                     # 底部边距
)
```

## 📊 项目数据

### 开发历程

- **迭代次数**: 7个版本（V1→V7）
- **开发时长**: 约15-20小时
- **代码行数**: 500+ 行（主脚本）
- **文档字数**: 5000+ 字（技能文档）

### 技术指标

- **最终视频时长**: 143.3秒
- **文件大小**: 18.7 MB
- **分辨率**: 1920x1080 (1080p)
- **帧率**: 24 fps
- **音频比特率**: 192 kbps AAC

### 成本估算

- **AI视频生成**: Runway Gen-3 (~$30)
- **文字转语音**: Azure TTS (~$5)
- **开发时间**: 15-20小时
- **总成本**: ~$35 + 人力成本

## 🛠️ 技术栈

### 核心工具

- **视频生成**: Runway Gen-3
- **图像生成**: MidJourney / DALL-E / Doubao
- **文字转语音**: Azure TTS / ElevenLabs
- **视频处理**: FFmpeg 4.0+
- **脚本语言**: Python 3.8+

### Python依赖

```python
# 核心库
pathlib          # 路径处理
subprocess       # FFmpeg调用
json            # 配置文件解析
typing          # 类型提示
```

## 📖 学习资源

### 推荐阅读顺序

1. **入门**: [README.md](README.md) - 项目概览（本文件）
2. **深入**: [video-production.md](.claude/skills/video-production.md) - 完整制作流程
3. **实践**: [merge_runway_videos.py](merge_runway_videos.py) - 主合成脚本
4. **优化**: [CLEANUP_RECOMMENDATION.md](CLEANUP_RECOMMENDATION.md) - 项目清理建议

### FFmpeg学习要点

本项目涉及的FFmpeg核心技术：

```bash
# 视频速度调整
ffmpeg -i input.mp4 -filter:v "setpts=1.087*PTS" output.mp4

# 音频填充与裁剪
ffmpeg -i input.mp3 -af "apad,atrim=0:10.5" output.mp3

# 音频混音
ffmpeg -i narration.aac -i bgm.mp3 \
  -filter_complex "[0:a][1:a]amix=inputs=2:duration=first:weights=1.0 0.2" \
  output.aac

# 字幕烧录
ffmpeg -i video.mp4 \
  -vf "subtitles=subtitle.srt:force_style='FontName=PingFang SC,FontSize=26'" \
  output.mp4
```

## 🎓 适用场景

本项目的方法和代码可以应用于：

### 文化传播
- 传统文化科普视频
- 历史故事讲述
- 艺术作品解读

### 教育培训
- 在线课程开场视频
- 知识点讲解动画
- 学习总结短片

### 企业宣传
- 品牌故事视频
- 产品功能演示
- 员工培训材料

### 社交媒体
- 抖音/快手短视频
- 公众号推文配图
- B站UP主内容

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 贡献方式

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

### 改进建议

- 添加更多AI视频生成平台支持（Pika, Kling等）
- 支持更多字幕样式模板
- 添加转场效果
- 支持批量处理多个项目

## 📝 版本历史

- **V7** (2026-01-03) - 字幕位置优化（MarginV=15）
- **V6** (2026-01-03) - 字幕位置调整（MarginV=30）
- **V5** (2026-01-03) - 场景音频独立同步 + BGM混音
- **V4** (2026-01-03) - 短片段减速处理优化
- **V3** (2026-01-03) - 字幕时间轴精确对齐
- **V2** (2026-01-03) - 音频循环修复
- **V1** (2026-01-03) - 初始版本

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 👤 作者

**James Wu**
- GitHub: [@JamesWuHK](https://github.com/JamesWuHK)
- 项目链接: [https://github.com/JamesWuHK/wanli-video](https://github.com/JamesWuHK/wanli-video)

## 🙏 致谢

- **Runway** - 提供强大的Gen-3视频生成能力
- **Azure** - 提供自然的TTS语音合成
- **FFmpeg** - 开源视频处理的瑞士军刀
- **Claude** - 协助整个项目的开发和优化

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 [GitHub Issue](https://github.com/JamesWuHK/wanli-video/issues)
- 发起 [GitHub Discussion](https://github.com/JamesWuHK/wanli-video/discussions)

---

⭐ 如果这个项目对你有帮助，请给个Star支持一下！

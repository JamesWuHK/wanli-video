# 文脉薪传 & 青云API 项目

这是一个从 demo-video-generator 项目中提取出来的独立项目，专门用于文脉薪传视频生成和青云API相关的功能。

## 项目结构

```
wanli-qingyun-project/
├── README.md                    # 项目说明文档
├── 文脉薪传_儒家五常_分镜头脚本.yaml  # 儒家五常分镜头脚本
├── 文脉薪传_细化脚本.yaml            # 详细脚本配置
├── scripts/                     # Python脚本目录
│   ├── generate_images_qingyun.py           # 青云API图像生成
│   ├── generate_wanli_poster_doubao.py      # 豆包API海报生成
│   ├── generate_wanli_newyear_poster.py     # 新年海报生成
│   ├── generate_images_chinese.py           # 中文图像生成
│   ├── generate_keyframes.py                # 关键帧生成
│   ├── generate_keyframes_parallel.py       # 并行关键帧生成
│   ├── generate_storyboard_images.py        # 分镜图像生成
│   ├── generate_ai_images.py                # AI图像生成
│   ├── generate_scene_videos.py             # 场景视频生成
│   ├── generate_scene_videos_with_narration.py  # 带旁白的场景视频
│   ├── merge_final_video.py                 # 视频合并
│   ├── generate_final_video_with_bgm.py     # 添加BGM的最终视频
│   └── create_storyboard_visualization.py   # 分镜可视化
├── examples/                    # 配置示例
│   ├── wanli_essay_demo.yaml              # 文章演示配置
│   ├── wanli_test.yaml                    # 测试配置
│   ├── wanli_claude_haiku_3.yaml          # Claude Haiku配置
│   ├── wanli_claude_sonnet_4_5.yaml       # Claude Sonnet配置
│   └── wanli_deepseek.yaml                # DeepSeek配置
├── storyboards/                 # 分镜板目录
│   └── 文脉薪传/                 # 文脉薪传项目分镜
│       ├── README.md            # 项目说明
│       ├── 使用指南.md          # 使用指南
│       ├── 青云API使用说明.md   # 青云API文档
│       ├── scene_videos/        # 场景视频
│       ├── ai_generated_images/ # AI生成的图像
│       └── *.json               # 分镜设计文件
├── output/                      # 输出文件目录
│   ├── wanli_essay_demo.mp4     # 演示视频
│   ├── wanli_claude_haiku_3.mp4 # Claude Haiku生成的视频
│   ├── wanli_claude_sonnet_4_5.mp4  # Claude Sonnet生成的视频
│   ├── wanli_deepseek.mp4       # DeepSeek生成的视频
│   └── *.srt                    # 字幕文件
└── docs/                        # 文档目录
    ├── BGM添加完成报告.md       # BGM添加报告
    ├── 最终步骤_添加真实BGM.md  # BGM添加步骤
    ├── 如何手动添加BGM.md       # BGM手动添加指南
    ├── 快速添加BGM.sh           # BGM快速添加脚本
    └── 启动说明.md              # 项目启动说明
```

## 主要功能

### 1. 青云API图像生成
- 使用青云API生成高质量的AI图像
- 支持中文提示词
- 参考脚本：`scripts/generate_images_qingyun.py`

### 2. 文脉薪传视频项目
- 儒家五常主题视频生成
- 分镜头设计和可视化
- 场景视频生成和合并
- 支持添加旁白和BGM

### 3. 多AI模型支持
- Claude Haiku 3
- Claude Sonnet 4.5
- DeepSeek
- 豆包API

## 快速开始

### 查看分镜设计
详细的分镜设计和使用说明请查看：
- [storyboards/文脉薪传/README.md](storyboards/文脉薪传/README.md)
- [storyboards/文脉薪传/使用指南.md](storyboards/文脉薪传/使用指南.md)

### 使用青云API
青云API的详细使用说明：
- [storyboards/文脉薪传/青云API使用说明.md](storyboards/文脉薪传/青云API使用说明.md)

### 生成视频
1. 配置YAML文件（参考 `examples/` 目录中的示例）
2. 运行对应的生成脚本
3. 查看输出结果在 `output/` 目录

### 添加BGM
参考文档：
- [docs/如何手动添加BGM.md](docs/如何手动添加BGM.md)
- [docs/最终步骤_添加真实BGM.md](docs/最终步骤_添加真实BGM.md)

或使用快速脚本：
```bash
bash docs/快速添加BGM.sh
```

## 成果展示

项目已生成的视频文件位于 `output/` 目录：
- `wanli_essay_demo.mp4` - 主要演示视频
- `wanli_claude_haiku_3.mp4` - Claude Haiku版本
- `wanli_claude_sonnet_4_5.mp4` - Claude Sonnet版本
- `wanli_deepseek.mp4` - DeepSeek版本

最终完整版视频：
- `storyboards/文脉薪传/文脉薪传_最终版V3.mp4`
- `storyboards/文脉薪传/文脉薪传_完整版_带BGM.mp4`

## 注意事项

1. 使用前请确保已配置好相应的API密钥
2. 青云API和其他AI服务可能需要付费
3. 生成视频可能需要较长时间，请耐心等待
4. 详细使用说明请查看各个文档文件

## 相关文档

- [BGM添加完成报告](docs/BGM添加完成报告.md)
- [启动说明](docs/启动说明.md)
- [青云API使用说明](storyboards/文脉薪传/青云API使用说明.md)
- [图像生成最终方案](storyboards/文脉薪传/图像生成最终方案.md)

## 技术栈

- Python 3.x
- 各类AI API（青云、豆包、Claude、DeepSeek等）
- 视频处理工具
- YAML配置管理

## 授权说明

本项目从 demo-video-generator 项目中提取，包含文脉薪传和青云API相关的所有资源和代码。

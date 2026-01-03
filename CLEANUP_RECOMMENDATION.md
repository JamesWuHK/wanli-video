# 项目文件清理建议

## 📁 文件分类与清理建议

### ✅ 保留 - 核心里程碑文件

#### 1. 最终成品视频
```
✓ storyboards/文脉薪传/文脉薪传_Runway_最终版_V7.mp4  (18.7 MB - 最终版本)
```
**说明**: V7是最终确定版本，字幕位置最优

#### 2. 核心脚本（可复用）
```
✓ merge_runway_videos.py                    (主合成脚本 - 最重要)
✓ scripts/generate_scene_videos.py          (场景视频生成)
✓ scripts/generate_scene_videos_with_narration.py  (带画外音的场景生成)
✓ scripts/merge_videos.py                   (视频合并工具)
✓ scripts/runway_batch_generate.py          (Runway批量生成)
```

#### 3. 技能文档
```
✓ .claude/skills/video-production.md        (视频制作完整流程文档)
```

#### 4. 项目配置
```
✓ storyboards/文脉薪传/complete_storyboard_design.json  (完整分镜脚本)
✓ 文脉薪传_细化脚本.yaml                     (细化脚本)
```

#### 5. 核心素材（用于最终成品）
```
✓ videos/*.mp4                               (13个Runway生成的视频片段)
✓ storyboards/文脉薪传/final_videos/audio/*  (13个画外音文件)
✓ storyboards/文脉薪传/final_videos/temp/*.srt  (13个字幕文件)
✓ storyboards/文脉薪传/bgm/china-chinese-asian-music-346568.mp3  (BGM)
```

#### 6. 重要文档
```
✓ README.md                                  (项目说明)
✓ storyboards/文脉薪传/使用指南.md
✓ storyboards/文脉薪传/交付清单.md
```

---

### 🗑️ 可删除 - 临时文件

#### 1. 临时音频处理文件 (130 MB)
```
❌ storyboards/文脉薪传/temp_audio/*_slowed.mp3  (13个文件 - 已用于合成)
❌ storyboards/文脉薪传/merged_narration.aac     (中间产物)
❌ storyboards/文脉薪传/reference_audio.aac      (从参考视频提取)
```
**原因**: 这些是音频处理的中间文件，最终成品已包含

#### 2. 临时视频延长文件 (20 MB)
```
❌ storyboards/文脉薪传/temp_extended/*.mp4     (2个文件)
```
**原因**: 短片段延长的临时文件，已合成到最终视频

#### 3. 历史版本视频 (V1-V6) (100+ MB)
```
❌ storyboards/文脉薪传/文脉薪传_Runway_最终版.mp4
❌ storyboards/文脉薪传/文脉薪传_Runway_最终版_V2.mp4
❌ storyboards/文脉薪传/文脉薪传_Runway_最终版_V3.mp4
❌ storyboards/文脉薪传/文脉薪传_Runway_最终版_V4.mp4
❌ storyboards/文脉薪传/文脉薪传_Runway_最终版_V5.mp4
❌ storyboards/文脉薪传/文脉薪传_Runway_最终版_V6.mp4
```
**原因**: 迭代过程的历史版本，保留V7即可

#### 4. 其他历史成品 (80+ MB)
```
❌ storyboards/文脉薪传/文脉薪传_完整版.mp4
❌ storyboards/文脉薪传/文脉薪传_完整版_带BGM.mp4
❌ storyboards/文脉薪传/文脉薪传_带演示BGM.mp4
❌ storyboards/文脉薪传/文脉薪传_最终版.mp4
❌ storyboards/文脉薪传/文脉薪传_最终版V2.mp4
❌ storyboards/文脉薪传/文脉薪传_最终版V3.mp4
```
**原因**: 早期版本，使用VectorEngine生成的旧版本

#### 5. 测试视频文件 (150+ MB)
```
❌ test_*.mp4                                 (根目录下所有测试文件)
❌ enhanced_kenburns_*.mp4                    (Ken Burns效果测试)
❌ scene_01_to_02_runway.mp4                  (转场测试)
❌ scene_07_ai_test.mp4                       (AI测试)
❌ test_enhanced_kenburns/*.mp4               (测试文件夹)
```
**原因**: 功能测试文件，已完成测试

#### 6. 示例输出文件 (60+ MB)
```
❌ output/*.mp4                               (示例视频输出)
❌ output/*.srt                               (示例字幕输出)
```
**原因**: 其他示例脚本的输出，非核心项目内容

#### 7. 冗余的中间素材
```
❌ storyboards/文脉薪传/scene_videos/*        (整个文件夹 - 早期版本)
❌ storyboards/文脉薪传/dynamic_videos_ve/*   (整个文件夹 - VectorEngine版本)
```
**原因**: 这些是用VectorEngine生成的早期版本，已被Runway版本替代

#### 8. 文本临时文件
```
❌ storyboards/文脉薪传/dynamic_videos_ve/merge_list.txt
❌ storyboards/文脉薪传/dynamic_videos_ve/videos/merge_list.txt
❌ storyboards/文脉薪传/merged_subtitles.srt  (已烧录到视频中)
```
**原因**: FFmpeg临时列表文件，可随时重新生成

---

### ⚠️ 可选保留 - 根据需求决定

#### 1. 测试脚本
```
? test_runway_api.py
? test_runway_api_v2.py
? test_ve_api.py
? runway_api_helper.py
```
**说明**: 如果不再需要测试API，可删除

#### 2. 单场景设计JSON
```
? storyboards/文脉薪传/scene_*_design.json    (13个文件)
```
**说明**: 已整合到complete_storyboard_design.json中，可删除

#### 3. 文档说明
```
? storyboards/文脉薪传/13个场景中文提示词.txt
? storyboards/文脉薪传/AI图像生成指南.md
? storyboards/文脉薪传/分镜设计文档.md
? storyboards/文脉薪传/图像生成最终方案.md
? storyboards/文脉薪传/如何添加BGM.md
? storyboards/文脉薪传/快速访问指南.md
? storyboards/文脉薪传/生成进度.md
? storyboards/文脉薪传/生成进度总结.md
? storyboards/文脉薪传/青云API使用说明.md
? storyboards/文脉薪传/项目完成总结.md
? docs/*.md
```
**说明**: 过程文档，如果只需最终结果可删除，建议保留部分核心文档

#### 4. 不再使用的脚本
```
? scripts/generate_dynamic_videos_vectorengine.py
? scripts/vectorengine_client.py
? scripts/vectorengine_client_old.py
? scripts/merge_videos_simple.py
? scripts/compose_final_video.py
```
**说明**: VectorEngine相关脚本，已改用Runway

---

## 📊 存储空间估算

### 当前占用
- **视频文件总计**: ~800 MB
  - 最终成品 V7: 18.7 MB
  - 历史版本 (V1-V6): ~100 MB
  - 早期成品版本: ~80 MB
  - 测试文件: ~150 MB
  - 中间素材: ~400 MB
  - 示例输出: ~60 MB

- **音频文件总计**: ~180 MB
  - 场景音频 (必需): ~15 MB
  - 临时处理文件: ~130 MB
  - BGM: ~5 MB

### 清理后预期
- **保留必需文件**: ~300 MB
  - 最终成品 V7: 18.7 MB
  - Runway视频片段 (13个): ~150 MB
  - 场景音频: ~15 MB
  - 字幕文件: ~1 MB
  - BGM: ~5 MB
  - 脚本和文档: ~10 MB
  - 其他必需素材: ~100 MB

- **可节省空间**: ~680 MB (85%)

---

## 🛠️ 清理命令

### 方案A: 激进清理（节省680 MB）
```bash
# 删除所有临时和历史文件
cd /Users/wujames/cursor_prj/wanli-qingyun-project

# 1. 删除临时音频
rm -rf storyboards/文脉薪传/temp_audio
rm -f storyboards/文脉薪传/merged_narration.aac
rm -f storyboards/文脉薪传/reference_audio.aac

# 2. 删除临时视频延长文件
rm -rf storyboards/文脉薪传/temp_extended

# 3. 删除历史版本（保留V7）
rm -f storyboards/文脉薪传/文脉薪传_Runway_最终版.mp4
rm -f storyboards/文脉薪传/文脉薪传_Runway_最终版_V2.mp4
rm -f storyboards/文脉薪传/文脉薪传_Runway_最终版_V3.mp4
rm -f storyboards/文脉薪传/文脉薪传_Runway_最终版_V4.mp4
rm -f storyboards/文脉薪传/文脉薪传_Runway_最终版_V5.mp4
rm -f storyboards/文脉薪传/文脉薪传_Runway_最终版_V6.mp4

# 4. 删除早期版本
rm -f storyboards/文脉薪传/文脉薪传_完整版.mp4
rm -f storyboards/文脉薪传/文脉薪传_完整版_带BGM.mp4
rm -f storyboards/文脉薪传/文脉薪传_带演示BGM.mp4
rm -f storyboards/文脉薪传/文脉薪传_最终版.mp4
rm -f storyboards/文脉薪传/文脉薪传_最终版V2.mp4
rm -f storyboards/文脉薪传/文脉薪传_最终版V3.mp4

# 5. 删除测试文件
rm -f test_*.mp4
rm -f enhanced_kenburns_*.mp4
rm -f scene_01_to_02_runway.mp4
rm -f scene_07_ai_test.mp4
rm -rf test_enhanced_kenburns

# 6. 删除示例输出
rm -rf output

# 7. 删除早期中间素材（VectorEngine版本）
rm -rf storyboards/文脉薪传/scene_videos
rm -rf storyboards/文脉薪传/dynamic_videos_ve

# 8. 删除临时文本文件
rm -f storyboards/文脉薪传/merged_subtitles.srt

# 9. 删除单场景设计JSON（已整合）
rm -f storyboards/文脉薪传/scene_*_design.json
```

### 方案B: 保守清理（节省400 MB）
```bash
# 仅删除明确的临时文件
cd /Users/wujames/cursor_prj/wanli-qingyun-project

# 1. 删除临时处理文件
rm -rf storyboards/文脉薪传/temp_audio
rm -rf storyboards/文脉薪传/temp_extended
rm -f storyboards/文脉薪传/merged_narration.aac
rm -f storyboards/文脉薪传/reference_audio.aac
rm -f storyboards/文脉薪传/merged_subtitles.srt

# 2. 删除历史版本V1-V5（保留V6和V7供对比）
rm -f storyboards/文脉薪传/文脉薪传_Runway_最终版.mp4
rm -f storyboards/文脉薪传/文脉薪传_Runway_最终版_V2.mp4
rm -f storyboards/文脉薪传/文脉薪传_Runway_最终版_V3.mp4
rm -f storyboards/文脉薪传/文脉薪传_Runway_最终版_V4.mp4
rm -f storyboards/文脉薪传/文脉薪传_Runway_最终版_V5.mp4

# 3. 删除测试文件
rm -f test_*.mp4
rm -f enhanced_kenburns_*.mp4
rm -rf test_enhanced_kenburns

# 4. 删除早期VectorEngine版本素材
rm -rf storyboards/文脉薪传/dynamic_videos_ve
```

---

## 📋 核心文件清单（清理后保留）

### 必需保留的文件结构
```
project/
├── .claude/
│   └── skills/
│       └── video-production.md              ★ 视频制作技能文档
├── merge_runway_videos.py                   ★ 主合成脚本
├── README.md                                ★ 项目说明
├── 文脉薪传_细化脚本.yaml                    ★ 脚本配置
├── scripts/
│   ├── generate_scene_videos.py             (可选：场景生成)
│   ├── merge_videos.py                      (可选：合并工具)
│   └── runway_batch_generate.py             (可选：批量生成)
├── videos/
│   └── *.mp4                                ★ 13个Runway视频片段
└── storyboards/文脉薪传/
    ├── complete_storyboard_design.json      ★ 完整分镜脚本
    ├── 文脉薪传_Runway_最终版_V7.mp4        ★ 最终成品
    ├── 使用指南.md                          ★ 使用说明
    ├── 交付清单.md                          ★ 交付文档
    ├── bgm/
    │   └── china-chinese-asian-music-346568.mp3  ★ BGM
    └── final_videos/
        ├── audio/
        │   └── *.mp3                        ★ 13个画外音
        └── temp/
            └── *.srt                        ★ 13个字幕文件
```

---

## ✅ 执行建议

1. **先备份整个项目**（以防万一）
   ```bash
   cp -r /Users/wujames/cursor_prj/wanli-qingyun-project \
         /Users/wujames/cursor_prj/wanli-qingyun-project_backup_2026-01-03
   ```

2. **查看当前占用**
   ```bash
   du -sh /Users/wujames/cursor_prj/wanli-qingyun-project
   ```

3. **执行清理**（建议先用方案B，观察效果后再决定是否用方案A）

4. **验证最终成品可用**
   ```bash
   open /Users/wujames/cursor_prj/wanli-qingyun-project/storyboards/文脉薪传/文脉薪传_Runway_最终版_V7.mp4
   ```

5. **再次查看占用**
   ```bash
   du -sh /Users/wujames/cursor_prj/wanli-qingyun-project
   ```

---

## 🎯 推荐方案

**建议使用方案A（激进清理）**，原因：
- ✓ 最终成品V7已完美，无需历史版本
- ✓ 临时文件已无用，可随时重新生成
- ✓ 节省680 MB空间（85%）
- ✓ 保留了所有可复用脚本和核心素材
- ✓ 项目结构更清晰，便于后续维护

如有需要历史版本对比，可从备份中提取。

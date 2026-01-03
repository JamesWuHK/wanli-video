# 如何为视频添加背景音乐（BGM）

## 📝 当前状态

✅ 已完成：
- 所有13个场景视频（带修复后的字幕）
- 最终合并视频（无BGM版本）

📹 视频位置：
- `storyboards/文脉薪传/文脉薪传_完整版_带BGM.mp4` （目前无BGM）
- `storyboards/文脉薪传/final_videos/` （各场景视频）

---

## 🎵 步骤1：准备背景音乐

### 推荐的BGM风格

- **风格**：中国风、古典音乐
- **乐器**：古筝、琵琶、二胡等传统乐器
- **时长**：至少90秒（视频总长89.3秒）
- **氛围**：舒缓、悠扬、适合文化类纪录片

### 免费BGM资源

1. **爱给网** - https://www.aigei.com/music/
   - 搜索"古筝"、"中国风"、"传统"
   - 下载MP3格式

2. **Pixabay Music** - https://pixabay.com/music/
   - 搜索 "Chinese" 或 "Traditional"
   - 免费且无版权

3. **YouTube Audio Library**
   - 搜索 "Chinese Traditional" 或 "Guzheng"

4. **Incompetech** - https://incompetech.com/
   - 搜索 "Eastern" 分类

### 推荐曲目关键词

- "高山流水"
- "春江花月夜"
- "梅花三弄"
- "渔舟唱晚"

---

## 🎬 步骤2：添加BGM到视频

### 方法1：使用提供的脚本（推荐）

```bash
# 1. 将BGM文件放入bgm目录
cp your_bgm.mp3 storyboards/文脉薪传/bgm/background_music.mp3

# 2. 运行添加BGM脚本
source venv/bin/activate
python add_bgm_to_video.py \
  --video "storyboards/文脉薪传/文脉薪传_完整版_带BGM.mp4" \
  --bgm "storyboards/文脉薪传/bgm/background_music.mp3" \
  --output "storyboards/文脉薪传/文脉薪传_最终版_带BGM.mp4" \
  --volume 0.15
```

**参数说明**：
- `--video`: 输入视频路径
- `--bgm`: 背景音乐路径
- `--output`: 输出视频路径
- `--volume`: BGM音量（0.0-1.0），默认0.15（15%音量）

### 方法2：手动使用FFmpeg

```bash
ffmpeg -y \
  -i "storyboards/文脉薪传/文脉薪传_完整版_带BGM.mp4" \
  -stream_loop -1 \
  -i "storyboards/文脉薪传/bgm/your_bgm.mp3" \
  -filter_complex \
  "[0:a]volume=1.0[a0];[1:a]volume=0.15[a1];[a0][a1]amix=inputs=2:duration=first[aout]" \
  -map 0:v \
  -map "[aout]" \
  -c:v copy \
  -c:a aac \
  -b:a 192k \
  -shortest \
  "storyboards/文脉薪传/文脉薪传_最终版_带BGM.mp4"
```

---

## ⚙️ 调整BGM音量

如果BGM太响或太小，调整 `--volume` 参数：

- **更小声**：`--volume 0.10` （10%）
- **默认**：`--volume 0.15` （15%）
- **更响亮**：`--volume 0.25` （25%）

---

## 📊 技术说明

### 音频混合原理

脚本会：
1. 保持原视频画外音音量为100%
2. 将BGM音量降低到15%（或您指定的音量）
3. 混合两个音轨
4. BGM循环播放直到视频结束

### 输出质量

- **视频编码**：复制原视频（无质量损失）
- **音频编码**：AAC 192kbps（高质量）
- **文件大小**：约增加1-2MB

---

## ✅ 完成后

添加BGM后，您将得到：

**最终作品**：`文脉薪传_最终版_带BGM.mp4`

包含：
- ✅ 高清画面（2048x1152, 16:9）
- ✅ 修复后的字幕
- ✅ 画外音解说
- ✅ 背景音乐
- ✅ 专业过渡效果

---

## 💡 提示

1. **测试音量**：先用 `--volume 0.15` 生成，如果需要调整再重新生成
2. **BGM长度**：如果BGM短于视频，脚本会自动循环播放
3. **文件格式**：BGM支持 MP3、WAV、AAC 等常见格式
4. **预览**：生成后可以先预览，确认效果满意

---

## 🆘 常见问题

**Q: 没有BGM文件怎么办？**
A: 可以从上述免费资源网站下载，或暂时不添加BGM

**Q: BGM音量太大或太小？**
A: 调整 `--volume` 参数并重新运行脚本

**Q: 可以添加多段不同的BGM吗？**
A: 需要手动使用更复杂的FFmpeg命令，建议使用视频编辑软件

**Q: 原视频画外音听不清楚？**
A: 降低BGM音量到 0.10 或更低

---

如有任何问题，请随时询问！

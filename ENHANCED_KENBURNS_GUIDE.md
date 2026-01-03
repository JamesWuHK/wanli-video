# 增强版 Ken Burns 效果说明

## ✅ 核心优势

**100% 保留设计稿内容**：
- ✅ 完整保留所有中文文字（仁义礼智信 等）
- ✅ 保留设计图的字体、排版、布局
- ✅ 保留所有视觉设计细节
- ✅ 零成本，无需 API 调用

**电影级动画效果**：
- 使用数学缓动曲线（easing curves）
- 模拟专业电影镜头运动
- 自然流畅的动画过渡

---

## 🎬 可用效果列表

### 1. zoom_in - 缓慢推进
**用途**：开场、强调、引入
**效果**：使用二次缓动曲线(t²)，慢-快-慢推进，电影感十足
```
适用场景：scene_01_opening, scene_07_grand_finale
```

### 2. zoom_out - 缓慢拉远
**用途**：展示全貌、收尾、介绍
**效果**：反向二次曲线，从近到远的展示
```
适用场景：intro 系列, history 系列
```

### 3. pan_right - 右移+缩放
**用途**：展现现代化、进步感
**效果**：向右平移配合正弦波缩放，增加动态感
```
适用场景：modern 系列场景
```

### 4. pan_left - 左移+缩放
**用途**：回顾历史、传统感
**效果**：向左平移配合动态缩放
```
适用场景：传统文化介绍
```

### 5. pan_up - 上移+缩放
**用途**：升腾感、希望感
**效果**：向上移动配合缩放，营造积极向上的氛围
```
适用场景：结尾、展望未来
```

### 6. diagonal_in - 对角线推进
**用途**：经典电影镜头、艺术感
**效果**：从右下到左上的对角线推进+缩放
```
适用场景：艺术性强的场景
```

### 7. circular - 圆周运动
**用途**：生动活泼、吸引注意
**效果**：圆周轨迹运动配合呼吸式缩放
```
适用场景：需要特别强调的内容
```

### 8. breathe - 呼吸感缩放
**用途**：沉浸感、冥想感
**效果**：使用正弦波(sin)实现慢-快-慢的自然呼吸节奏
```
适用场景：哲学内涵、意境表达
```

---

## 📝 技术细节

### 缓动函数说明

1. **二次缓动 (Quadratic Easing)**
   ```
   z = 1.0 + 0.4 * pow(t, 2)
   ```
   - t = on/duration（0 到 1）
   - 开始慢、中间快、结束慢
   - 最自然的推进/拉远效果

2. **正弦波 (Sinusoidal)**
   ```
   z = 1.0 + 0.15 * sin(t * PI)
   ```
   - 完美的对称曲线
   - 适合呼吸、震动等周期性动画

3. **圆周运动 (Circular Motion)**
   ```
   x = 100 * sin(t * 2 * PI)
   y = 60 * cos(t * 2 * PI)
   ```
   - 创建平滑的圆周轨迹
   - 配合缩放增加立体感

### 视频参数

- **分辨率**：2048x1152 (16:9)
- **帧率**：30fps
- **编码**：H.264 (libx264)
- **质量**：CRF 18（高质量）
- **预设**：slow（更好的压缩效率）

---

## 🎯 智能效果选择逻辑

脚本会根据场景ID自动选择最合适的效果：

```python
if 'opening' in scene_id or 'grand' in scene_id:
    effect = "zoom_in"  # 开场和结尾用推进
elif 'intro' in scene_id or 'history' in scene_id:
    effect = "zoom_out"  # 介绍性场景用拉远
elif 'modern' in scene_id:
    effect = "pan_right"  # 现代场景用平移
else:
    # 按序号循环使用所有效果
    effect = effects[scene_index % 8]
```

---

## 🆚 对比 AI 图生视频

### AI 方案（VEO、Sora、Kling）
- ❌ **不保留原图文字** - AI 重新生成场景
- ❌ **成本高** - 每次 ¥0.078 - ¥0.30
- ❌ **不可控** - 生成结果随机
- ❌ **需要等待** - 1-2分钟生成时间
- ✅ 可能产生物体运动（但我们不需要）

### 增强版 Ken Burns
- ✅ **100% 保留文字** - 所有设计内容完整
- ✅ **零成本** - 本地 FFmpeg 处理
- ✅ **完全可控** - 精确控制每个参数
- ✅ **快速生成** - 5秒视频约15秒完成
- ✅ **专业效果** - 电影级缓动曲线

---

## 📦 测试视频对比

已生成测试视频（使用 scene_01_opening.png）：

1. `enhanced_kenburns_zoom_in.mp4` - 缓慢推进（1.1MB，5秒）
2. `enhanced_kenburns_circular.mp4` - 圆周运动（2.2MB，5秒）
3. `enhanced_kenburns_diagonal.mp4` - 对角线推进（1.3MB，5秒）
4. `enhanced_kenburns_breathe.mp4` - 呼吸感缩放（0.8MB，5秒）

**请对比查看效果，确认是否满足需求。**

---

## 🚀 批量生成

确认效果满意后，运行以下命令生成所有13个场景：

```bash
# 使用增强版 Ken Burns（USE_AI=false）
export USE_AI=false
python3 scripts/generate_dynamic_videos_vectorengine.py
```

或使用 Docker：

```bash
docker run --rm \
  -v /Users/wujames/cursor_prj/wanli-qingyun-project/storyboards:/app/storyboards \
  -e USE_AI=false \
  video-generator:latest
```

预计耗时：约 3-5 分钟（13个场景，并发处理）

---

## 📋 总结

**推荐方案**：增强版 Ken Burns

**理由**：
1. 完美保留设计稿的中文文字和视觉设计
2. 零成本，无需 API 调用
3. 专业的电影级动画效果
4. 完全可控，可精确调整每个参数
5. 快速生成，支持并发处理

AI 图生视频虽然能产生物体运动，但会丢失原始设计的文字内容，不符合本项目需求。

---

**创建时间**：2026-01-03
**状态**：✅ 已实现并测试通过

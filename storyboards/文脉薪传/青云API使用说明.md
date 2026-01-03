# 青云API图像生成说明

## ✅ 已完成配置

您的青云API已经配置完成并开始生成图像！

### 📋 配置信息

- **API密钥**: sk-KfCX4tI7rDBtC7mynLmFj1z9D90HaO1oCQrVt61y9EXQ2vs1
- **接口地址**: https://api.qingyuntop.top/v1
- **使用模型**: DALL-E 3 (高质量)
- **生成数量**: 13张场景设计图

### 💰 成本估算

- **单张成本**: 约 $0.04
- **总成本**: 约 $0.52 (13张)
- **生成时间**: 5-10分钟

## 🚀 正在生成

脚本正在后台运行，为以下13个场景生成设计图：

1. scene_01_opening - 开篇·薪火相传
2. scene_02_ren_intro - 仁·古代
3. scene_02_ren_modern - 仁·现代
4. scene_03_yi_history - 义·历史
5. scene_03_yi_modern - 义·现代
6. scene_04_li_tradition - 礼·传统
7. scene_04_li_modern - 礼·现代
8. scene_05_zhi_ancient - 智·古代
9. scene_05_zhi_modern - 智·现代
10. scene_06_xin_principle - 信·原则
11. scene_06_xin_modern - 信·现代
12. scene_07_heritage_education - 传承·教育
13. scene_07_grand_finale - 传承·升华

## 📁 输出位置

生成的图像将保存在：
```
storyboards/文脉薪传/qingyun_images/
```

每个文件命名格式：`{场景ID}.png`

## 🔍 查看进度

您可以随时查看生成进度：

```bash
# 查看输出目录
ls -lh storyboards/文脉薪传/qingyun_images/

# 查看已生成的图片数量
ls storyboards/文脉薪传/qingyun_images/*.png 2>/dev/null | wc -l

# 查看最新生成的图片
ls -lt storyboards/文脉薪传/qingyun_images/ | head -5
```

## ⚠️ 注意事项

### 速率限制
- 脚本已设置每次生成间隔2秒
- 如遇速率限制错误，会自动记录失败场景
- 可以稍后重新运行，脚本会跳过已存在的图片

### 可能的问题

**问题1: API额度不足**
- 解决：访问 https://chaxun.wlai.vip/ 查询余额
- 如需充值，请访问青云API官网

**问题2: 生成失败**
- 解决：检查网络连接
- 删除失败场景的文件，重新运行脚本

**问题3: 图像质量不满意**
- 解决：可以修改脚本中的提示词
- 或使用 dall-e-2 模型（更便宜，质量略低）

## 🎨 生成后操作

### 1. 查看所有图像
```bash
open storyboards/文脉薪传/qingyun_images/
```

### 2. 筛选和优化
- 查看每张图片
- 如有不满意的，可删除后重新生成
- 或使用图片编辑软件调整

### 3. 重新生成特定场景
```bash
# 删除不满意的图片
rm storyboards/文脉薪传/qingyun_images/scene_01_opening.png

# 重新运行脚本（会自动跳过已存在的）
python generate_images_qingyun.py
```

### 4. 更换模型
```bash
# 使用 DALL-E 2（更便宜：$0.02/张）
python generate_images_qingyun.py --model dall-e-2

# 自定义输出目录
python generate_images_qingyun.py \
  --model dall-e-3 \
  --output storyboards/文脉薪传/qingyun_hd_images
```

## 📚 青云API资源

- **官网**: https://api.qingyuntop.top
- **文档**: https://api.qingyuntop.top/about
- **定价**: https://api.qingyuntop.top/pricing
- **额度查询**: https://chaxun.wlai.vip/
- **综合资源站**: https://qingyuntop.top

## 💡 提示

### 优化提示词
如果生成的图片不够满意，可以：

1. 编辑 `文脉薪传_细化脚本.yaml`
2. 修改对应场景的 `image_generation_prompt`
3. 删除旧图片
4. 重新运行生成脚本

### 批量处理
```bash
# 只生成前3个场景（测试）
# 需要手动修改脚本，添加切片：scenes[:3]

# 只生成失败的场景
# 脚本会自动跳过已存在的文件
```

## ✨ 后续步骤

生成完成后：

1. ✅ 查看并筛选图像
2. ✅ 开始视频制作
3. ✅ 参考《使用指南.md》选择制作路径

---

**预计完成时间**: 5-10分钟

**当前状态**: 🔄 生成中...

请稍候，图像生成完成后会有通知！

#!/bin/bash
# 快速添加BGM到最终视频
# 使用方法：将BGM文件放到 storyboards/文脉薪传/bgm/ 目录后运行此脚本

set -e  # 遇到错误立即退出

echo "════════════════════════════════════════════════════════════"
echo "🎵 文脉薪传 - 快速添加BGM工具"
echo "════════════════════════════════════════════════════════════"
echo ""

# 检查BGM目录
BGM_DIR="storyboards/文脉薪传/bgm"

if [ ! -d "$BGM_DIR" ]; then
    echo "❌ 错误：BGM目录不存在"
    exit 1
fi

# 查找BGM文件
echo "📁 查找BGM文件..."
BGM_FILES=($(find "$BGM_DIR" -name "*.mp3" -o -name "*.wav" -o -name "*.m4a" 2>/dev/null))

if [ ${#BGM_FILES[@]} -eq 0 ]; then
    echo "❌ 未找到BGM文件！"
    echo ""
    echo "请先下载BGM文件并放入目录："
    echo "  $BGM_DIR/"
    echo ""
    echo "推荐来源："
    echo "  1. Pixabay: https://pixabay.com/music/search/chinese/"
    echo "  2. YouTube Audio Library"
    echo "  3. FreePD: https://freepd.com/"
    echo ""
    exit 1
fi

# 显示找到的BGM文件
echo "✅ 找到以下BGM文件："
for i in "${!BGM_FILES[@]}"; do
    FILE_SIZE=$(du -h "${BGM_FILES[$i]}" | cut -f1)
    echo "  $((i+1)). $(basename "${BGM_FILES[$i]}") ($FILE_SIZE)"
done
echo ""

# 选择BGM文件
if [ ${#BGM_FILES[@]} -eq 1 ]; then
    SELECTED_BGM="${BGM_FILES[0]}"
    echo "🎵 自动选择: $(basename "$SELECTED_BGM")"
else
    echo "请选择要使用的BGM文件 (1-${#BGM_FILES[@]})："
    read -p "输入编号: " SELECTION

    if [[ ! "$SELECTION" =~ ^[0-9]+$ ]] || [ "$SELECTION" -lt 1 ] || [ "$SELECTION" -gt ${#BGM_FILES[@]} ]; then
        echo "❌ 无效选择"
        exit 1
    fi

    SELECTED_BGM="${BGM_FILES[$((SELECTION-1))]}"
fi

echo ""
echo "────────────────────────────────────────────────────────────"

# 询问音量
echo "🔊 请选择BGM音量："
echo "  1. 轻柔 (10%) - 纯背景衬托"
echo "  2. 标准 (15%) - 推荐，平衡度最佳"
echo "  3. 响亮 (20%) - 突出音乐氛围"
echo "  4. 自定义"
echo ""
read -p "输入选项 (1-4) [默认:2]: " VOLUME_CHOICE

case "${VOLUME_CHOICE:-2}" in
    1) VOLUME=0.10 ;;
    2) VOLUME=0.15 ;;
    3) VOLUME=0.20 ;;
    4)
        read -p "输入音量值 (0.0-1.0): " VOLUME
        if [[ ! "$VOLUME" =~ ^0\.[0-9]+$ ]] && [[ ! "$VOLUME" =~ ^1\.0$ ]]; then
            echo "❌ 无效音量值，使用默认值 0.15"
            VOLUME=0.15
        fi
        ;;
    *) VOLUME=0.15 ;;
esac

echo ""
echo "════════════════════════════════════════════════════════════"
echo "📋 执行参数："
echo "────────────────────────────────────────────────────────────"
echo "  输入视频: 文脉薪传_完整版.mp4"
echo "  背景音乐: $(basename "$SELECTED_BGM")"
echo "  BGM音量: $(echo "$VOLUME * 100" | bc)%"
echo "  输出视频: 文脉薪传_最终版.mp4"
echo "════════════════════════════════════════════════════════════"
echo ""

read -p "确认开始处理? (y/n) [y]: " CONFIRM
if [[ "${CONFIRM:-y}" != "y" ]] && [[ "${CONFIRM:-y}" != "Y" ]]; then
    echo "已取消"
    exit 0
fi

echo ""
echo "🎬 开始处理..."
echo ""

# 激活虚拟环境并执行
source venv/bin/activate

python add_bgm_to_video.py \
    --video "storyboards/文脉薪传/文脉薪传_完整版.mp4" \
    --bgm "$SELECTED_BGM" \
    --output "storyboards/文脉薪传/文脉薪传_最终版.mp4" \
    --volume "$VOLUME"

echo ""
echo "════════════════════════════════════════════════════════════"
echo "✅ 处理完成！"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "📁 最终视频位置："
echo "  storyboards/文脉薪传/文脉薪传_最终版.mp4"
echo ""

# 显示文件大小
FINAL_SIZE=$(du -h "storyboards/文脉薪传/文脉薪传_最终版.mp4" | cut -f1)
echo "📊 文件大小: $FINAL_SIZE"
echo ""

# 询问是否播放
read -p "是否立即播放视频? (y/n) [y]: " PLAY
if [[ "${PLAY:-y}" == "y" ]] || [[ "${PLAY:-y}" == "Y" ]]; then
    echo "🎥 正在打开视频..."
    open "storyboards/文脉薪传/文脉薪传_最终版.mp4"
fi

echo ""
echo "🎉 全部完成！感谢使用！"
echo ""

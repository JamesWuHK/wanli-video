FROM python:3.11-slim

# 使用国内镜像源
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources || \
    sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list

# 安装必要的系统依赖（如果还没有）
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY scripts/ /app/scripts/
COPY 文脉薪传_细化脚本.yaml /app/
COPY storyboards/ /app/storyboards/

# 使用国内 pip 镜像并只安装缺少的包
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    pip install --no-cache-dir \
    pyyaml \
    edge-tts \
    requests

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV USE_AI=false

# 运行命令
# 默认生成视频，可通过 docker run 参数覆盖
CMD ["python3", "scripts/generate_dynamic_videos_vectorengine.py"]

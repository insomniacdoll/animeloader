FROM python:3.12-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 创建非 root 用户
RUN useradd --create-home --shell /bin/bash app

# 创建必要的目录结构
RUN mkdir -p /home/app/.animeloader/data \
             /home/app/.animeloader/logs \
             /home/app/.animeloader/downloads

# 设置目录权限
RUN chown -R app:app /app /home/app/.animeloader
USER app

# 从 GitHub 下载预构建的二进制文件
# 注意：需要替换为实际的 GitHub 发布版本 URL
ARG GITHUB_RELEASE_URL="https://github.com/insomniacdoll/animeloader/releases/latest/download"
RUN curl -L ${GITHUB_RELEASE_URL}/animeloader-server -o /app/animeloader-server && \
    chmod +x /app/animeloader-server

# 创建默认配置文件
RUN mkdir -p /home/app/.animeloader && \
    echo "server:\n  host: \"0.0.0.0\"\n  port: 8000\n  debug: false\n\ndatabase:\n  path: \"~/.animeloader/data/animeloader.db\"\n\nlogging:\n  level: \"INFO\"\n  file: \"~/.animeloader/logs/animeloader.log\"\n\nscheduler:\n  enabled: true\n\nsmart_parser:\n  timeout: 30\n  user_agent: \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\"\n  max_results: 10\n  auto_add_rss: true" > /home/app/.animeloader/server_config.yaml

# 暴露端口
EXPOSE 8000

# 启动服务
CMD ["./animeloader-server"]
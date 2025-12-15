# 后端 Dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（用于 OpenCV 和其他库）
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir requests

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p uploads

# 设置权限
RUN chmod +x healthcheck.py

# 暴露端口
EXPOSE 5030

# 设置环境变量
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# 启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:5030", "--workers", "4", "--timeout", "120", "run:app"]

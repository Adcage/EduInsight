#!/bin/bash
# EduInsight Docker 快速启动脚本

set -e

echo "🚀 EduInsight Docker 部署脚本"
echo "================================"
echo ""

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: Docker 未安装"
    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ 错误: Docker Compose 未安装"
    echo "请先安装 Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# 选择环境
echo "请选择部署环境:"
echo "1) 开发环境 (支持热重载)"
echo "2) 生产环境"
read -p "请输入选项 (1 或 2): " env_choice

case $env_choice in
    1)
        echo ""
        echo "📦 启动开发环境..."
        docker-compose -f docker-compose.dev.yml up -d
        echo ""
        echo "✅ 开发环境启动成功!"
        echo ""
        echo "访问地址:"
        echo "  前端: http://localhost:5173"
        echo "  后端: http://localhost:5030"
        echo ""
        echo "查看日志: docker-compose -f docker-compose.dev.yml logs -f"
        ;;
    2)
        echo ""
        echo "📦 启动生产环境..."
        
        # 检查是否存在 .env 文件
        if [ ! -f .env ]; then
            echo "⚠️  警告: 未找到 .env 文件"
            read -p "是否创建默认配置? (y/n): " create_env
            if [ "$create_env" = "y" ]; then
                cat > .env << EOF
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=sqlite:///app.db
CORS_ORIGINS=http://localhost
EOF
                echo "✅ 已创建 .env 文件"
            fi
        fi
        
        docker-compose up -d
        echo ""
        echo "✅ 生产环境启动成功!"
        echo ""
        echo "访问地址:"
        echo "  前端: http://localhost"
        echo "  后端: http://localhost:5030"
        echo ""
        echo "查看日志: docker-compose logs -f"
        ;;
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac

echo ""
echo "其他命令:"
echo "  停止服务: docker-compose down"
echo "  重启服务: docker-compose restart"
echo "  查看状态: docker-compose ps"

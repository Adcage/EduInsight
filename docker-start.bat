@echo off
REM EduInsight Docker 快速启动脚本 (Windows)

echo ========================================
echo   EduInsight Docker 部署脚本
echo ========================================
echo.

REM 检查 Docker 是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Docker 未安装
    echo 请先安装 Docker Desktop: https://docs.docker.com/desktop/install/windows-install/
    pause
    exit /b 1
)

REM 检查 Docker Compose 是否可用
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Docker Compose 未安装
    pause
    exit /b 1
)

echo 请选择部署环境:
echo 1) 开发环境 (支持热重载)
echo 2) 生产环境
echo.
set /p env_choice="请输入选项 (1 或 2): "

if "%env_choice%"=="1" (
    echo.
    echo [启动] 开发环境...
    docker-compose -f docker-compose.dev.yml up -d
    echo.
    echo [成功] 开发环境启动成功!
    echo.
    echo 访问地址:
    echo   前端: http://localhost:5173
    echo   后端: http://localhost:5030
    echo.
    echo 查看日志: docker-compose -f docker-compose.dev.yml logs -f
) else if "%env_choice%"=="2" (
    echo.
    echo [启动] 生产环境...
    
    REM 检查 .env 文件
    if not exist .env (
        echo [警告] 未找到 .env 文件
        set /p create_env="是否创建默认配置? (y/n): "
        if /i "!create_env!"=="y" (
            echo SECRET_KEY=your-secret-key-change-in-production> .env
            echo DATABASE_URL=sqlite:///app.db>> .env
            echo CORS_ORIGINS=http://localhost>> .env
            echo [成功] 已创建 .env 文件
        )
    )
    
    docker-compose up -d
    echo.
    echo [成功] 生产环境启动成功!
    echo.
    echo 访问地址:
    echo   前端: http://localhost
    echo   后端: http://localhost:5030
    echo.
    echo 查看日志: docker-compose logs -f
) else (
    echo [错误] 无效选项
    pause
    exit /b 1
)

echo.
echo 其他命令:
echo   停止服务: docker-compose down
echo   重启服务: docker-compose restart
echo   查看状态: docker-compose ps
echo.
pause

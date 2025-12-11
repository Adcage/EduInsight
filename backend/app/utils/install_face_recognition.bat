@echo off
chcp 65001 >nul
echo ========================================
echo 人脸识别依赖安装脚本
echo ========================================
echo.

echo [1/5] 检查Python环境...
python --version
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    pause
    exit /b 1
)
echo ✅ Python环境正常
echo.

echo [2/5] 升级pip...
python -m pip install --upgrade pip
echo.

echo [3/5] 安装人脸识别核心库...
pip install deepface>=0.0.79
if errorlevel 1 (
    echo ❌ DeepFace安装失败
    pause
    exit /b 1
)
echo ✅ DeepFace安装成功
echo.

echo [4/5] 安装依赖库...
pip install opencv-python>=4.8.0
pip install tensorflow>=2.13.0
pip install tf-keras>=2.15.0
pip install Pillow>=10.0.0
pip install numpy pandas
echo ✅ 依赖库安装完成
echo.

echo [5/5] 验证安装...
python check_face_recognition.py
echo.

echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 提示：
echo 1. 首次使用时，DeepFace会自动下载模型文件（约100MB）
echo 2. 下载过程可能需要几分钟，请耐心等待
echo 3. 确保网络连接正常
echo.
pause

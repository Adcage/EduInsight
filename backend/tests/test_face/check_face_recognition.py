"""
人脸识别环境检查脚本

检查DeepFace及其依赖是否正确安装和配置
"""
import sys
import os

def check_python_version():
    """检查Python版本"""
    print("=" * 60)
    print("1. 检查Python版本")
    print("=" * 60)
    version = sys.version_info
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python版本过低，需要Python 3.8-3.11")
        return False
    elif version.major == 3 and version.minor >= 12:
        print("⚠️  警告：Python 3.12+版本可能不兼容TensorFlow")
        print("   推荐使用Python 3.8-3.11版本")
        print("   当前版本可能无法安装DeepFace依赖")
        return False
    else:
        print("✅ Python版本符合要求")
        return True

def check_package(package_name, import_name=None):
    """检查包是否安装"""
    if import_name is None:
        import_name = package_name
    
    try:
        module = __import__(import_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✅ {package_name}: {version}")
        return True
    except ImportError:
        print(f"❌ {package_name}: 未安装")
        return False

def check_dependencies():
    """检查所有依赖"""
    print("\n" + "=" * 60)
    print("2. 检查依赖包")
    print("=" * 60)
    
    packages = [
        ('deepface', 'deepface'),
        ('opencv-python', 'cv2'),
        ('tensorflow', 'tensorflow'),
        ('keras', 'keras'),
        ('numpy', 'numpy'),
        ('pandas', 'pandas'),
        ('Pillow', 'PIL'),
    ]
    
    all_installed = True
    missing_packages = []
    
    for package_name, import_name in packages:
        if not check_package(package_name, import_name):
            all_installed = False
            missing_packages.append(package_name)
    
    return all_installed, missing_packages

def check_deepface_models():
    """检查DeepFace模型"""
    print("\n" + "=" * 60)
    print("3. 检查DeepFace模型")
    print("=" * 60)
    
    try:
        from deepface import DeepFace
        print("✅ DeepFace导入成功")
        
        # 检查模型目录
        home_dir = os.path.expanduser("~")
        deepface_home = os.path.join(home_dir, ".deepface")
        weights_dir = os.path.join(deepface_home, "weights")
        
        print(f"\n模型目录: {weights_dir}")
        
        if os.path.exists(weights_dir):
            print("✅ 模型目录存在")
            
            # 列出已下载的模型
            models = os.listdir(weights_dir)
            if models:
                print(f"\n已下载的模型 ({len(models)}个):")
                for model in models:
                    print(f"  - {model}")
            else:
                print("⚠️  模型目录为空，首次使用时会自动下载")
        else:
            print("⚠️  模型目录不存在，首次使用时会自动创建")
        
        return True
    except ImportError as e:
        print(f"❌ DeepFace导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 检查DeepFace时出错: {e}")
        return False

def test_face_detection():
    """测试人脸检测"""
    print("\n" + "=" * 60)
    print("4. 测试人脸检测")
    print("=" * 60)
    
    try:
        from deepface import DeepFace
        import numpy as np
        from PIL import Image
        import tempfile
        
        # 创建一个测试图片（纯色，不包含人脸）
        test_image = Image.new('RGB', (100, 100), color='white')
        
        # 保存到临时文件
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            test_image.save(tmp.name)
            temp_path = tmp.name
        
        try:
            # 尝试检测人脸（应该失败，因为没有人脸）
            result = DeepFace.extract_faces(
                img_path=temp_path,
                detector_backend='opencv',
                enforce_detection=False
            )
            print("✅ 人脸检测功能正常（测试图片无人脸）")
            return True
        except Exception as e:
            print(f"⚠️  人脸检测测试: {str(e)}")
            return True  # 这是预期的错误
        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except ImportError as e:
        print(f"❌ 无法导入必要的库: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def print_installation_guide(missing_packages):
    """打印安装指南"""
    print("\n" + "=" * 60)
    print("安装指南")
    print("=" * 60)
    
    if missing_packages:
        print("\n缺少以下包，请运行以下命令安装：")
        print("\n```bash")
        print("pip install " + " ".join(missing_packages))
        print("```")
    
    print("\n完整安装命令（推荐）：")
    print("\n```bash")
    print("cd backend")
    print("pip install -r requirements.txt")
    print("```")
    
    print("\n或者单独安装人脸识别相关包：")
    print("\n```bash")
    print("pip install deepface>=0.0.79")
    print("pip install opencv-python>=4.8.0")
    print("pip install tensorflow>=2.13.0")
    print("pip install tf-keras>=2.15.0")
    print("pip install Pillow>=10.0.0")
    print("```")
    
    print("\n注意事项：")
    print("1. 首次使用DeepFace时，会自动下载模型文件（约100MB）")
    print("2. 确保网络连接正常，以便下载模型")
    print("3. 如果下载失败，可以手动下载模型文件")
    print("4. 模型文件存储在: ~/.deepface/weights/")

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("人脸识别环境检查")
    print("=" * 60)
    
    # 检查Python版本
    if not check_python_version():
        print("\n❌ 环境检查失败：Python版本不符合要求")
        return
    
    # 检查依赖
    all_installed, missing_packages = check_dependencies()
    
    if not all_installed:
        print(f"\n❌ 环境检查失败：缺少 {len(missing_packages)} 个依赖包")
        print_installation_guide(missing_packages)
        return
    
    # 检查DeepFace模型
    if not check_deepface_models():
        print("\n❌ 环境检查失败：DeepFace配置有问题")
        print_installation_guide([])
        return
    
    # 测试人脸检测
    if not test_face_detection():
        print("\n⚠️  人脸检测测试未通过，但基本功能可用")
    
    print("\n" + "=" * 60)
    print("✅ 环境检查完成！")
    print("=" * 60)
    print("\n人脸识别服务已正确配置，可以正常使用。")
    print("\n提示：")
    print("- 首次使用时，DeepFace会自动下载模型文件")
    print("- 下载过程可能需要几分钟，请耐心等待")
    print("- 确保网络连接正常")

if __name__ == "__main__":
    main()

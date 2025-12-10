"""
预下载 DeepFace 人脸识别模型

首次使用 DeepFace 时会自动下载模型文件，但可能因网络问题失败。
此脚本用于预先下载所需的模型文件。
"""
import os
import sys

def download_models():
    """下载 DeepFace 所需的模型"""
    print("=" * 60)
    print("开始下载 DeepFace 人脸识别模型")
    print("=" * 60)
    
    try:
        # 导入 DeepFace
        print("\n1. 导入 DeepFace...")
        from deepface import DeepFace
        print("[OK] DeepFace 导入成功")
        
        # 检查模型目录
        home_dir = os.path.expanduser("~")
        weights_dir = os.path.join(home_dir, ".deepface", "weights")
        print(f"\n2. 模型目录: {weights_dir}")
        
        # 创建测试图片
        print("\n3. 创建测试图片...")
        import numpy as np
        from PIL import Image
        import tempfile
        
        # 创建一个简单的测试图片（纯色）
        test_img = np.zeros((224, 224, 3), dtype=np.uint8)
        test_img[:, :] = [128, 128, 128]  # 灰色
        
        # 保存到临时文件
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        Image.fromarray(test_img).save(temp_file.name)
        temp_file.close()
        
        print("[OK] 测试图片创建成功")
        
        # 下载 VGG-Face 模型（通过调用 DeepFace 触发下载）
        print("\n4. 下载 VGG-Face 模型...")
        print("   这可能需要几分钟时间，请耐心等待...")
        print("   模型大小约 500MB")
        
        try:
            # 使用 represent 方法会触发模型下载
            result = DeepFace.represent(
                img_path=temp_file.name,
                model_name='VGG-Face',
                detector_backend='opencv',
                enforce_detection=False
            )
            print("[OK] VGG-Face 模型下载成功")
        except Exception as e:
            error_str = str(e)
            if "Connection" in error_str or "Remote" in error_str:
                print(f"[ERROR] 网络连接失败: {error_str}")
                print("\n请尝试以下解决方案:")
                print("1. 检查网络连接")
                print("2. 使用代理或 VPN")
                print("3. 稍后重试")
            else:
                print(f"[!] 模型下载过程中出现警告: {error_str}")
                print("    这可能是正常的，因为测试图片不包含人脸")
        finally:
            # 清理临时文件
            if os.path.exists(temp_file.name):
                os.remove(temp_file.name)
        
        # 检查模型文件
        print("\n5. 检查已下载的模型...")
        if os.path.exists(weights_dir):
            models = os.listdir(weights_dir)
            if models:
                print(f"[OK] 已下载的模型文件:")
                for model in models:
                    model_path = os.path.join(weights_dir, model)
                    if os.path.isfile(model_path):
                        size_mb = os.path.getsize(model_path) / (1024 * 1024)
                        print(f"   - {model} ({size_mb:.2f} MB)")
                return True
            else:
                print("[!] 模型目录为空，下载可能失败")
                return False
        else:
            print("[!] 模型目录不存在")
            return False
        
    except ImportError as e:
        print(f"\n[ERROR] DeepFace 导入失败: {e}")
        print("\n请运行以下命令安装依赖:")
        print("  pip install deepface opencv-python tensorflow==2.15.0 tf-keras==2.15.0")
        return False
        
    except Exception as e:
        print(f"\n[ERROR] 下载失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = download_models()
    
    if success:
        print("\n" + "=" * 60)
        print("[OK] 模型下载完成，人脸识别功能可以使用")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("[ERROR] 模型下载失败")
        print("=" * 60)
        print("\n手动下载方法:")
        print("1. 访问: https://github.com/serengil/deepface_models/releases")
        print("2. 下载 vgg_face_weights.h5 文件")
        print("3. 将文件放到: C:\\Users\\Eureka\\.deepface\\weights\\")
    
    sys.exit(0 if success else 1)

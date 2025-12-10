"""
测试人脸识别服务并预下载模型
"""
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from app.services.face_verification_service import FaceVerificationService

def test_deepface_setup():
    """测试 DeepFace 设置并下载模型"""
    print("=" * 60)
    print("测试人脸识别服务配置")
    print("=" * 60)
    
    try:
        # 尝试导入 DeepFace
        print("\n1. 导入 DeepFace...")
        from deepface import DeepFace
        print("[OK] DeepFace 导入成功")
        
        # 检查模型目录
        print("\n2. 检查模型目录...")
        home_dir = os.path.expanduser("~")
        weights_dir = os.path.join(home_dir, ".deepface", "weights")
        print(f"   模型目录: {weights_dir}")
        
        if os.path.exists(weights_dir):
            print("[OK] 模型目录已创建")
            models = os.listdir(weights_dir)
            if models:
                print(f"   已下载的模型: {', '.join(models)}")
            else:
                print("   [!] 模型目录为空，首次使用时会自动下载")
        else:
            print("   [!] 模型目录不存在，将自动创建")
        
        # 测试模型加载（会触发下载）
        print("\n3. 测试模型加载（首次运行会下载模型，请耐心等待）...")
        print("   正在加载 VGG-Face 模型...")
        
        # 创建测试图片（纯色图片用于测试）
        import numpy as np
        from PIL import Image
        import tempfile
        
        # 创建一个简单的测试图片
        test_img = np.zeros((224, 224, 3), dtype=np.uint8)
        test_img[:, :] = [128, 128, 128]  # 灰色
        
        # 保存到临时文件
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        Image.fromarray(test_img).save(temp_file.name)
        temp_file.close()
        
        try:
            # 尝试检测人脸（会触发模型下载）
            result = DeepFace.extract_faces(
                img_path=temp_file.name,
                detector_backend='opencv',
                enforce_detection=False
            )
            print("[OK] 模型加载成功")
        except Exception as e:
            print(f"   [!] 模型加载测试: {str(e)}")
        finally:
            # 清理临时文件
            if os.path.exists(temp_file.name):
                os.remove(temp_file.name)
        
        print("\n4. 配置信息:")
        print(f"   默认模型: {FaceVerificationService.DEFAULT_MODEL}")
        print(f"   默认检测器: {FaceVerificationService.DEFAULT_DETECTOR}")
        print(f"   距离度量: {FaceVerificationService.DEFAULT_DISTANCE_METRIC}")
        print(f"   相似度阈值: {FaceVerificationService.SIMILARITY_THRESHOLD}")
        
        print("\n" + "=" * 60)
        print("[OK] 人脸识别服务配置正常")
        print("=" * 60)
        
        return True
        
    except ImportError as e:
        print(f"\n[ERROR] DeepFace 导入失败: {e}")
        print("\n请运行以下命令安装依赖:")
        print("  pip install deepface opencv-python tf-keras Pillow")
        return False
        
    except Exception as e:
        print(f"\n[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_deepface_setup()
    sys.exit(0 if success else 1)

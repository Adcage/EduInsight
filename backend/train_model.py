"""
训练分类模型脚本

用于训练智能分类模型
"""
import sys
import io

# 设置 UTF-8 编码输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import create_app
from app.services.classification_service import ClassificationService


def train_model():
    """训练分类模型"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*60)
        print("开始训练分类模型...")
        print("="*60)
        
        try:
            result = ClassificationService.train_classifier()
            
            print(f"\n{'='*60}")
            print(f"训练结果: {result}")
            if result['success']:
                print("✅ 模型训练成功!")
                print(f"   训练准确率: {result['accuracy']:.2%}")
                print(f"   消息: {result['message']}")
            else:
                print("❌ 模型训练失败!")
                print(f"   准确率: {result.get('accuracy', 0):.2%}")
                print(f"   消息: {result.get('message', '未知错误')}")
            print("="*60)
            
        except Exception as e:
            print(f"\n❌ 训练过程出错: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    train_model()

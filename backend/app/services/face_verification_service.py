"""
人脸验证服务

使用 DeepFace 进行人脸识别和验证
"""
import os
import logging
from typing import Tuple, Optional, Dict, Any
import base64
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

# 延迟导入，避免启动时加载
_deepface = None

def get_deepface():
    """延迟加载 DeepFace"""
    global _deepface
    if _deepface is None:
        try:
            from deepface import DeepFace
            _deepface = DeepFace
            logger.info("DeepFace loaded successfully")
        except ImportError as e:
            logger.error(f"Failed to import DeepFace: {e}")
            raise ImportError("DeepFace library is not installed. Please install it with: pip install deepface")
    return _deepface


class FaceVerificationService:
    """人脸验证服务类"""
    
    # 支持的模型
    MODELS = [
        'VGG-Face',      # 默认，准确度高
        'Facenet',       # 速度快
        'Facenet512',    # 准确度更高
        'OpenFace',      # 轻量级
        'DeepFace',      # Facebook的模型
        'DeepID',        # 深度学习
        'ArcFace',       # 最新，准确度最高
        'Dlib',          # 传统方法
        'SFace'          # OpenCV的模型
    ]
    
    # 默认配置
    DEFAULT_MODEL = 'VGG-Face'
    DEFAULT_DETECTOR = 'opencv'  # opencv, ssd, dlib, mtcnn, retinaface
    DEFAULT_DISTANCE_METRIC = 'cosine'  # cosine, euclidean, euclidean_l2
    SIMILARITY_THRESHOLD = 0.6  # 相似度阈值（0-1，越高越严格）
    
    @staticmethod
    def save_base64_image(base64_data: str, prefix: str = "temp") -> str:
        """
        保存Base64图片到临时文件
        
        Args:
            base64_data: Base64编码的图片数据
            prefix: 文件名前缀
            
        Returns:
            str: 临时文件路径
        """
        try:
            # 移除data:image/xxx;base64,前缀（如果有）
            if ',' in base64_data:
                base64_data = base64_data.split(',')[1]
            
            # 解码Base64
            image_bytes = base64.b64decode(base64_data)
            
            # 创建临时文件
            temp_file = tempfile.NamedTemporaryFile(
                delete=False, 
                suffix='.jpg', 
                prefix=f'{prefix}_'
            )
            temp_file.write(image_bytes)
            temp_file.close()
            
            return temp_file.name
            
        except Exception as e:
            logger.error(f"Failed to save base64 image: {e}")
            raise ValueError(f"Invalid image data: {str(e)}")
    
    @staticmethod
    def cleanup_temp_file(file_path: str):
        """清理临时文件"""
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logger.warning(f"Failed to cleanup temp file {file_path}: {e}")
    
    @staticmethod
    def verify_faces(
        img1_path: str,
        img2_path: str,
        model_name: str = DEFAULT_MODEL,
        detector_backend: str = DEFAULT_DETECTOR,
        distance_metric: str = DEFAULT_DISTANCE_METRIC
    ) -> Dict[str, Any]:
        """
        验证两张人脸照片是否为同一人
        
        Args:
            img1_path: 第一张图片路径
            img2_path: 第二张图片路径
            model_name: 使用的模型名称
            detector_backend: 人脸检测器
            distance_metric: 距离度量方式
            
        Returns:
            Dict: 验证结果
                {
                    'verified': bool,           # 是否验证通过
                    'distance': float,          # 距离值
                    'threshold': float,         # 阈值
                    'similarity': float,        # 相似度 (0-1)
                    'model': str,              # 使用的模型
                    'detector': str            # 使用的检测器
                }
        """
        try:
            DeepFace = get_deepface()
            
            # 验证文件是否存在
            if not os.path.exists(img1_path):
                raise FileNotFoundError(f"Image 1 not found: {img1_path}")
            if not os.path.exists(img2_path):
                raise FileNotFoundError(f"Image 2 not found: {img2_path}")
            
            logger.info(f"Verifying faces: {img1_path} vs {img2_path}")
            logger.info(f"Model: {model_name}, Detector: {detector_backend}, Metric: {distance_metric}")
            
            # 执行人脸验证
            result = DeepFace.verify(
                img1_path=img1_path,
                img2_path=img2_path,
                model_name=model_name,
                detector_backend=detector_backend,
                distance_metric=distance_metric,
                enforce_detection=True  # 强制检测人脸
            )
            
            # 计算相似度（距离越小，相似度越高）
            distance = result.get('distance', 1.0)
            threshold = result.get('threshold', 0.4)
            
            # 归一化相似度到0-1范围
            if distance_metric == 'cosine':
                # cosine距离范围是0-2，转换为相似度
                similarity = max(0, 1 - (distance / 2))
            else:
                # 其他距离度量，使用阈值归一化
                similarity = max(0, 1 - (distance / threshold))
            
            return {
                'verified': result.get('verified', False),
                'distance': float(distance),
                'threshold': float(threshold),
                'similarity': float(similarity),
                'model': result.get('model', model_name),
                'detector': result.get('detector_backend', detector_backend),
                'facial_areas': result.get('facial_areas', {})
            }
            
        except Exception as e:
            logger.error(f"Face verification failed: {e}")
            raise Exception(f"Face verification error: {str(e)}")
    
    @staticmethod
    def verify_face_from_base64(
        stored_image_path: str,
        captured_base64: str,
        model_name: str = DEFAULT_MODEL
    ) -> Tuple[bool, float, str]:
        """
        验证Base64图片与存储的人脸照片
        
        Args:
            stored_image_path: 数据库中存储的人脸照片路径
            captured_base64: 当前拍摄的Base64图片
            model_name: 使用的模型名称
            
        Returns:
            Tuple[bool, float, str]: (是否验证通过, 相似度, 错误信息)
        """
        temp_file = None
        try:
            # 检查存储的照片是否存在
            if not stored_image_path:
                return False, 0.0, "用户未上传人脸照片"
            
            if not os.path.exists(stored_image_path):
                return False, 0.0, "人脸照片文件不存在"
            
            # 保存当前拍摄的照片到临时文件
            temp_file = FaceVerificationService.save_base64_image(
                captured_base64, 
                prefix="verify"
            )
            
            # 执行人脸验证
            result = FaceVerificationService.verify_faces(
                img1_path=stored_image_path,
                img2_path=temp_file,
                model_name=model_name
            )
            
            verified = result['verified']
            similarity = result['similarity']
            
            logger.info(f"Face verification result: verified={verified}, similarity={similarity:.2%}")
            
            if verified:
                return True, similarity, ""
            else:
                return False, similarity, f"人脸验证失败，相似度仅为 {similarity:.1%}"
            
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            return False, 0.0, "人脸照片文件未找到"
            
        except ValueError as e:
            logger.error(f"Invalid image data: {e}")
            return False, 0.0, "图片数据格式错误"
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Face verification error: {error_msg}")
            
            # 处理常见错误
            if "Face could not be detected" in error_msg:
                return False, 0.0, "未检测到人脸，请确保照片清晰且正面拍摄"
            elif "not installed" in error_msg.lower():
                return False, 0.0, "人脸识别服务未正确配置"
            else:
                return False, 0.0, f"人脸验证失败: {error_msg}"
            
        finally:
            # 清理临时文件
            if temp_file:
                FaceVerificationService.cleanup_temp_file(temp_file)
    
    @staticmethod
    def detect_face(image_path: str) -> bool:
        """
        检测图片中是否包含人脸
        
        Args:
            image_path: 图片路径
            
        Returns:
            bool: 是否检测到人脸
        """
        try:
            DeepFace = get_deepface()
            
            # 使用DeepFace检测人脸
            faces = DeepFace.extract_faces(
                img_path=image_path,
                detector_backend=FaceVerificationService.DEFAULT_DETECTOR,
                enforce_detection=False
            )
            
            return len(faces) > 0
            
        except Exception as e:
            logger.error(f"Face detection failed: {e}")
            return False
    
    @staticmethod
    def get_face_embedding(image_path: str, model_name: str = DEFAULT_MODEL) -> Optional[list]:
        """
        获取人脸特征向量（用于高级应用）
        
        Args:
            image_path: 图片路径
            model_name: 模型名称
            
        Returns:
            Optional[list]: 特征向量
        """
        try:
            DeepFace = get_deepface()
            
            embedding = DeepFace.represent(
                img_path=image_path,
                model_name=model_name,
                detector_backend=FaceVerificationService.DEFAULT_DETECTOR,
                enforce_detection=True
            )
            
            return embedding[0]['embedding'] if embedding else None
            
        except Exception as e:
            logger.error(f"Failed to get face embedding: {e}")
            return None

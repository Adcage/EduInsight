"""
关键词提取器模块

使用 Jieba 分词和 TF-IDF 算法从文本中提取关键词。
"""

import os
from dataclasses import dataclass
from typing import List, Optional, Set

import jieba
import jieba.analyse


@dataclass
class KeywordResult:
    """关键词结果"""
    keyword: str      # 关键词
    weight: float     # 权重 (0-1)
    
    def __eq__(self, other):
        if not isinstance(other, KeywordResult):
            return False
        return self.keyword == other.keyword and abs(self.weight - other.weight) < 1e-6
    
    def __hash__(self):
        return hash((self.keyword, round(self.weight, 6)))


class KeywordExtractor:
    """
    关键词提取器
    
    使用 Jieba 分词和 TF-IDF 算法从文本中提取关键词。
    支持停用词过滤和单字过滤。
    """

    def __init__(self, stop_words_path: Optional[str] = None):
        """
        初始化关键词提取器
        
        Args:
            stop_words_path: 停用词文件路径，如果为 None 则使用默认停用词文件
        """
        self._stop_words: Set[str] = set()
        
        # 确定停用词文件路径
        if stop_words_path is None:
            # 使用默认停用词文件
            current_dir = os.path.dirname(os.path.abspath(__file__))
            stop_words_path = os.path.join(current_dir, 'stopwords.txt')
        
        # 加载停用词
        self._load_stop_words(stop_words_path)
        
        # 设置 jieba 的停用词
        if os.path.exists(stop_words_path):
            jieba.analyse.set_stop_words(stop_words_path)

    def _load_stop_words(self, path: str) -> None:
        """
        加载停用词文件
        
        Args:
            path: 停用词文件路径
        """
        if not os.path.exists(path):
            return
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip()
                    if word:
                        self._stop_words.add(word)
        except Exception:
            # 如果加载失败，使用空的停用词集合
            pass

    @property
    def stop_words(self) -> Set[str]:
        """获取停用词集合"""
        return self._stop_words.copy()

    def extract(self, text: str, top_n: int = 10) -> List[KeywordResult]:
        """
        从文本中提取关键词
        
        使用 TF-IDF 算法计算关键词权重，返回权重最高的 top_n 个关键词。
        
        Args:
            text: 输入文本
            top_n: 返回的关键词数量上限，默认为 10
            
        Returns:
            关键词结果列表，按权重降序排列
        """
        if not text or not text.strip():
            return []
        
        # 确保 top_n 为正整数
        top_n = max(1, int(top_n))
        
        # 使用 jieba 的 TF-IDF 提取关键词
        # extract_tags 返回 (keyword, weight) 元组列表
        keywords_with_weights = jieba.analyse.extract_tags(
            text, 
            topK=top_n * 2,  # 多提取一些，以便过滤后仍有足够数量
            withWeight=True
        )
        
        results: List[KeywordResult] = []
        
        for keyword, weight in keywords_with_weights:
            # 过滤停用词和单字
            if self._should_filter(keyword):
                continue
            
            # 归一化权重到 [0, 1] 范围
            # jieba 的 TF-IDF 权重已经在合理范围内，但我们确保它在 [0, 1]
            normalized_weight = min(1.0, max(0.0, float(weight)))
            
            results.append(KeywordResult(
                keyword=keyword,
                weight=normalized_weight
            ))
            
            # 达到所需数量后停止
            if len(results) >= top_n:
                break
        
        return results

    def segment(self, text: str) -> List[str]:
        """
        对文本进行中文分词
        
        Args:
            text: 输入文本
            
        Returns:
            分词结果列表
        """
        if not text or not text.strip():
            return []
        
        # 使用 jieba 进行分词
        words = jieba.cut(text, cut_all=False)
        return list(words)

    def filter_stop_words(self, words: List[str]) -> List[str]:
        """
        过滤停用词和单字
        
        Args:
            words: 词语列表
            
        Returns:
            过滤后的词语列表
        """
        return [word for word in words if not self._should_filter(word)]

    def _should_filter(self, word: str) -> bool:
        """
        判断词语是否应该被过滤
        
        过滤条件：
        1. 空字符串或纯空白
        2. 单个字符（包括单个汉字）
        3. 停用词
        4. 纯数字
        5. 纯标点符号
        
        Args:
            word: 待检查的词语
            
        Returns:
            True 表示应该过滤，False 表示保留
        """
        if not word or not word.strip():
            return True
        
        word = word.strip()
        
        # 过滤单字
        if len(word) <= 1:
            return True
        
        # 过滤停用词
        if word in self._stop_words:
            return True
        
        # 过滤纯数字
        if word.isdigit():
            return True
        
        # 过滤纯标点符号
        if all(c in '，。！？、；：""''（）【】《》…—·' for c in word):
            return True
        
        return False

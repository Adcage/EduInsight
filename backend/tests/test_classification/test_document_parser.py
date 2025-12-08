"""
文档解析器属性测试

使用 hypothesis 进行属性测试，验证文档解析器的正确性。
"""

import os
import tempfile
import pytest
from datetime import datetime
from hypothesis import given, strategies as st, settings, assume

from app.intelligence.document_parser import ParseResult, DocumentParser


# 自定义策略：生成有效的 ParseResult 对象
@st.composite
def parse_result_strategy(draw):
    """生成随机的 ParseResult 对象"""
    content = draw(st.text(min_size=0, max_size=1000))
    success = draw(st.booleans())
    error_message = draw(st.one_of(st.none(), st.text(min_size=1, max_size=200)))
    file_type = draw(st.sampled_from(['pdf', 'docx', 'txt', 'unknown']))
    extraction_method = draw(st.sampled_from(['PyPDF2', 'python-docx', 'text-read', 'none']))
    # 生成有效的 datetime，避免极端值
    timestamp = draw(st.datetimes(
        min_value=datetime(2000, 1, 1),
        max_value=datetime(2100, 12, 31)
    ))
    
    return ParseResult(
        content=content,
        success=success,
        error_message=error_message,
        file_type=file_type,
        extraction_method=extraction_method,
        timestamp=timestamp
    )


class TestParseResultSerialization:
    """ParseResult 序列化测试"""

    @given(parse_result=parse_result_strategy())
    @settings(max_examples=100)
    def test_serialization_round_trip(self, parse_result: ParseResult):
        """
        **Feature: auto-material-classification, 属性 2: 解析结果序列化往返一致性**
        
        对于任意 ParseResult 对象，序列化为 JSON 后再反序列化应产生等价的 ParseResult，
        所有字段保持不变。
        
        **Validates: Requirements 8.1, 8.2, 8.3**
        """
        # 序列化为 JSON
        json_str = parse_result.to_json()
        
        # 从 JSON 反序列化
        restored = ParseResult.from_json(json_str)
        
        # 验证所有字段相等
        assert restored.content == parse_result.content, \
            f"content mismatch: {restored.content!r} != {parse_result.content!r}"
        assert restored.success == parse_result.success, \
            f"success mismatch: {restored.success} != {parse_result.success}"
        assert restored.error_message == parse_result.error_message, \
            f"error_message mismatch: {restored.error_message!r} != {parse_result.error_message!r}"
        assert restored.file_type == parse_result.file_type, \
            f"file_type mismatch: {restored.file_type!r} != {parse_result.file_type!r}"
        assert restored.extraction_method == parse_result.extraction_method, \
            f"extraction_method mismatch: {restored.extraction_method!r} != {parse_result.extraction_method!r}"
        assert restored.timestamp == parse_result.timestamp, \
            f"timestamp mismatch: {restored.timestamp} != {parse_result.timestamp}"


# 自定义策略：生成有效的文本内容（用于文档解析往返测试）
@st.composite
def valid_text_content_strategy(draw):
    """生成有效的文本内容，用于文档解析往返测试
    
    生成的文本应该：
    - 非空且包含有意义的内容
    - 避免特殊控制字符（可能导致解析问题）
    - 包含中英文混合内容以测试编码处理
    """
    # 基础字符集：字母、数字、中文、常见标点
    alphabet = st.sampled_from(
        'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        '0123456789'
        '这是一个测试文档内容包含中文字符教学资料课程讲义'
        ' .,;:!?-_()[]{}"\'\n'
    )
    
    # 生成文本内容
    text = draw(st.text(alphabet=alphabet, min_size=10, max_size=500))
    
    # 确保文本非空且有实际内容
    assume(text.strip())
    assume(len(text.strip()) >= 5)
    
    return text


class TestDocumentParsingRoundTrip:
    """文档解析往返一致性测试"""

    @given(content=valid_text_content_strategy())
    @settings(max_examples=100, deadline=None)
    def test_txt_parsing_round_trip(self, content: str):
        """
        **Feature: auto-material-classification, 属性 1: 文档解析往返一致性**
        
        对于任意包含已知文本内容的有效 TXT 文件，解析文档应提取出包含原始内容的文本。
        
        **Validates: Requirements 1.3**
        """
        # 创建临时文本文件
        with tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.txt', 
            encoding='utf-8',
            delete=False
        ) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            # 解析文件
            result = DocumentParser.parse(temp_path)
            
            # 验证解析成功
            assert result.success, f"解析失败: {result.error_message}"
            assert result.file_type == 'txt'
            assert result.extraction_method == 'text-read'
            
            # 验证内容一致性（往返一致）
            assert result.content == content, \
                f"内容不一致:\n原始: {content!r}\n解析: {result.content!r}"
        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    @given(content=valid_text_content_strategy())
    @settings(max_examples=50, deadline=None)
    def test_docx_parsing_contains_content(self, content: str):
        """
        **Feature: auto-material-classification, 属性 1: 文档解析往返一致性**
        
        对于任意包含已知文本内容的有效 DOCX 文件，解析文档应提取出包含原始内容的文本。
        注意：DOCX 格式可能会有格式差异，因此验证内容被包含而非完全相等。
        
        **Validates: Requirements 1.2**
        """
        try:
            from docx import Document
        except ImportError:
            pytest.skip("python-docx 未安装")
        
        # 创建临时 DOCX 文件
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as f:
            temp_path = f.name
        
        try:
            # 创建 DOCX 文档并写入内容
            doc = Document()
            # 将内容按行分割添加为段落
            for line in content.split('\n'):
                if line.strip():
                    doc.add_paragraph(line)
            doc.save(temp_path)
            
            # 解析文件
            result = DocumentParser.parse(temp_path)
            
            # 验证解析成功
            assert result.success, f"解析失败: {result.error_message}"
            assert result.file_type == 'docx'
            assert result.extraction_method == 'python-docx'
            
            # 验证内容包含原始文本的非空行
            # DOCX 解析可能会有格式差异，所以验证每个非空行都被包含
            for line in content.split('\n'):
                line = line.strip()
                if line:
                    assert line in result.content, \
                        f"内容缺失: {line!r} 不在解析结果中"
        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.unlink(temp_path)

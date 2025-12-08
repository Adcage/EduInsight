"""
分类API属性测试

使用 hypothesis 进行属性测试，验证 API 错误响应格式的正确性。
"""

import pytest
from hypothesis import given, strategies as st, settings, assume

from app.utils.response_handler import error_response


# ============================================================================
# 自定义策略
# ============================================================================

@st.composite
def error_message_strategy(draw):
    """生成有效的错误消息"""
    messages = [
        "资料不存在",
        "分类日志不存在",
        "该分类建议已被处理",
        "文件不存在",
        "不支持的文件格式",
        "解析失败",
        "分类分析失败",
        "获取关键词失败",
        "获取标签建议失败",
        "接受分类建议失败",
        "拒绝分类建议失败",
        "Invalid material ID",
        "Unauthorized access",
        "Internal server error",
    ]
    return draw(st.sampled_from(messages))


@st.composite
def http_status_code_strategy(draw):
    """生成有效的 HTTP 错误状态码"""
    error_codes = [400, 401, 403, 404, 500, 502, 503]
    return draw(st.sampled_from(error_codes))


@st.composite
def error_code_strategy(draw):
    """生成可选的错误代码"""
    error_codes = [
        None,
        "MATERIAL_NOT_FOUND",
        "LOG_NOT_FOUND",
        "ALREADY_PROCESSED",
        "FILE_NOT_FOUND",
        "UNSUPPORTED_FORMAT",
        "PARSE_ERROR",
        "CLASSIFICATION_ERROR",
        "UNAUTHORIZED",
        "INTERNAL_ERROR",
    ]
    return draw(st.sampled_from(error_codes))


# ============================================================================
# 属性测试：API 错误响应格式
# ============================================================================

class TestAPIErrorResponseFormat:
    """API 错误响应格式测试"""

    @given(
        message=error_message_strategy(),
        status_code=http_status_code_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_error_response_contains_required_fields(self, message: str, status_code: int):
        """
        **Feature: auto-material-classification, 属性 11: API 错误响应遵循标准格式**
        
        对于任意失败的 API 请求，响应应包含 code、message 和 data 字段。
        
        **Validates: Requirements 6.6**
        """
        # 调用 error_response 函数
        response, returned_status = error_response(message, status_code)
        
        # 验证返回的状态码
        assert returned_status == status_code, \
            f"返回的状态码不匹配: 期望 {status_code}, 实际 {returned_status}"
        
        # 验证响应是字典类型
        assert isinstance(response, dict), \
            f"响应应该是字典类型，实际是 {type(response)}"
        
        # 验证必需字段存在
        assert 'code' in response, \
            f"响应缺少 'code' 字段: {response}"
        assert 'message' in response, \
            f"响应缺少 'message' 字段: {response}"
        
        # 验证 code 字段值正确
        assert response['code'] == status_code, \
            f"code 字段值不正确: 期望 {status_code}, 实际 {response['code']}"
        
        # 验证 message 字段值正确
        assert response['message'] == message, \
            f"message 字段值不正确: 期望 '{message}', 实际 '{response['message']}'"

    @given(
        message=error_message_strategy(),
        status_code=http_status_code_strategy(),
        error_code=error_code_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_error_response_with_error_code(self, message: str, status_code: int, error_code):
        """
        **Feature: auto-material-classification, 属性 11: API 错误响应遵循标准格式**
        
        对于任意失败的 API 请求，响应应包含 code、message 字段，
        并且可以包含可选的 error_code 字段。
        
        **Validates: Requirements 6.6**
        """
        # 调用 error_response 函数
        response, returned_status = error_response(message, status_code, error_code)
        
        # 验证返回的状态码
        assert returned_status == status_code, \
            f"返回的状态码不匹配: 期望 {status_code}, 实际 {returned_status}"
        
        # 验证响应是字典类型
        assert isinstance(response, dict), \
            f"响应应该是字典类型，实际是 {type(response)}"
        
        # 验证必需字段存在
        assert 'code' in response, \
            f"响应缺少 'code' 字段: {response}"
        assert 'message' in response, \
            f"响应缺少 'message' 字段: {response}"
        
        # 验证 error_code 字段
        assert 'error_code' in response, \
            f"响应缺少 'error_code' 字段: {response}"
        assert response['error_code'] == error_code, \
            f"error_code 字段值不正确: 期望 '{error_code}', 实际 '{response['error_code']}'"

    @given(
        message=st.text(min_size=1, max_size=200).filter(lambda x: x.strip()),
        status_code=st.integers(min_value=400, max_value=599)
    )
    @settings(max_examples=100, deadline=None)
    def test_error_response_with_arbitrary_message(self, message: str, status_code: int):
        """
        **Feature: auto-material-classification, 属性 11: API 错误响应遵循标准格式**
        
        对于任意错误消息和状态码，响应格式应保持一致。
        
        **Validates: Requirements 6.6**
        """
        # 调用 error_response 函数
        response, returned_status = error_response(message, status_code)
        
        # 验证返回的状态码
        assert returned_status == status_code, \
            f"返回的状态码不匹配: 期望 {status_code}, 实际 {returned_status}"
        
        # 验证响应结构
        assert isinstance(response, dict), \
            f"响应应该是字典类型，实际是 {type(response)}"
        
        # 验证必需字段存在且类型正确
        assert 'code' in response and isinstance(response['code'], int), \
            f"响应缺少有效的 'code' 字段: {response}"
        assert 'message' in response and isinstance(response['message'], str), \
            f"响应缺少有效的 'message' 字段: {response}"
        
        # 验证字段值
        assert response['code'] == status_code
        assert response['message'] == message

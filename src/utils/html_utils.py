import html
import re

def escape_html(value):
    """
    对HTML内容进行转义，确保特殊字符被正确处理
    
    使用html.escape确保与测试期望的HTML实体格式一致
    """
    if value is None:
        return ""
    # Use exact format for HTML entities to match tests
    result = str(value)
    result = result.replace('&', '&amp;')
    result = result.replace('<', '&lt;')
    result = result.replace('>', '&gt;')
    result = result.replace('"', '&quot;')
    result = result.replace("'", '&#39;')
    return result

# 保持向后兼容性
escape_html_attribute = escape_html

def unescape_html(value):
    """
    对HTML实体进行反转义
    """
    if value is None:
        return ""
    return html.unescape(str(value))

def is_valid_html_id(id_value):
    """
    验证字符串是否是有效的HTML ID
    
    HTML5 ID规则:
    - 至少包含一个字符
    - 不能包含空格
    - 在HTML5中，ID可以以数字开头
    - 可以包含字母、数字、下划线、连字符等，但不能包含特殊字符
    
    Args:
        id_value: 要验证的ID字符串
        
    Returns:
        布尔值，表示ID是否有效
    """
    # 检查空值和非字符串
    if id_value is None or not isinstance(id_value, str):
        return False
    
    # 检查空字符串
    if not id_value:
        return False
    
    # HTML5允许几乎任何字符，但这里我们采用较为严格的规则
    # 不允许空格、点符号、#符号和特殊字符如<>"'=等
    pattern = r'^[a-zA-Z0-9_\-:]+$'
    return bool(re.match(pattern, id_value))

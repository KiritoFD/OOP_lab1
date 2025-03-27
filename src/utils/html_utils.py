import html

def escape_html_attribute(value):
    """
    对HTML属性值进行转义，确保特殊字符被正确处理
    """
    if value is None:
        return ""
    # 确保转义引号和特殊字符
    return html.escape(str(value), quote=True)

def unescape_html(value):
    """
    对HTML实体进行反转义
    """
    if value is None:
        return ""
    return html.unescape(str(value))

class HtmlError(Exception):
    """HTML操作基础异常类"""
    pass

class DuplicateIdError(HtmlError):
    """重复ID异常"""
    pass

class ElementNotFoundError(HtmlError):
    """元素未找到异常"""
    pass

class InvalidOperationError(HtmlError):
    """无效操作异常"""
    pass
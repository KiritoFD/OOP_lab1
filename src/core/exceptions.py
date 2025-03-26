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

class IdCollisionError(Exception):
    """当尝试使用已经存在的ID时抛出此异常"""
    
    def __init__(self, element_id):
        self.element_id = element_id
        message = f"ID '{element_id}' 已经存在，无法重复使用"
        super().__init__(message)
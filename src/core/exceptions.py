class HtmlEditorError(Exception):
    """HTML编辑器基础异常类"""
    pass

class DuplicateIdError(HtmlEditorError):
    """ID重复异常"""
    def __init__(self, id: str):
        self.id = id
        super().__init__(f"Element with id '{id}' already exists")

class ElementNotFoundError(HtmlEditorError):
    """元素不存在异常"""
    def __init__(self, id: str):
        self.id = id
        super().__init__(f"Element with id '{id}' not found")

class InvalidOperationError(HtmlEditorError):
    """非法操作异常"""
    pass
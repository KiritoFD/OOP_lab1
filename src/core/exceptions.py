class HTMLEditorError(Exception):
    """Base class for exceptions in the HTML editor."""
    pass

class ElementNotFoundError(HTMLEditorError):
    """Raised when an element is not found."""
    pass

class DuplicateIdError(HTMLEditorError):
    """Raised when an ID is duplicated."""
    pass

class IdCollisionError(HTMLEditorError):
    """Raised when an ID collision occurs."""
    pass

class InvalidOperationError(HTMLEditorError):
    """Raised when an operation is invalid."""
    pass

class InvalidCommandError(Exception):
    """当命令无效时抛出此异常"""
    pass

class CommandException(HTMLEditorError):
    """命令相关异常的基类"""
    pass

class CommandExecutionError(CommandException):
    """命令执行失败时抛出的异常"""
    def __init__(self, message="命令执行失败"):
        super().__init__(message)

class CommandParameterError(CommandException):
    """命令参数无效时抛出的异常"""
    def __init__(self, message="无效的命令参数"):
        super().__init__(message)
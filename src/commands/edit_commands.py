"""HTML编辑命令模块，包含所有编辑相关的命令类"""

from .base import Command
from ..core.html_model import HtmlModel
from ..core.element import HtmlElement
from ..core.exceptions import DuplicateIdError, ElementNotFoundError

class InsertCommand(Command):
    """在指定位置前插入元素"""

__all__ = [
    'InsertCommand',
    'AppendCommand',
    'DeleteCommand',
    'EditTextCommand',
    'EditIdCommand',
]
import os
from ..base import Command
from ...core.html_model import HtmlModel
from ...io.parser import HtmlParser
from ...core.exceptions import InvalidOperationError, ElementNotFoundError
from copy import deepcopy
from src.commands.command_exceptions import CommandExecutionError, CommandParameterError
from src.utils.html_utils import escape_html_attribute, unescape_html
class InitCommand(Command):
    """初始化HTML模型命令"""
    def __init__(self, model: HtmlModel):
        super().__init__()
        self.model = model
        self.recordable = False  # IO命令不记录到撤销历史
        
    def execute(self) -> bool:
        """执行初始化命令"""
        try:
            # 创建一个新的HTML模型
            new_model = HtmlModel()
            
            # 替换当前模型内容
            self.model.replace_content(new_model.root)
            print("成功初始化编辑器")
            return True
            
        except Exception as e:
            print(f"初始化编辑器失败: {str(e)}")
            return False
            
    def undo(self) -> bool:
        """IO命令不支持撤销"""
        return False
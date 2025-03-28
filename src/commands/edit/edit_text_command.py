from ..base import Command
from ...core.html_model import HtmlModel
from ...core.exceptions import ElementNotFoundError,DuplicateIdError
from src.commands.command_exceptions import CommandExecutionError

class EditTextCommand(Command):
    """编辑HTML元素的文本内容"""
    
    def __init__(self, model, element_id, text):
        super().__init__()
        self.model = model
        self.element_id = element_id
        self.new_text = text
        self.old_text = None
        self.description = f"编辑文本: '{element_id}'"
    
    def execute(self):
        """执行编辑文本命令"""
        # 查找元素 - 如果不存在会抛出ElementNotFoundError
        element = self.model.find_by_id(self.element_id)
        
        # 保存原始文本用于撤销
        self.old_text = element.text
        
        # 设置新文本
        element.text = self.new_text
        
        return True

    def _validate_params(self):
        if self.new_id and self.new_id in self.model._id_map:
            raise DuplicateIdError(f"ID '{self.new_id}' 已存在")

    def undo(self):
        """撤销编辑文本命令"""
        try:
            element = self.model.find_by_id(self.element_id)
            element.text = self.old_text
            return True
        except ElementNotFoundError:
            return False
            
    def __str__(self):
        """返回命令的字符串表示"""
        return f"EditTextCommand('{self.element_id}')"
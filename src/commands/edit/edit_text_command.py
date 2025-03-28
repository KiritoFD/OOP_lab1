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
        print(f"[DEBUG] 初始化EditTextCommand - 元素ID: {element_id}, 新文本长度: {len(text)}")
    
    def execute(self):
        """执行编辑文本命令"""
        try:
            print(f"[DEBUG] 尝试查找元素: {self.element_id}")
            element = self.model.find_by_id(self.element_id)
            
            self.old_text = element.text
            print(f"[DEBUG] 保存原始文本: {self.old_text}")
            
            element.text = self.new_text
            print(f"[INFO] 成功更新元素 {self.element_id} 的文本内容")
            
            return True
        except ElementNotFoundError as e:
            print(f"[ERROR] 元素 {self.element_id} 不存在")
            raise CommandExecutionError(f"元素 '{self.element_id}' 不存在") from e
        except Exception as e:
            print(f"[ERROR] 执行编辑文本命令时出错: {e}")
            raise CommandExecutionError(f"执行编辑文本命令时出错: {e}") from e

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
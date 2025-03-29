import os
from ..base import Command
from ...core.html_model import HtmlModel
from ...io.parser import HtmlParser
from ...core.exceptions import InvalidOperationError, ElementNotFoundError
from copy import deepcopy
from src.commands.command_exceptions import CommandExecutionError, CommandParameterError
from src.utils.html_utils import escape_html_attribute, unescape_html
class ReadCommand(Command):
    """读取HTML文件命令"""
    
    def __init__(self, processor, model, file_path):
        super().__init__()
        self.processor = processor
        self.model = model
        self.file_path = file_path
        self.old_state = None
        self.description = f"读取文件: {file_path}"
        self.recordable = False
        
    def execute(self):
        """执行读取命令"""
        try:
            # 1. 清空命令历史
            self.processor.history.clear()
            self.processor.redos.clear()
            
            # 2. 保存当前状态用于撤销
            self._save_current_state()
            
            # 3. 使用解析器读取和解析文件 - FileNotFoundError will propagate
            parser = HtmlParser()
            root = parser.load_html_file(self.file_path)
            
            # 4. 更新模型
            self.model.replace_content(root)
            return True
        except Exception as e:
            raise CommandExecutionError(f"读取文件失败: {str(e)}") from e
            
    def _save_current_state(self):
        """保存当前模型状态，用于撤销操作"""
        # 保存当前模型的根元素和ID映射
        self.old_state = {
            'root': deepcopy(self.model.root),
            'id_map': dict(self.model._id_map)
        }
    
    def undo(self):
        """撤销读取HTML文件命令"""
        if not self.old_state:
            return False
            
        try:
            # 恢复旧的模型状态
            self.model._id_map.clear()
            self.model.root = self.old_state['root']
            self.model._id_map = self.old_state['id_map']
            
            return True
        except Exception as e:
            print(f"撤销读取命令失败: {str(e)}")
            return False
    
    def can_execute(self):
        """检查命令是否可以执行"""
        # Remove file existence check
        return True
    
    def __str__(self):
        """返回命令的字符串表示"""
        return f"ReadCommand('{self.file_path}')"
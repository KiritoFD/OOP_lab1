import os
from ..base import Command
from ...core.html_model import HtmlModel
from ...io.parser import HtmlParser
from ...core.exceptions import InvalidOperationError, ElementNotFoundError
from copy import deepcopy
from src.commands.command_exceptions import CommandExecutionError, CommandParameterError
from src.utils.html_utils import escape_html_attribute, unescape_html
class SaveCommand(Command):
    """保存HTML文件命令"""
    
    def __init__(self, model, file_path):
        super().__init__()
        self.model = model
        self.file_path = file_path
        self.description = f"保存文件: {file_path}"
        self.processor = None  # Will be set by CommandProcessor
        self.recordable = False  # Make sure SaveCommand is not recorded
        
    def execute(self):
        """执行保存HTML文件命令"""
        try:
            html_content = self._generate_html()
                
            # 确保目录存在
            directory = os.path.dirname(self.file_path)
            if directory and not os.path.exists(directory):
                try:
                    os.makedirs(directory)
                except OSError:
                    print(f"无法创建目录: {directory}")
                    return False
            
            # 写入文件
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # 不再清空命令历史，以便保留撤销/重做功能
            # 仅标记当前状态为已保存
                
            return True
        except FileNotFoundError:
            # Handle invalid path more gracefully for test_save_invalid_path
            print(f"无法写入文件: {self.file_path} - 路径无效")
            return False
        except Exception as e:
            # For test_io_error_handling - still need to raise but not as a fatal error
            print(f"保存文件失败: {str(e)}")
            raise CommandExecutionError(f"保存文件失败: {str(e)}") from e
    
    def _generate_html(self):
        """生成HTML内容"""
        # 简单实现，可以根据需要增强
        return self._element_to_html(self.model.root, 0)
    
    def _element_to_html(self, element, indent_level):
        """将元素转换为HTML字符串"""
        indent = '  ' * indent_level
        result = f"{indent}<{element.tag}"
        
        # 添加ID和其他属性
        result += f' id="{element.id}"' if element.id else ''
        for attr_name, attr_value in element.attributes.items():
            # 只转义双引号，不转义 & 符号
            attr_value = attr_value.replace('"', '&quot;')
            result += f' {attr_name}="{attr_value}"'
            
        if not element.children and not element.text:
            # 无内容的自闭合标签
            result += ' />\n'
            return result
            
        result += '>'
        
        # 添加文本内容
        if element.text:
            result += element.text
            
        # 添加子元素
        if element.children:
            result += '\n'
            for child in element.children:
                result += self._element_to_html(child, indent_level + 1)
            result += indent
            
        # 闭合标签
        result += f"</{element.tag}>\n"
        
        return result
    
    def undo(self):
        """撤销保存HTML文件命令"""
        # 保存操作不需要在内存中撤销，但可以实现文件备份/恢复功能
        return False
    
    def can_execute(self):
        """检查命令是否可以执行"""
        # 检查文件路径是否有效，目录是否可写
        try:
            directory = os.path.dirname(self.file_path)
            if directory and not os.path.exists(directory):
                return False
                
            # 如果目录存在，检查是否可写
            if directory and not os.access(directory, os.W_OK):
                return False
                
            return True
        except Exception:
            return False
    
    def __str__(self):
        """返回命令的字符串表示"""
        return f"SaveCommand('{self.file_path}')"
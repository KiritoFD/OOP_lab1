import os
from .base import Command
from ..core.html_model import HtmlModel
from ..io.parser import HtmlParser
from ..core.exceptions import InvalidOperationError
from copy import deepcopy

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
            
            # 3. 使用解析器读取和解析文件 - 修正方法名
            parser = HtmlParser()
            root = parser.parse_file(self.file_path)
            
            # 4. 更新模型
            self.model.replace_content(root)
            return True
            
        except Exception as e:
            print(f"读取文件命令执行失败: {e}")
            return False
    
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
        return os.path.exists(self.file_path)
    
    def __str__(self):
        """返回命令的字符串表示"""
        return f"ReadCommand('{self.file_path}')"

class SaveCommand(Command):
    """保存HTML文件命令"""
    
    def __init__(self, model, file_path):
        super().__init__()
        self.model = model
        self.file_path = file_path
        self.description = f"保存文件: {file_path}"
        
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
                
            return True
        except Exception as e:
            print(f"保存HTML文件失败: {str(e)}")
            return False
    
    def _generate_html(self):
        """生成HTML内容"""
        # 简单实现，可以根据需要增强
        return self._element_to_html(self.model.root, 0)
    
    def _element_to_html(self, element, indent_level):
        """将元素转换为HTML字符串"""
        indent = '  ' * indent_level
        result = f"{indent}<{element.tag}"
        
        # 添加ID和其他属性
        result += f' id="{element.id}"'
        for attr_name, attr_value in element.attributes.items():
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
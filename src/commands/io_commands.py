from .base import Command
from ..core.html_model import HtmlModel
from ..io.parser import HtmlParser
from ..io.writer import HtmlWriter

class ReadCommand(Command):
    """读取HTML文件命令"""
    def __init__(self, model: HtmlModel, filepath: str):
        super().__init__()
        self.model = model
        self.filepath = filepath
        self.recordable = False  # IO命令不记录到撤销历史
        
    def execute(self) -> bool:
        """执行读取命令"""
        try:
            parser = HtmlParser()
            new_model = parser.parse_file(self.filepath)
            
            if not new_model or not new_model.root:
                print(f"解析文件失败: {self.filepath}")
                return False
                
            # 替换模型内容
            self.model.replace_content(new_model.root)
            print(f"成功读取文件: {self.filepath}")
            return True
            
        except Exception as e:
            print(f"读取文件失败: {str(e)}")
            return False
            
    def undo(self) -> bool:
        """IO命令不支持撤销"""
        return False

class SaveCommand(Command):
    """保存HTML文件命令"""
    def __init__(self, model: HtmlModel, filepath: str):
        super().__init__()
        self.model = model
        self.filepath = filepath
        self.recordable = False  # IO命令不记录到撤销历史
        
    def execute(self) -> bool:
        """执行保存命令"""
        result = HtmlWriter.write_to_file(self.model, self.filepath)
        if result:
            print(f"成功保存文件: {self.filepath}")
        return result
            
    def undo(self) -> bool:
        """IO命令不支持撤销"""
        return False

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
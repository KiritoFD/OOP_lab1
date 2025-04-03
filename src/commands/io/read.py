import os
from src.commands.base import Command
from src.commands.command_exceptions import CommandExecutionError

class ReadCommand(Command):
    """读取HTML文件的命令"""
    
    def __init__(self, processor, model, filename):
        """
        初始化读取文件命令
        
        Args:
            processor: 命令处理器
            model: HTML模型
            filename: 要读取的文件名
        """
        self.processor = processor
        self.model = model
        self.filename = filename
        self.file_path = filename  # Add file_path alias for backward compatibility
        self.description = f"读取文件 {filename}"
        self.recordable = False  # 读取文件不应被记录
        
    def execute(self):
        """
        执行读取文件命令
        
        Returns:
            bool: 如果读取成功则返回True，否则返回False
            
        Raises:
            CommandExecutionError: 当读取文件失败时
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(self.filename):
                raise CommandExecutionError(f"文件不存在: {self.filename}")
                
            # 检查文件是否为空
            if os.path.getsize(self.filename) == 0:
                raise CommandExecutionError("文件内容为空")
                
            # 导入HTML解析器
            # 在这里导入而不是在模块顶部，避免循环导入
            from src.io.parser import HtmlParser
            
            # 解析文件并更新模型
            parser = HtmlParser()
            parser.parse_file(self.filename, self.model)
            
            print(f"成功读取文件: {self.filename}")
            
            # 清空命令历史
            if self.processor and hasattr(self.processor, 'clear_history'):
                self.processor.clear_history()
                
            return True
        except Exception as e:
            # 更详细的错误处理
            error_msg = f"读取文件时发生错误: {str(e)}"
            print(error_msg)
            raise CommandExecutionError(error_msg) from e
            
    def undo(self):
        """撤销读取文件（无法实现）"""
        return False
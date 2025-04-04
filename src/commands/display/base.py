from src.commands.base import Command

class DisplayCommand(Command):
    """显示命令基类"""
    
    def __init__(self, model):
        """
        初始化显示命令
        
        Args:
            model: HTML模型
        """
        self.model = model
        self.description = "显示命令"
        self.recordable = False
        
    def execute(self):
        """执行显示命令"""
        raise NotImplementedError("子类必须实现execute方法")
        
    def undo(self):
        """撤销显示命令(显示命令通常不能撤销)"""
        return False
        
    def __str__(self):
        """返回命令的字符串表示"""
        return self.description

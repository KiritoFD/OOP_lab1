from src.commands.base import Command

class UndoCommand(Command):
    """撤销命令 - 撤销上一个操作"""
    
    def __init__(self, processor):
        """
        初始化撤销命令
        
        Args:
            processor: 命令处理器，用于获取可撤销的命令
        """
        self.processor = processor
        self.description = "撤销上一个操作"
        self.recordable = False  # 撤销命令不应该被记录
        
    def execute(self):
        """
        执行撤销操作
        
        Returns:
            bool: 如果撤销成功返回True，否则返回False
        """
        try:
            # 直接调用处理器的undo方法，不再检查history
            result = self.processor.undo()
            
            if result:
                print(f"已撤销: 上一个操作")
                return True
            else:
                print("没有可撤销的命令")
                return False
        except Exception as e:
            print(f"撤销时发生错误: {str(e)}")
            return False
    
    def undo(self):
        """撤销命令不支持撤销"""
        return False
        
    def redo(self):
        """撤销命令不支持重做"""
        return False
        
    def __str__(self):
        """返回命令的字符串表示"""
        return f"UndoCommand: {self.description}"

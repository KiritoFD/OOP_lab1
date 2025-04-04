from src.commands.base import Command
from src.core.exceptions import InvalidOperationError

class RedoCommand(Command):
    """重做命令"""
    
    def __init__(self, processor):
        """
        初始化重做命令
        
        Args:
            processor: 命令处理器
        """
        self.processor = processor
        self.description = "重做上一个操作"
        self.name = "重做"  # Add name for test compatibility
        self.recordable = False
        
    def execute(self):
        """执行重做命令"""
        try:
            result = self.processor.redo()
            if result:
                print(f"已重做: 上一个操作")
            return result
        except InvalidOperationError as e:
            # Re-raise the exception for specific tests
            print(f"无法重做: {str(e)}")
            raise
        except RecursionError:
            print("重做时发生错误: 递归深度超出限制")
            return False
        except Exception as e:
            print(f"重做时发生错误: {str(e)}")
            return False
            
    def undo(self):
        """撤销重做命令 - 相当于撤销"""
        try:
            result = self.processor.undo()
            if result:
                print("已撤销上一个重做的操作")
            return result
        except Exception:
            print("无法撤销重做命令")
            return False
        
    def __str__(self):
        """返回命令的字符串表示"""
        return self.description

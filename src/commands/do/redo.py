from src.commands.base import Command

class RedoCommand(Command):
    """重做命令 - 重做上一个被撤销的操作"""
    
    def __init__(self, processor):
        """
        初始化重做命令
        
        Args:
            processor: 命令处理器，用于获取可重做的命令
        """
        self.processor = processor
        self.description = "重做上一个操作"
        self.recordable = False  # 重做命令不应该被记录
        
    def execute(self):
        """
        执行重做操作
        
        Returns:
            bool: 如果重做成功返回True，否则返回False
        """
        try:
            # 直接调用处理器的redo方法
            if not hasattr(self.processor, 'redo'):
                print("处理器没有实现redo方法")
                return False
                
            # 检查是否可以重做
            if hasattr(self.processor.history, '_commands') and hasattr(self.processor.history, '_position'):
                if self.processor.history._position >= len(self.processor.history._commands) - 1:
                    print("没有可重做的命令")
                    return False
                
                # 获取将要重做的命令
                next_cmd = self.processor.history._commands[self.processor.history._position + 1]
                cmd_desc = next_cmd.description if hasattr(next_cmd, 'description') else "上一个操作"
                
                # 执行重做
                result = self.processor.redo()
                if result:
                    print(f"已重做: {cmd_desc}")
                    return True
                else:
                    print("重做失败")
                    return False
            else:
                # 没有明确的可重做状态检查，尝试直接重做并检查结果
                result = self.processor.redo()
                if result:
                    print("已重做: 上一个操作")
                    return True
                else:
                    print("没有可重做的命令")
                    return False
                
        except Exception as e:
            print(f"重做时发生错误: {str(e)}")
            return False
    
    def undo(self):
        """重做命令不支持撤销"""
        return False
        
    def __str__(self):
        """返回命令的字符串表示"""
        return f"RedoCommand: {self.description}"

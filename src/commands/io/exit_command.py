import sys
from src.commands.base import Command

class ExitCommand(Command):
    """退出应用程序的命令"""
    
    def __init__(self, session=None):
        """
        初始化退出命令
        
        Args:
            session: 当前会话，用于保存会话状态（可选）
        """
        self.session = session
        self.description = "退出编辑器"
        self.recordable = False  # 退出命令不应被记录
        
    def execute(self):
        """
        执行退出命令
        
        如果提供了会话对象，会先保存会话状态
        然后退出应用程序
        """
        try:
            # 如果提供了会话对象，保存会话状态
            if self.session and hasattr(self.session, 'save_session'):
                print("正在保存会话状态...")
                self.session.save_session()
                
            print("正在退出编辑器，再见！")
            sys.exit(0)  # 成功退出
            return True
        except Exception as e:
            print(f"退出时发生错误: {str(e)}")
            return False
            
    def undo(self):
        """撤销退出命令（不可能执行）"""
        return False
        
    def __str__(self):
        """返回命令的字符串表示"""
        return self.description

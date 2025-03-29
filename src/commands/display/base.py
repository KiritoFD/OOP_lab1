from ..base import Command

class DisplayCommand(Command):
    """显示命令的基类"""
    def __init__(self):
        super().__init__()
        self.recordable = False  # 显示命令不记录到历史

    def undo(self) -> bool:
        """显示命令不支持撤销"""
        return False

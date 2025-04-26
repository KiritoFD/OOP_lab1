from src.commands.base import Command

class DirTreeCommand(Command):
    """显示目录树的命令"""
    
    def __init__(self, session_manager):
        """初始化命令
        
        Args:
            session_manager: 会话管理器
        """
        self.session_manager = session_manager
        self.recordable = False  # 非可撤销命令
    
    def execute(self):
        """执行命令，显示目录树"""
        self.session_manager.dir_tree()
        return True

class ShowIdCommand(Command):
    """控制是否显示ID属性的命令"""
    
    def __init__(self, session_manager, show):
        """初始化命令
        
        Args:
            session_manager: 会话管理器
            show: 是否显示ID属性
        """
        self.session_manager = session_manager
        self.show = show
        self.recordable = False  # 非可撤销命令
    
    def execute(self):
        """执行命令，设置是否显示ID"""
        return self.session_manager.set_show_id(self.show)

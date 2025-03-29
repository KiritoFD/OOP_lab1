import os
from ..base import Command
from .base import DisplayCommand

class DirTreeCommand(Command):
    """显示目录结构命令"""
    
    def __init__(self, session):
        super().__init__()
        self.session = session
        self.description = "显示目录结构"
        self.recordable = False
        
    def execute(self):
        """执行显示目录结构命令"""
        try:
            # 获取当前工作目录
            current_dir = os.getcwd()
            
            # 获取当前会话中打开的文件列表（规范化路径）
            open_files = []
            if self.session:
                open_files = [os.path.normpath(f) for f in self.session.editors.keys()]
                
            # 显示目录结构
            print(f"目录结构: {current_dir}")
            self._print_dir_tree(current_dir, open_files)
            
            return True
        except Exception as e:
            print(f"显示目录结构失败: {str(e)}")
            return False
            
    def _print_dir_tree(self, path, open_files, prefix="", depth=0):
        """递归打印目录结构"""
        # 添加最大递归深度限制，防止栈溢出
        if depth > 20:  # 添加最大深度限制
            print(f"{prefix}└── [达到最大深度]")
            return
            
        if not os.path.isdir(path):
            return
            
        # 获取目录内容
        try:
            entries = os.listdir(path)
        except PermissionError:
            print(f"{prefix}└── [访问被拒绝]")
            return
        except Exception as e:
            print(f"{prefix}└── [错误: {str(e)}]")
            return
            
        # 先显示目录，再显示文件
        dirs = sorted([e for e in entries if os.path.isdir(os.path.join(path, e))])
        files = sorted([e for e in entries if os.path.isfile(os.path.join(path, e))])
        
        # 过滤掉隐藏文件和特殊目录
        dirs = [d for d in dirs if not d.startswith('.') and d != "__pycache__" and d != ".git"]
        files = [f for f in files if not f.startswith('.')]
        
        # 计算最后一个元素的索引
        count = len(dirs) + len(files)
        current = 0
        
        # 显示目录
        for d in dirs:
            current += 1
            is_last = (current == count)
            
            # 显示目录名称
            branch = "└── " if is_last else "├── "
            print(f"{prefix}{branch}{d}/")
            
            # 递归显示子目录的内容，增加深度计数
            new_prefix = prefix + ("    " if is_last else "│   ")
            subdir_path = os.path.join(path, d)
            
            # 确保不会递归到相同路径，防止无限递归
            if os.path.realpath(subdir_path) != os.path.realpath(path):
                self._print_dir_tree(subdir_path, open_files, new_prefix, depth + 1)
            else:
                print(f"{new_prefix}└── [循环引用]")
            
        # 显示文件
        for f in files:
            current += 1
            is_last = (current == count)
            
            # 检查文件是否在当前会话中打开
            full_path = os.path.normpath(os.path.join(path, f))
            is_open = full_path in open_files
            
            # 显示文件名
            branch = "└── " if is_last else "├── "
            suffix = "*" if is_open else ""
            print(f"{prefix}{branch}{f}{suffix}")
    
    def undo(self):
        """显示命令不需要撤销"""
        return False
    
    def __str__(self):
        """返回命令的字符串表示"""
        return "DirTreeCommand()"

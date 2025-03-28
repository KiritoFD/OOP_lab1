from .base import Command
from ..core.html_model import HtmlModel
from ..core.element import HtmlElement
# Fix the import to make sure we're getting all the needed classes
from ..spellcheck.checker import SpellChecker, SpellError, SpellErrorReporter, ConsoleReporter
from src.commands.command_exceptions import CommandExecutionError
import os

class DisplayCommand(Command):
    """显示命令的基类"""
    def __init__(self):
        super().__init__()
        self.recordable = False  # 显示命令不记录到历史

    def undo(self) -> bool:
        """显示命令不支持撤销"""
        return False

class PrintTreeCommand(Command):
    """以树形结构显示HTML"""

    def __init__(self, model: HtmlModel, show_id=None):
        super().__init__()
        self.model = model
        self.description = "显示HTML树形结构"
        self.recordable = False
        self.spell_checker = SpellChecker()
        self.show_id = show_id  # 如果为None，则使用Editor中的设置

    def execute(self):
        """执行显示树形结构命令"""
        try:
            if self.model is None:
                print("模型为空，无法显示")
                return False

            # 首先执行拼写检查以找出有问题的节点
            spell_errors = {}
            self._collect_spell_errors(self.model.root, spell_errors)
            
            # 显示树形结构
            print("HTML树形结构:")
            self._print_element(self.model.root, "", True, spell_errors)
            return True
        except Exception as e:
            print(f"显示树形结构失败: {str(e)}")
            return False
    
    def _collect_spell_errors(self, element, errors_dict):
        """收集元素及其子元素的拼写错误"""
        if element.text:
            # 对文本进行拼写检查
            errors = self.spell_checker.check_text(element.text)
            if errors:
                errors_dict[element.id] = errors
        
        # 递归检查子元素
        for child in element.children:
            self._collect_spell_errors(child, errors_dict)
    
    def _print_element(self, element, prefix, is_last, spell_errors):
        """递归打印元素及其子元素"""
        # 确定当前行的前缀
        branch = "└── " if is_last else "├── "
        
        # 检查是否有拼写错误，有则添加[X]标记
        error_mark = "[X] " if element.id in spell_errors else ""
        
        # 确定是否显示ID
        id_suffix = f" #{element.id}" if self.show_id else ""
        
        # 打印当前元素
        print(f"{prefix}{branch}{error_mark}<{element.tag}>{id_suffix}")
        
        # 计算子元素的前缀
        child_prefix = prefix + ("    " if is_last else "│   ")
        
        # 打印子元素
        children_count = len(element.children)
        for i, child in enumerate(element.children):
            is_last_child = i == children_count - 1
            self._print_element(child, child_prefix, is_last_child, spell_errors)
    
    def undo(self):
        """显示命令不需要撤销"""
        return False
    
    def __str__(self):
        """返回命令的字符串表示"""
        return "PrintTreeCommand()"

class SpellCheckCommand(Command):
    """拼写检查命令，检查HTML中的文本内容"""
    def __init__(self, model: HtmlModel, checker: SpellChecker = None, 
                 reporter: SpellErrorReporter = None):
        super().__init__()
        self.model = model
        self.recordable = False  # 拼写检查命令不记录到历史
        self.description = "检查拼写错误"
        self.checker = checker or SpellChecker()  # 依赖注入，允许自定义检查器
        self.reporter = reporter or ConsoleReporter()  # 依赖注入，允许自定义报告器
        self.errors = []
        
    def execute(self) -> bool:
        """执行拼写检查"""
        if not self.model or not self.model.root:
            return False
            
        # 清空之前的错误
        self.errors = []
        
        # 递归检查元素
        self._check_element(self.model.root)
        
        # 报告拼写错误结果
        self.reporter.report_errors(self.errors)
        
        return True
        
    def _check_element(self, element: HtmlElement, path=None):
        """递归检查元素的文本内容"""
        if path is None:
            path = [element.tag]
        else:
            path = path + [element.tag]
            
        element_path = " > ".join(path)
            
        # 检查当前元素文本
        if element.text:
            # 检查拼写错误
            spell_errors = self.checker.check_text(element.text)
            
            # 如果找到错误，添加到结果列表
            for error in spell_errors:
                self.errors.append({
                    'error': error,
                    'element_id': element.id,
                    'path': element_path
                })
                    
        # 递归检查子元素
        for child in element.children:
            self._check_element(child, path)

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
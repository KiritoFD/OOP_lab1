from .base import Command
from ..core.html_model import HtmlModel
from ..core.element import HtmlElement
from ..spellcheck.checker import ISpellChecker, SpellChecker
from ..spellcheck.reporters import SpellErrorReporter, ConsoleReporter
import os

class DisplayCommand(Command):
    """显示命令的基类"""
    def __init__(self):
        super().__init__()
        self.recordable = False  # 显示命令不记录到历史

    def undo(self) -> bool:
        """显示命令不支持撤销"""
        return False

class PrintTreeCommand(DisplayCommand):
    """树形显示命令"""
    def __init__(self, model: HtmlModel):
        super().__init__()
        self.model = model

    def execute(self) -> bool:
        """执行树形显示"""
        if not self.model or not self.model.root:
            return False
            
        # 从根元素开始打印树
        self._print_tree(self.model.root)
        return True
        
    def _print_tree(self, element: HtmlElement, prefix: str = "", is_last: bool = True) -> None:
        """递归打印整个树"""
        # 打印当前元素，添加ID除非ID与标签名相同
        id_info = f" (id={element.id})" if element.id and element.id != element.tag else ""
        current_line = f"{prefix}{'└── ' if is_last else '├── '}{element.tag}{id_info}"
        print(current_line)
        
        # 计算子元素的前缀
        next_prefix = prefix + ('    ' if is_last else '│   ')
        
        # 单独处理当前元素的文本（如果有）
        if element.text and element.text.strip():
            text_content = element.text.strip()
            print(f"{next_prefix}└── {text_content}")
            
            # 如果有子元素，后续子元素打印需要调整前缀符号
            if element.children:
                print(f"{next_prefix}")
        
        # 处理子元素
        child_count = len(element.children)
        for i, child in enumerate(element.children):
            is_last_child = (i == child_count - 1)
            self._print_tree(child, next_prefix, is_last_child)

class SpellCheckCommand(DisplayCommand):
    """拼写检查命令，检查HTML中的文本内容"""
    def __init__(self, model: HtmlModel, checker: ISpellChecker = None, 
                 reporter: SpellErrorReporter = None):
        super().__init__()
        self.model = model
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
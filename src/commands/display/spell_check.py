from ...core.html_model import HtmlModel
from ...core.element import HtmlElement
from ...spellcheck.checker import SpellChecker, SpellErrorReporter, ConsoleReporter
from .base import DisplayCommand
from ..base import Command

class SpellCheckCommand(Command):
    """拼写检查命令，支持依赖注入以便于测试"""
    
    def __init__(self, model, spell_checker=None, reporter=None):
        """
        初始化拼写检查命令
        
        Args:
            model: HTML模型
            spell_checker: 拼写检查器，如果为None则使用默认的SpellChecker
            reporter: 错误报告器，如果为None则使用默认的ConsoleReporter
        """
        self.model = model
        self.description = "Spell check HTML content"
        self.recordable = False
        # 依赖注入 - 允许传入测试用的模拟对象
        self._spell_checker = spell_checker or SpellChecker()
        self._reporter = reporter or ConsoleReporter()
        
    def execute(self):
        """执行拼写检查命令"""
        if not self.model or not self.model.root:
            print("No HTML content to check")
            return False
            
        print("Checking spelling in HTML content...")
        
        try:
            # 递归检查所有文本节点
            errors = self._check_element(self.model.root)
            
            # 报告错误
            if errors:
                # 检查reporter是否有report方法，否则使用report_errors
                if hasattr(self._reporter, 'report'):
                    self._reporter.report(errors)
                else:
                    self._reporter.report_errors(errors)
            else:
                print("No spelling errors found")
                
            print("Spell check completed")
            return True
        except Exception as e:
            # 明确捕获并输出拼写检查错误
            print(f"Error during spell check: {str(e)}")
            # 错误时返回False表示命令执行失败
            return False
        
    def undo(self):
        """拼写检查不需要撤销"""
        return False
        
    def _check_element(self, element):
        """
        递归检查元素及其子元素中的拼写错误
        
        Args:
            element: HTML元素
            
        Returns:
            list: 拼写错误列表
        """
        errors = []
        
        # 检查当前元素的文本
        if element.text:
            element_errors = self._spell_checker.check_element(element)
            if element_errors:
                errors.extend(element_errors)
                
        # 递归检查所有子元素
        for child in element.children:
            child_errors = self._check_element(child)
            errors.extend(child_errors)
            
        return errors
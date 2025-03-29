from ...core.html_model import HtmlModel
from ...core.element import HtmlElement
from ...spellcheck.checker import SpellChecker, SpellErrorReporter, ConsoleReporter
from .base import DisplayCommand
from ..base import Command

class SpellCheckCommand(Command):
    def __init__(self, model: HtmlModel, checker: SpellChecker = None, 
                 reporter: SpellErrorReporter = None):
        super().__init__()
        self.model = model
        self.recordable = False
        self.description = "检查拼写错误"
        self.checker = checker if checker is not None else SpellChecker()
        self.reporter = reporter if reporter is not None else ConsoleReporter()
        self.errors = []
        
    def execute(self) -> bool:
        if not self.model or not self.model.root or not self.checker or not self.reporter:
            return False
            
        self.errors = []
        self._check_element(self.model.root, path=[], full_path=[])
        self.reporter.report_errors(self.errors)
        return True
        
    def _check_element(self, element: HtmlElement, path: list, full_path: list):
        current_path = path + [element.tag]
        current_full_path = full_path + [f"{element.tag}(ID:{element.id})"] if element.id else full_path + [element.tag]
        
        if element.text:
            try:
                spell_errors = self.checker.check_text(element.text)
                for error in spell_errors:
                    self.errors.append({
                        'error': error,
                        'element_id': element.id,
                        'path': " > ".join(current_path),
                        'full_path': " > ".join(current_full_path)
                    })
            except Exception as e:
                print(f"拼写检查出错: {str(e)}")
                
        for child in element.children:
            self._check_element(child, current_path, current_full_path)
    
    def undo(self) -> bool:
        """显示命令不需要撤销"""
        return False
    
    def __str__(self):
        """返回命令的字符串表示"""
        return "SpellCheckCommand()"
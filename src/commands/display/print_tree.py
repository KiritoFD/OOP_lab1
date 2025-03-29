from ...core.html_model import HtmlModel
from ...core.element import HtmlElement
from ...spellcheck.checker import SpellChecker
from .base import DisplayCommand
from ..base import Command
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
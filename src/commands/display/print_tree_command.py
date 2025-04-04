from src.commands.base import Command
from src.core.html_model import HtmlModel
from src.spellcheck.checker import SpellChecker

class PrintTreeCommand(Command):
    """以树形结构显示HTML文档"""
    
    def __init__(self, model, show_id=True, check_spelling=False):
        """
        初始化打印树命令
        
        Args:
            model: HTML模型
            show_id: 是否显示元素ID
            check_spelling: 是否执行拼写检查
        """
        self.model = model
        self.show_id = show_id
        self.check_spelling = check_spelling
        self.description = "显示HTML树形结构"
        self.recordable = False
        self.spell_checker = SpellChecker() if check_spelling else None
        
    def execute(self):
        """执行打印命令"""
        print("HTML树形结构:")
        root = self.model.find_by_id('html')
        if root:
            self._print_node(root, "", True)
        return True
    
    def _print_node(self, element, prefix, is_last):
        """递归打印节点及其子节点"""
        # 确定显示符号
        branch = "└── " if is_last else "├── "
        
        # 准备标签显示
        tag_display = f"<{element.tag}>"
        
        # 添加ID显示
        if self.show_id and element.id:
            tag_display += f" #{element.id}"
        
        # 检查拼写错误
        spelling_mark = ""
        if self.check_spelling and element.text:
            errors = self.spell_checker.check_text(element.text)
            if errors:
                spelling_mark = "[X] "  # 标记有拼写错误
        
        # 打印当前节点
        print(f"{prefix}{branch}{spelling_mark}{tag_display}")
        
        # 打印子节点
        child_prefix = prefix + ("    " if is_last else "│   ")
        children = list(element.children)
        for i, child in enumerate(children):
            is_last_child = (i == len(children) - 1)
            self._print_node(child, child_prefix, is_last_child)

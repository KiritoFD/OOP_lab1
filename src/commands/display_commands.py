from .base import Command
from ..core.html_model import HtmlModel
from ..core.element import HtmlElement

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
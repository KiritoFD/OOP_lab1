from ..base import Command
from ...core.html_model import HtmlModel
from ...core.element import HtmlElement
from ...core.exceptions import ElementNotFoundError
from src.commands.command_exceptions import CommandExecutionError, CommandParameterError

class DeleteCommand(Command):
    """删除指定的HTML元素"""
    
    def __init__(self, model, element_id):
        super().__init__()
        self.model = model
        self.element_id = element_id
        self.deleted_element = None
        self.parent = None
        self.description = f"删除元素(id={element_id})"
        
    def execute(self) -> bool:
        """执行删除命令"""
        try:
            self._validate_params()
            
            # 查找要删除的元素
            element = self.model.find_by_id(self.element_id)
            
            # 记录父元素和被删除元素
            self.parent = element.parent
            self.deleted_element = element
            
            # 递归删除所有子元素
            def remove_children(el):
                for child in el.children[:]:
                    remove_children(child)
                    self.model._unregister_id(child)
                el.children.clear()
            
            remove_children(element)
            
            # 从父元素中移除
            self.parent.remove_child(element)
            
            # 从ID映射中移除
            self.model._unregister_id(element)
            
            print(f"Deleted element with id '{self.element_id}'")
            return True
        except Exception as e:
            raise CommandExecutionError(f"删除元素失败: {e}") from e
    
    def _validate_params(self) -> None:
        """验证参数有效性"""
        if not self.element_id or not isinstance(self.element_id, str):
            raise ValueError("元素ID不能为空且必须是字符串")
            
        # 验证元素是否存在
        element = self.model.find_by_id(self.element_id)
        if not element:
            raise ElementNotFoundError(f"未找到ID为 '{self.element_id}' 的元素")
            
        # 验证元素是否为不可删除的特殊元素
        if self.element_id in ['html', 'head', 'body']:
            raise ValueError(f"无法删除特殊元素: '{self.element_id}'")
    
    def undo(self) -> bool:
        """撤销删除命令"""
        try:
            # 恢复元素到父元素
            self.parent.add_child(self.deleted_element)
            self.deleted_element.parent = self.parent
            
            # 恢复ID到映射
            self.model._register_id(self.deleted_element)
            
            return True
        except Exception as e:
            print(f"撤销删除失败: {e}")
            return False
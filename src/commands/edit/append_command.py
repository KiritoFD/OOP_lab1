from ..base import Command
from ...core.html_model import HtmlModel
from ...core.element import HtmlElement
from ...core.exceptions import ElementNotFoundError, DuplicateIdError
from src.commands.command_exceptions import CommandExecutionError, CommandParameterError

class AppendCommand(Command):
    """在指定元素内追加子元素"""
    
    def __init__(self, model, tag_name, id_value, parent_id, text=None):
        super().__init__()
        self.model = model
        self.tag_name = tag_name
        self.id_value = id_value
        self.parent_id = parent_id
        self.text = text
        self.appended_element = None
        self.description = f"追加{tag_name}元素(id={id_value})到{parent_id}"
        
    def execute(self) -> bool:
        """执行追加命令"""
        try:
            self._validate_params()
            
            # 查找父元素
            parent = self.model.find_by_id(self.parent_id)
            
            # 创建新元素
            new_element = HtmlElement(self.tag_name, self.id_value)
            if self.text:
                new_element.text = self.text
                
            # 添加到父元素
            parent.add_child(new_element)
            new_element.parent = parent
            
            # 注册ID到模型
            self.model._register_id(new_element)
            self.appended_element = new_element
            
            print(f"Appended '{self.id_value}' as child of '{self.parent_id}'")
            return True
        except (DuplicateIdError, ElementNotFoundError):
            # 直接抛出原始异常
            raise
        except Exception as e:
            raise CommandExecutionError(f"执行追加命令时发生意外错误: {str(e)}") from e
    
    def _validate_params(self) -> None:
        """验证参数有效性"""
        if not self.tag_name or not isinstance(self.tag_name, str):
            raise ValueError("标签名不能为空且必须是字符串")
            
        if not self.id_value or not isinstance(self.id_value, str):
            raise ValueError("ID不能为空且必须是字符串")
            
        if not self.parent_id or not isinstance(self.parent_id, str):
            raise ValueError("父元素ID不能为空且必须是字符串")
            
        # 检查ID是否已存在
        if self.id_value in self.model._id_map:
            raise DuplicateIdError(f"ID '{self.id_value}' 已存在")
            
        # 检查父元素是否存在
        if self.parent_id not in self.model._id_map:
            raise ElementNotFoundError(f"未找到ID为 '{self.parent_id}' 的父元素")
    
    def undo(self) -> bool:
        """撤销追加命令"""
        try:
            # 找到父元素
            parent = self.model.find_by_id(self.parent_id)
            
            # 从父元素中移除
            parent.remove_child(self.appended_element)
            
            # 从ID映射中移除
            self.model._unregister_id(self.appended_element)
            
            return True
        except Exception as e:
            print(f"撤销追加失败: {e}")
            return False
from ..base import Command
from ...core.html_model import HtmlModel
from ...core.element import HtmlElement
from ...core.exceptions import ElementNotFoundError, DuplicateIdError

class AppendCommand(Command):
    """在指定元素内追加子元素"""
    def __init__(self, model: HtmlModel, tag_name: str, id_value: str, parent_id: str, text: str = None):
        super().__init__()
        self.model = model
        self.tag_name = tag_name
        self.id_value = id_value
        self.parent_id = parent_id
        self.text = text
        self.appended_element = None
        self.parent = None

    def _validate_params(self) -> None:
        """验证参数有效性"""
        if not self.tag_name or not isinstance(self.tag_name, str):
            raise ValueError("标签名不能为空且必须是字符串")
            
        if not self.id_value or not isinstance(self.id_value, str):
            raise ValueError("ID不能为空且必须是字符串")
            
        if not self.parent_id or not isinstance(self.parent_id, str):
            raise ValueError("父元素ID不能为空且必须是字符串")
            
        # 检查ID是否已存在
        if self.model.find_by_id(self.id_value):
            raise DuplicateIdError(f"ID '{self.id_value}' 已存在")
            
        # 检查父元素是否存在
        self.parent = self.model.find_by_id(self.parent_id)
        if not self.parent:
            raise ElementNotFoundError(f"未找到ID为 '{self.parent_id}' 的父元素")

    def execute(self) -> bool:
        """执行追加命令"""
        try:
            # 验证参数
            self._validate_params()
            
            # 创建新元素
            self.appended_element = HtmlElement(self.tag_name, self.id_value)
            if self.text:
                self.appended_element.text = self.text
                
            # 注册新元素ID
            self.model._register_id(self.appended_element)
            
            # 添加到父元素
            if self.parent.add_child(self.appended_element):
                return True
            
            # 如果添加失败，清理注册的ID
            self.model._unregister_id(self.appended_element)
            return False
            
        except Exception as e:
            # 发生错误时进行清理
            if self.appended_element:
                if self.appended_element.id in self.model._id_map:
                    self.model._unregister_id(self.appended_element)
                if self.appended_element.parent:
                    self.appended_element.parent.remove_child(self.appended_element)
            raise
            
    def undo(self) -> bool:
        """撤销追加命令"""
        try:
            # 确保有需要撤销的状态
            if not (self.appended_element and self.parent):
                return False
                
            # 从父元素中删除已追加的元素
            if self.parent.remove_child(self.appended_element):
                # 更新模型的ID映射
                if self.appended_element.id in self.model._id_map:
                    self.model._unregister_id(self.appended_element)
                return True
                
            return False
            
        except Exception as e:
            print(f"撤销追加命令时发生错误: {str(e)}")
            return False
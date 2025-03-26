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
        self.parent = None  # 将在执行时设置
        self._executed = False  # 跟踪命令是否已执行

    def _validate_params(self) -> None:
        """验证参数有效性"""
        if not self.tag_name or not isinstance(self.tag_name, str):
            raise ValueError("标签名不能为空且必须是字符串")
            
        if not self.id_value or not isinstance(self.id_value, str):
            raise ValueError("ID不能为空且必须是字符串")
            
        if not self.parent_id or not isinstance(self.parent_id, str):
            raise ValueError("父元素ID不能为空且必须是字符串")
            
        # 检查ID是否已存在
        try:
            if self.model.find_by_id(self.id_value):
                raise DuplicateIdError(f"ID '{self.id_value}' 已存在")
        except ElementNotFoundError:
            # 如果ID不存在，这是我们想要的，继续执行
            pass
            
        # 检查父元素是否存在
        try:
            self.parent = self.model.find_by_id(self.parent_id)
        except ElementNotFoundError:
            raise ElementNotFoundError(f"父元素ID '{self.parent_id}' 不存在")

    def execute(self) -> bool:
        """执行追加命令"""
        try:
            # 如果命令已执行，直接返回
            if self._executed:
                return True
                
            # 验证参数
            self._validate_params()
            
            # 创建新元素
            self.appended_element = HtmlElement(self.tag_name, self.id_value)
            if self.text:
                self.appended_element.text = self.text
                
            # 注册新元素ID
            self.model._register_id(self.appended_element)
            
            # 添加到父元素 - 确保this.parent已经初始化
            if self.parent and self.parent.add_child(self.appended_element):
                self.appended_element.parent = self.parent
                print(f"Appended '{self.id_value}' as child of '{self.parent_id}'")
                self._executed = True
                return True
            
            # 如果添加失败，清理注册的ID
            self.model._unregister_id(self.appended_element)
            return False
            
        except (ValueError, DuplicateIdError, ElementNotFoundError) as e:
            # 发生错误时进行清理
            if self.appended_element:
                if self.appended_element.id in self.model._id_map:
                    self.model._unregister_id(self.appended_element)
                if self.appended_element.parent:
                    self.appended_element.parent.remove_child(self.appended_element)
            # 向上传播异常
            raise
        except Exception as e:
            print(f"追加元素时发生错误: {str(e)}")
            self._executed = False
            return False
            
    def undo(self) -> bool:
        """撤销追加命令"""
        try:
            # 确保有需要撤销的状态
            if not self.appended_element or not self._executed:
                return False
                
            # 从父元素中删除已追加的元素
            if self.parent and self.appended_element in self.parent.children:
                self.parent.children.remove(self.appended_element)
                
                # 更新模型的ID映射
                if self.appended_element.id in self.model._id_map:
                    del self.model._id_map[self.appended_element.id]
                
                print(f"Successfully removed '{self.appended_element.id}' from '{self.parent.id}'")
                self._executed = False
                return True
                
            print(f"Failed to undo: element '{self.appended_element.id}' not found in parent's children")
            return False
            
        except Exception as e:
            print(f"撤销追加命令时发生错误: {str(e)}")
            return False
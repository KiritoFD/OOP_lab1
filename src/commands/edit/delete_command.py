from ..base import Command
from ...core.html_model import HtmlModel
from ...core.element import HtmlElement
from ...core.exceptions import ElementNotFoundError

class DeleteCommand(Command):
    """删除指定元素"""
    def __init__(self, model: HtmlModel, element_id: str):
        super().__init__()
        self.model = model
        self.element_id = element_id
        self.deleted_element = None
        self.parent = None
        self.next_sibling = None

    def _validate_params(self) -> None:
        """验证参数有效性"""
        if not self.element_id or not isinstance(self.element_id, str):
            raise ValueError("元素ID不能为空且必须是字符串")
            
        # 查找要删除的元素
        self.deleted_element = self.model.find_by_id(self.element_id)
        if not self.deleted_element:
            raise ElementNotFoundError(f"未找到ID为 '{self.element_id}' 的元素")
            
        # 检查是否有父元素
        if not self.deleted_element.parent:
            raise ValueError("根元素不能被删除")

    def execute(self) -> bool:
        """执行删除命令"""
        try:
            # 验证参数
            self._validate_params()
            
            # 保存状态用于撤销
            self.parent = self.deleted_element.parent
            siblings = self.parent.children
            idx = siblings.index(self.deleted_element)
            self.next_sibling = siblings[idx + 1] if idx + 1 < len(siblings) else None
            
            # 执行删除操作
            return self.model.delete_element(self.element_id)
            
        except Exception as e:
            # 重置状态
            self.deleted_element = None
            self.parent = None
            self.next_sibling = None
            raise
            
    def undo(self) -> bool:
        """撤销删除命令"""
        try:
            # 确保有需要撤销的状态
            if not (self.deleted_element and self.parent):
                return False
                
            # 重新注册元素ID
            self.model._register_id(self.deleted_element)
            
            # 如果有下一个兄弟节点，在其前面插入
            if self.next_sibling:
                result = self.model.insert_before(self.next_sibling.id, self.deleted_element)
            else:
                # 否则追加到父节点
                result = self.parent.add_child(self.deleted_element)
                
            if not result:
                # 如果插入失败，取消ID注册
                self.model._unregister_id(self.deleted_element)
                
            return result
            
        except Exception as e:
            print(f"撤销删除命令时发生错误: {str(e)}")
            return False
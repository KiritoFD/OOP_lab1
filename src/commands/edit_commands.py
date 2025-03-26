from .base import Command
from ..core.html_model import HtmlModel
from ..core.element import HtmlElement

class InsertCommand(Command):
    """在指定位置前插入元素"""
    def __init__(self, model: HtmlModel, tag_name: str, id_value: str, location: str, text: str = None):
        super().__init__()
        self.model = model
        self.tag_name = tag_name
        self.id_value = id_value
        self.location = location
        self.text = text
        self.inserted_element = None
        self.parent = None
        self.next_sibling = None

    def execute(self) -> bool:
        # 创建新元素
        self.inserted_element = HtmlElement(self.tag_name, self.id_value)
        if self.text:
            self.inserted_element.text = self.text

        # 查找目标位置
        target = self.model.find_by_id(self.location)
        if not target:
            return False

        # 保存当前状态（用于撤销）
        self.parent = target.parent
        self.next_sibling = target

        # 执行插入操作
        return self.model.insert_before(self.location, self.inserted_element)

    def undo(self) -> bool:
        # 直接通过命令的状态信息撤销，不依赖模型的查找
        if self.inserted_element and self.parent:
            return self.parent.remove_child(self.inserted_element)
        return False

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

    def execute(self) -> bool:
        # 使用model的append_child方法，它会同时处理_id_map的更新
        self.appended_element = self.model.append_child(
            self.parent_id, 
            self.tag_name, 
            self.id_value, 
            self.text
        )
        return self.appended_element is not None

    def undo(self) -> bool:
        # 使用model的delete_element方法撤销
        if self.appended_element:
            return self.model.delete_element(self.appended_element.id)
        return False

class DeleteCommand(Command):
    """删除指定元素"""
    def __init__(self, model: HtmlModel, element_id: str):
        super().__init__()
        self.model = model
        self.element_id = element_id
        self.deleted_element = None
        self.parent = None
        self.next_sibling = None

    def execute(self) -> bool:
        # 查找并保存元素信息（用于撤销）
        self.deleted_element = self.model.find_by_id(self.element_id)
        if not self.deleted_element:
            return False

        # 保存位置信息
        self.parent = self.deleted_element.parent
        siblings = self.parent.children if self.parent else []
        idx = siblings.index(self.deleted_element)
        self.next_sibling = siblings[idx + 1] if idx + 1 < len(siblings) else None

        # 执行删除
        return self.model.delete_element(self.element_id)

    def undo(self) -> bool:
        # 使用保存的信息恢复元素
        if not (self.deleted_element and self.parent):
            return False

        # 如果有下一个兄弟节点，在其前面插入
        if self.next_sibling:
            return self.model.insert_before(self.next_sibling.id, self.deleted_element)
        else:
            # 否则追加到父节点
            return self.parent.add_child(self.deleted_element)

class EditTextCommand(Command):
    """编辑元素文本内容"""
    def __init__(self, model: HtmlModel, element_id: str, new_text: str):
        super().__init__()
        self.model = model
        self.element_id = element_id
        self.new_text = new_text
        self.old_text = None
        self.element = None

    def execute(self) -> bool:
        self.element = self.model.find_by_id(self.element_id)
        if not self.element:
            return False

        # 保存原文本
        self.old_text = self.element.text
        # 设置新文本
        self.element.text = self.new_text
        return True

    def undo(self) -> bool:
        if not self.element or self.old_text is None:
            return False
        # 恢复原文本
        self.element.text = self.old_text
        return True

class EditIdCommand(Command):
    """编辑元素ID"""
    def __init__(self, model: HtmlModel, old_id: str, new_id: str):
        super().__init__()
        self.model = model
        self.old_id = old_id
        self.new_id = new_id
        self.element = None

    def execute(self) -> bool:
        self.element = self.model.find_by_id(self.old_id)
        if not self.element:
            return False

        # 验证新ID是否可用
        if self.model.find_by_id(self.new_id):
            return False

        # 更新ID
        old_id = self.element.id
        self.element.id = self.new_id
        return True

    def undo(self) -> bool:
        if not self.element:
            return False
        # 恢复原ID
        self.element.id = self.old_id
        return True
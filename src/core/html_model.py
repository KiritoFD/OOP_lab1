from typing import Dict, Optional
from .element import HtmlElement
from .exceptions import DuplicateIdError, ElementNotFoundError

class HtmlModel:
    """HTML文档模型，管理整个HTML树结构"""
    def __init__(self):
        # 创建基本结构
        self.root = HtmlElement('html')
        self._id_map = {self.root.id: self.root}
        
        # 创建head和body节点
        head = HtmlElement('head')
        body = HtmlElement('body')
        self.root.add_child(head)
        self.root.add_child(body)
        self._id_map[head.id] = head
        self._id_map[body.id] = body
        
        # 创建title节点
        title = HtmlElement('title')
        head.add_child(title)
        self._id_map[title.id] = title

    def find_by_id(self, id: str) -> Optional[HtmlElement]:
        """通过ID查找元素"""
        return self._id_map.get(id)

    def insert_before(self, target_id: str, element: HtmlElement) -> bool:
        """在目标元素之前插入新元素"""
        if element.id in self._id_map:
            raise DuplicateIdError(element.id)
            
        target = self.find_by_id(target_id)
        if not target:
            raise ElementNotFoundError(target_id)
            
        parent = target.parent
        if not parent:
            return False
            
        # 获取目标元素在父元素children中的索引
        index = parent.children.index(target)
        # 在该位置插入新元素
        parent.children.insert(index, element)
        element.parent = parent
        
        # 更新ID索引
        self._id_map[element.id] = element
        return True

    def append_child(self, parent_id: str, tag_name: str = None, id_value: str = None, text: str = None) -> Optional[HtmlElement]:
        """添加子元素
        
        可以接受以下两种调用方式:
        1. append_child(parent_id, existing_element) - 添加已存在的元素
        2. append_child(parent_id, tag_name, id_value, text) - 创建并添加新元素
        """
        parent = self.find_by_id(parent_id)
        if not parent:
            raise ElementNotFoundError(parent_id)
            
        # 如果第二个参数是HtmlElement对象，使用旧的实现
        if isinstance(tag_name, HtmlElement):
            element = tag_name
            if element.id in self._id_map:
                raise DuplicateIdError(element.id)
                
            parent.add_child(element)
            self._id_map[element.id] = element
            return element
        
        # 否则创建新元素
        if tag_name is None:
            return None
            
        # 创建新元素
        element = HtmlElement(tag_name, id_value)
        if text:
            element.text = text
            
        # 检查ID是否重复
        if element.id in self._id_map:
            raise DuplicateIdError(element.id)
            
        # 添加到父元素
        parent.add_child(element)
        self._id_map[element.id] = element
        return element

    def delete_element(self, element_id: str) -> bool:
        """删除元素"""
        element = self.find_by_id(element_id)
        if not element:
            raise ElementNotFoundError(element_id)
            
        if element.parent:
            element.parent.remove_child(element)
            del self._id_map[element_id]
            return True
        return False

    def replace_content(self, new_root: HtmlElement) -> bool:
        """替换整个文档内容
        用于IO命令实现文件读取和初始化功能
        """
        try:
            # 清空当前模型
            self._id_map.clear()
            
            # 深拷贝新的内容
            def copy_element(src: HtmlElement) -> HtmlElement:
                new_elem = HtmlElement(src.tag, src.id)
                new_elem.text = src.text
                for child in src.children:
                    new_child = copy_element(child)
                    new_elem.add_child(new_child)
                    self._id_map[new_child.id] = new_child
                return new_elem
            
            # 创建新的根节点
            self.root = copy_element(new_root)
            self._id_map[self.root.id] = self.root
            return True
            
        except Exception as e:
            # 如果替换失败，保持原状
            return False

    def can_have_children(self, element: HtmlElement) -> bool:
        """检查元素是否可以有子元素"""
        # 所有元素都可以有子元素
        return True
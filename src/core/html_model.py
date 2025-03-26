from typing import Optional, Dict
from .element import HtmlElement
from .exceptions import DuplicateIdError, ElementNotFoundError

class HtmlModel:
    """HTML文档模型"""
    def __init__(self):
        # 创建根元素
        self.root = HtmlElement('html', 'html')  # 修改ID为'html'
        # 创建基本结构
        head = HtmlElement('head', 'head')
        body = HtmlElement('body', 'body')
        self.root.add_child(head)
        self.root.add_child(body)
        
        # ID到元素的映射
        self._id_map: Dict[str, HtmlElement] = {
            'html': self.root,  # 更新映射
            'head': head,
            'body': body
        }
        
    def find_by_id(self, id: str) -> Optional[HtmlElement]:
        """通过ID查找元素"""
        return self._id_map.get(id)
        
    def _register_id(self, element: HtmlElement) -> None:
        """注册元素ID到映射表"""
        if element.id in self._id_map:
            raise DuplicateIdError(f"ID '{element.id}' 已存在")
        self._id_map[element.id] = element
        
    def _unregister_id(self, element: HtmlElement) -> None:
        """从映射表中移除元素ID"""
        if element.id in self._id_map:
            del self._id_map[element.id]
            
    def insert_before(self, target_id: str, new_element: HtmlElement) -> bool:
        """在指定元素前插入新元素"""
        target = self.find_by_id(target_id)
        if not target:
            raise ElementNotFoundError(f"未找到ID为 '{target_id}' 的元素")

        parent = target.parent if target.parent else self.root

        try:
            # 注册新元素ID
            self._register_id(new_element)

            # 获取目标元素在父元素中的索引
            index = parent.children.index(target)

            # 设置父子关系
            new_element.parent = parent
            parent.children.insert(index, new_element)

            # 调试输出
            print(f"Inserted element '{new_element.id}' with parent '{new_element.parent.id}'")

            return True

        except Exception as e:
            # 清理失败的插入操作
            self._cleanup_after_failed_insert(new_element, parent)
            raise
            
    def _cleanup_after_failed_insert(self, element: HtmlElement, parent: HtmlElement) -> None:
        """清理失败的插入操作"""
        if element.id in self._id_map:
            self._unregister_id(element)
        if element in parent.children:
            parent.children.remove(element)
        element.parent = None
            
    def _register_subtree_ids(self, root: HtmlElement) -> None:
        """递归注册子树中所有元素的ID"""
        for child in root.children:
            if child.id:
                self._register_id(child)
            self._register_subtree_ids(child)
            
    def append_child(self, parent_id: str, tag: str, id: str, text: str = None) -> Optional[HtmlElement]:
        """向指定元素追加子元素"""
        parent = self.find_by_id(parent_id)
        if not parent:
            raise ElementNotFoundError(f"未找到ID为 '{parent_id}' 的父元素")
            
        # 创建新元素
        new_element = HtmlElement(tag, id)
        if text:
            new_element.text = text
            
        try:
            # 注册新元素ID
            self._register_id(new_element)
            
            # 添加到父元素
            parent.add_child(new_element)
            
            return new_element
            
        except Exception as e:
            # 发生错误时回滚更改
            if new_element.id in self._id_map:
                self._unregister_id(new_element)
            if new_element.parent:
                new_element.parent.remove_child(new_element)
            raise
            
    def delete_element(self, element_id: str) -> bool:
        """删除指定元素"""
        element = self.find_by_id(element_id)
        if not element or not element.parent:
            return False
            
        try:
            # 递归注销所有子元素的ID
            self._unregister_subtree_ids(element)
            
            # 从父元素中移除
            return element.parent.remove_child(element)
            
        except Exception as e:
            print(f"删除元素时发生错误: {str(e)}")
            return False
            
    def _unregister_subtree_ids(self, root: HtmlElement) -> None:
        """递归注销子树中所有元素的ID"""
        for child in root.children:
            if child.id:
                self._unregister_id(child)
            self._unregister_subtree_ids(child)
            
    def replace_content(self, new_root: HtmlElement) -> None:
        """替换整个文档内容"""
        # 清除旧的ID映射
        self._id_map.clear()
        
        # 替换根元素
        self.root = new_root
        
        # 重新注册所有ID
        self._register_id(self.root)
        self._register_subtree_ids(self.root)
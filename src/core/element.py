from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod
from .exceptions import InvalidOperationError

class HtmlVisitor(ABC):
    """访问者接口"""
    @abstractmethod
    def visit(self, element: 'HtmlElement') -> None:
        pass

class HtmlElement:
    """HTML元素类"""
    
    def __init__(self, tag, id):
        """初始化HTML元素"""
        self.tag = tag
        self.id = id
        self.children = []
        self.parent = None
        self.attributes = {}
        self.text = ''  # Initialize as empty string, not None
    
    def add_child(self, child):
        """添加子元素，并处理父子关系"""
        # 检查是否试图添加元素自身
        if child == self:
            raise InvalidOperationError(f"不能将元素自身添加为子元素: {self.id}")
            
        # 检查是否形成循环引用 - 修正实现
        if child.is_ancestor_of(self):
            raise InvalidOperationError(f"循环引用: 元素 {self.id} 已经是 {child.id} 的后代")
            
        # 如果子元素已有父元素，先从原父元素中移除
        if child.parent:
            child.parent.remove_child(child)
            
        # 建立父子关系
        self.children.append(child)
        child.parent = self
        
    def remove_child(self, child):
        """移除子元素，解除父子关系"""
        if child in self.children:
            self.children.remove(child)
            child.parent = None
            return True
        return False
        
    def set_attribute(self, name, value):
        """设置元素属性"""
        self.attributes[name] = value
        
    def get_attribute(self, name, default=None):
        """获取元素属性值，不存在时返回默认值"""
        return self.attributes.get(name, default)
        
    def remove_attribute(self, name):
        """移除元素属性"""
        if name in self.attributes:
            del self.attributes[name]
            
    def has_attribute(self, name):
        """检查是否存在指定属性"""
        return name in self.attributes
        
    def copy(self, deep=False):
        """
        复制元素
        
        Args:
            deep: 是否深度复制（包括子元素）
            
        Returns:
            复制的元素
        """
        # 创建新元素
        new_element = HtmlElement(self.tag, self.id)
        new_element.text = self.text
        new_element.attributes = self.attributes.copy()
        
        # 如果需要深度复制，递归复制所有子元素
        if deep:
            for child in self.children:
                child_copy = child.copy(deep=True)
                new_element.add_child(child_copy)
                
        return new_element
        
    def is_ancestor_of(self, element):
        """检查当前元素是否是指定元素的祖先"""
        if element is None or element == self:
            return False
            
        current = element.parent
        while current:
            if current == self:
                return True
            current = current.parent
        
        return False
        
    def get_parent_chain(self):
        """获取从当前元素到根元素的父元素链"""
        chain = []
        parent = self.parent
        
        while parent:
            chain.append(parent)
            parent = parent.parent
            
        return chain

    def accept(self, visitor: HtmlVisitor) -> None:
        """访问者模式接口"""
        visitor.visit(self)
        for child in self.children:
            child.accept(visitor)

    def find_child(self, id: str) -> Optional['HtmlElement']:
        """查找指定ID的子元素
        
        Args:
            id: 要查找的子元素ID
            
        Returns:
            找到的子元素，未找到则返回None
        """
        # 先在直接子元素中查找
        for child in self.children:
            if child.id == id:
                return child
                
        # 递归查找子元素的子元素
        for child in self.children:
            result = child.find_child(id)
            if result:
                return result
                
        return None
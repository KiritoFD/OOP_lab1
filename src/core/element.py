from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod

class HtmlVisitor(ABC):
    """访问者接口"""
    @abstractmethod
    def visit(self, element: 'HtmlElement') -> None:
        pass

class HtmlElement:
    """HTML元素基类"""
    def __init__(self, tag: str, id: str = None):
        self.tag = tag
        self.id = id or tag
        self.text = None
        self.children: List[HtmlElement] = []
        self.parent: Optional[HtmlElement] = None
        self.attributes: Dict[str, str] = {}  # 添加属性字典
        
    def add_child(self, child: 'HtmlElement') -> bool:
        """添加子元素"""
        if not child:
            return False
            
        # 如果子元素已经在正确位置，直接返回成功
        if child in self.children and child.parent is self:
            return True
            
        # 如果子元素已有父元素，先移除
        if child.parent:
            child.parent.children.remove(child)
            
        # 设置新的父子关系
        child.parent = self
        if child not in self.children:
            self.children.append(child)
            
        return True
        
    def remove_child(self, child: 'HtmlElement') -> bool:
        """移除子元素"""
        if child not in self.children:
            return False
            
        # 解除父子关系
        child.parent = None
        self.children.remove(child)
        return True

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
        
    # 添加属性管理方法
    def get_attribute(self, name: str) -> Optional[str]:
        """获取属性值"""
        return self.attributes.get(name)
        
    def set_attribute(self, name: str, value: str) -> None:
        """设置属性值"""
        self.attributes[name] = value
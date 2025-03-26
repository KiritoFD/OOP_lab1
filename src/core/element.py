from typing import List, Optional
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
        self.id = id or tag  # 如果没有提供id，使用tag作为默认id
        self.text = ""
        self.children: List[HtmlElement] = []
        self.parent: Optional[HtmlElement] = None

    def add_child(self, child: 'HtmlElement') -> bool:
        """添加子元素"""
        if child.parent is not None:
            return False
            
        child.parent = self
        self.children.append(child)
        return True

    def remove_child(self, child: 'HtmlElement') -> bool:
        """移除子元素"""
        if child not in self.children:
            return False
            
        child.parent = None
        self.children.remove(child)
        return True

    def accept(self, visitor: HtmlVisitor) -> None:
        """访问者模式接口"""
        visitor.visit(self)
        for child in self.children:
            child.accept(visitor)
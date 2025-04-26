import pytest
from src.core.element import HtmlElement
from src.core.exceptions import InvalidOperationError

@pytest.mark.unit
class TestHtmlElement:
    """测试HTML元素类"""
    
    def test_init_attributes(self):
        """测试元素初始化"""
        element = HtmlElement('div', 'test-id')
        assert element.tag == 'div'
        assert element.id == 'test-id'
        assert element.children == []
        assert element.parent is None
        assert element.attributes == {}
        assert element.text == ''
        
    def test_add_child(self):
        """测试添加子元素"""
        parent = HtmlElement('div', 'parent')
        child = HtmlElement('p', 'child')
        
        parent.add_child(child)
        
        assert child in parent.children
        assert child.parent == parent
        assert len(parent.children) == 1
        
    def test_add_multiple_children(self):
        """测试添加多个子元素"""
        parent = HtmlElement('div', 'parent')
        child1 = HtmlElement('p', 'child1')
        child2 = HtmlElement('span', 'child2')
        child3 = HtmlElement('a', 'child3')
        
        parent.add_child(child1)
        parent.add_child(child2)
        parent.add_child(child3)
        
        assert len(parent.children) == 3
        assert parent.children[0] == child1
        assert parent.children[1] == child2
        assert parent.children[2] == child3
        
    def test_add_child_already_has_parent(self):
        """测试添加已有父元素的子元素"""
        parent1 = HtmlElement('div', 'parent1')
        parent2 = HtmlElement('div', 'parent2')
        child = HtmlElement('p', 'child')
        
        parent1.add_child(child)
        parent2.add_child(child)
        
        # 子元素应该移动到新的父元素
        assert child not in parent1.children
        assert child in parent2.children
        assert child.parent == parent2
        
    def test_add_child_self_reference(self):
        """测试将元素自身添加为子元素"""
        element = HtmlElement('div', 'self')
        
        with pytest.raises(InvalidOperationError):
            element.add_child(element)
            
    def test_add_child_circular_reference(self):
        """测试添加循环引用"""
        parent = HtmlElement('div', 'parent')
        child = HtmlElement('p', 'child')
        grandchild = HtmlElement('span', 'grandchild')
        
        parent.add_child(child)
        child.add_child(grandchild)
        
        with pytest.raises(InvalidOperationError):
            grandchild.add_child(parent)
            
    def test_remove_child(self):
        """测试移除子元素"""
        parent = HtmlElement('div', 'parent')
        child1 = HtmlElement('p', 'child1')
        child2 = HtmlElement('span', 'child2')
        
        parent.add_child(child1)
        parent.add_child(child2)
        
        result = parent.remove_child(child1)
        
        assert result is True
        assert child1 not in parent.children
        assert child1.parent is None
        assert len(parent.children) == 1
        assert parent.children[0] == child2
        
    def test_remove_nonexistent_child(self):
        """测试移除不存在的子元素"""
        parent = HtmlElement('div', 'parent')
        child = HtmlElement('p', 'child')
        nonchild = HtmlElement('span', 'nonchild')
        
        parent.add_child(child)
        
        result = parent.remove_child(nonchild)
        
        assert result is False
        assert len(parent.children) == 1
        assert child in parent.children
        
    def test_set_attribute(self):
        """测试设置属性"""
        element = HtmlElement('div', 'test')
        
        element.set_attribute('class', 'container')
        element.set_attribute('data-id', '123')
        
        assert element.attributes == {'class': 'container', 'data-id': '123'}
        
    def test_get_attribute(self):
        """测试获取属性"""
        element = HtmlElement('div', 'test')
        element.attributes = {'class': 'container', 'data-id': '123'}
        
        assert element.get_attribute('class') == 'container'
        assert element.get_attribute('data-id') == '123'
        assert element.get_attribute('nonexistent') is None
        assert element.get_attribute('nonexistent', 'default') == 'default'
        
    def test_remove_attribute(self):
        """测试移除属性"""
        element = HtmlElement('div', 'test')
        element.attributes = {'class': 'container', 'data-id': '123'}
        
        element.remove_attribute('class')
        
        assert 'class' not in element.attributes
        assert element.attributes == {'data-id': '123'}
        
    def test_remove_nonexistent_attribute(self):
        """测试移除不存在的属性"""
        element = HtmlElement('div', 'test')
        element.attributes = {'class': 'container'}
        
        # 不应抛出异常
        element.remove_attribute('nonexistent')
        assert element.attributes == {'class': 'container'}
        
    def test_has_attribute(self):
        """测试属性存在性检查"""
        element = HtmlElement('div', 'test')
        element.attributes = {'class': 'container', 'data-empty': ''}
        
        assert element.has_attribute('class') is True
        assert element.has_attribute('data-empty') is True
        assert element.has_attribute('nonexistent') is False
        
    def test_copy(self):
        """测试元素复制"""
        original = HtmlElement('div', 'original')
        original.text = 'Original text'
        original.attributes = {'class': 'container'}
        
        child = HtmlElement('p', 'child')
        original.add_child(child)
        
        # 复制元素
        copy = original.copy()
        
        # 验证基本属性被复制
        assert copy.tag == original.tag
        assert copy.id == original.id
        assert copy.text == original.text
        assert copy.attributes == original.attributes
        
        # 验证关系不复制
        assert copy.parent is None
        assert len(copy.children) == 0
        
    def test_copy_deep(self):
        """测试元素深度复制"""
        original = HtmlElement('div', 'original')
        original.text = 'Original text'
        original.attributes = {'class': 'container'}
        
        child = HtmlElement('p', 'child')
        child.text = 'Child text'
        original.add_child(child)
        
        grandchild = HtmlElement('span', 'grandchild')
        grandchild.text = 'Grandchild text'
        child.add_child(grandchild)
        
        # 执行深度复制
        copy = original.copy(deep=True)
        
        # 验证基本属性被复制
        assert copy.tag == original.tag
        assert copy.id == original.id
        assert copy.text == original.text
        assert copy.attributes == original.attributes
        
        # 验证子元素结构被复制
        assert len(copy.children) == 1
        copied_child = copy.children[0]
        assert copied_child.tag == child.tag
        assert copied_child.id == child.id
        assert copied_child.text == child.text
        assert copied_child.parent == copy
        
        assert len(copied_child.children) == 1
        copied_grandchild = copied_child.children[0]
        assert copied_grandchild.tag == grandchild.tag
        assert copied_grandchild.id == grandchild.id
        assert copied_grandchild.text == grandchild.text
        assert copied_grandchild.parent == copied_child
        
    def test_is_ancestor_of(self):
        """测试祖先关系检查"""
        root = HtmlElement('html', 'root')
        parent = HtmlElement('div', 'parent')
        child = HtmlElement('p', 'child')
        grandchild = HtmlElement('span', 'grandchild')
        
        root.add_child(parent)
        parent.add_child(child)
        child.add_child(grandchild)
        
        # 直接和间接祖先
        assert root.is_ancestor_of(parent) is True
        assert root.is_ancestor_of(child) is True
        assert root.is_ancestor_of(grandchild) is True
        assert parent.is_ancestor_of(child) is True
        assert parent.is_ancestor_of(grandchild) is True
        assert child.is_ancestor_of(grandchild) is True
        
        # 非祖先
        assert grandchild.is_ancestor_of(child) is False
        assert child.is_ancestor_of(parent) is False
        assert parent.is_ancestor_of(root) is False
        
        # 自身不是自己的祖先
        assert root.is_ancestor_of(root) is False
        
        # 无关元素
        other = HtmlElement('div', 'other')
        assert root.is_ancestor_of(other) is False
        
    def test_get_parent_chain(self):
        """测试获取父元素链"""
        root = HtmlElement('html', 'root')
        parent = HtmlElement('div', 'parent')
        child = HtmlElement('p', 'child')
        
        root.add_child(parent)
        parent.add_child(child)
        
        # 获取child的父元素链
        parent_chain = child.get_parent_chain()
        
        assert len(parent_chain) == 2
        assert parent_chain[0] == parent
        assert parent_chain[1] == root
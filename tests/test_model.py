import pytest
from src.core.html_model import HtmlModel
from src.core.element import HtmlElement
from src.core.exceptions import ElementNotFoundError, DuplicateIdError

class TestHtmlModel:
    @pytest.fixture
    def model(self):
        return HtmlModel()
    
    def test_init_model(self, model):
        """测试模型初始化"""
        # 验证基本HTML结构
        html = model.find_by_id('html')
        head = model.find_by_id('head')
        title = model.find_by_id('title')
        body = model.find_by_id('body')
        
        assert html is not None
        assert head is not None
        assert title is not None
        assert body is not None
        
        # 验证元素关系
        assert head in html.children
        assert body in html.children
        assert title in head.children
        
    def test_find_by_id(self, model):
        """测试通过ID查找元素"""
        # 测试查找现有元素
        body = model.find_by_id('body')
        assert body is not None
        assert body.id == 'body'
        
        # 测试查找不存在的元素
        nonexistent = model.find_by_id('nonexistent')
        assert nonexistent is None
        
    def test_add_element(self, model):
        """测试添加元素"""
        # 创建新元素
        div = HtmlElement('div', 'test-div')
        
        # 添加到body
        body = model.find_by_id('body')
        model.add_element(div, body)
        
        # 验证添加成功
        added_div = model.find_by_id('test-div')
        assert added_div is not None
        assert added_div.parent == body
        assert added_div in body.children
        
    def test_add_duplicate_id(self, model):
        """测试添加重复ID的元素"""
        div1 = HtmlElement('div', 'test-div')
        div2 = HtmlElement('div', 'test-div')
        
        body = model.find_by_id('body')
        model.add_element(div1, body)
        
        # 尝试添加重复ID的元素
        with pytest.raises(DuplicateIdError):
            model.add_element(div2, body)
            
    def test_remove_element(self, model):
        """测试删除元素"""
        # 准备要删除的元素
        div = HtmlElement('div', 'test-div')
        body = model.find_by_id('body')
        model.add_element(div, body)
        
        # 执行删除
        removed = model.remove_element('test-div')
        
        # 验证删除成功
        assert removed is True
        assert model.find_by_id('test-div') is None
        assert div not in body.children
        
    def test_remove_nonexistent_element(self, model):
        """测试删除不存在的元素"""
        assert model.remove_element('nonexistent') is False
        
    def test_remove_core_element(self, model):
        """测试删除核心元素（不应允许）"""
        core_elements = ['html', 'head', 'title', 'body']
        for id in core_elements:
            assert model.remove_element(id) is False
            assert model.find_by_id(id) is not None
            
    def test_element_hierarchy(self, model):
        """测试元素层级关系"""
        # 创建多层嵌套结构
        elements = [
            HtmlElement('div', 'parent'),
            HtmlElement('p', 'child1'),
            HtmlElement('span', 'child2'),
            HtmlElement('em', 'grandchild')
        ]
        
        body = model.find_by_id('body')
        model.add_element(elements[0], body)  # 添加父元素
        model.add_element(elements[1], elements[0])  # 添加第一个子元素
        model.add_element(elements[2], elements[0])  # 添加第二个子元素
        model.add_element(elements[3], elements[1])  # 添加孙元素
        
        # 验证层级关系
        assert elements[0].parent == body
        assert elements[1].parent == elements[0]
        assert elements[2].parent == elements[0]
        assert elements[3].parent == elements[1]
        
        assert elements[1] in elements[0].children
        assert elements[2] in elements[0].children
        assert elements[3] in elements[1].children
        
    def test_clear_model(self, model):
        """测试清空模型"""
        # 添加一些元素
        div = HtmlElement('div', 'test-div')
        p = HtmlElement('p', 'test-p')
        body = model.find_by_id('body')
        model.add_element(div, body)
        model.add_element(p, div)
        
        # 清空模型
        model.clear()
        
        # 验证只保留核心元素
        core_elements = ['html', 'head', 'title', 'body']
        for id in core_elements:
            assert model.find_by_id(id) is not None
            
        # 验证其他元素被删除
        assert model.find_by_id('test-div') is None
        assert model.find_by_id('test-p') is None
        assert len(body.children) == 0
        
    def test_element_text(self, model):
        """测试元素文本操作"""
        # 创建带文本的元素
        p = HtmlElement('p', 'test-p')
        p.text = 'Test text'
        
        body = model.find_by_id('body')
        model.add_element(p, body)
        
        # 验证文本
        found = model.find_by_id('test-p')
        assert found.text == 'Test text'
        
        # 修改文本
        found.text = 'Updated text'
        assert found.text == 'Updated text'
        
        # 清空文本
        found.text = ''
        assert found.text == ''
        
    def test_nested_operations(self, model):
        """测试嵌套元素的操作"""
        # 创建嵌套结构
        elements = {
            'parent': HtmlElement('div', 'parent'),
            'child1': HtmlElement('p', 'child1'),
            'child2': HtmlElement('p', 'child2')
        }
        
        body = model.find_by_id('body')
        model.add_element(elements['parent'], body)
        model.add_element(elements['child1'], elements['parent'])
        model.add_element(elements['child2'], elements['parent'])
        
        # 验证初始结构
        assert len(elements['parent'].children) == 2
        
        # 移除中间元素
        model.remove_element('child1')
        
        # 验证结构更新
        assert len(elements['parent'].children) == 1
        assert elements['child2'] in elements['parent'].children
        
        # 清空父元素
        model.remove_element('parent')
        
        # 验证所有相关元素都被移除
        for id in elements:
            assert model.find_by_id(id) is None
            
    def test_element_attributes(self, model):
        """测试元素属性操作"""
        # 创建带属性的元素
        div = HtmlElement('div', 'test-div')
        div.attributes['class'] = 'test-class'
        div.attributes['data-test'] = 'test-value'
        
        body = model.find_by_id('body')
        model.add_element(div, body)
        
        # 验证属性
        found = model.find_by_id('test-div')
        assert found.attributes['class'] == 'test-class'
        assert found.attributes['data-test'] == 'test-value'
        
        # 修改属性
        found.attributes['class'] = 'updated-class'
        assert found.attributes['class'] == 'updated-class'
        
        # 删除属性
        del found.attributes['data-test']
        assert 'data-test' not in found.attributes
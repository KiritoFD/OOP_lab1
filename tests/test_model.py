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
        with pytest.raises(ElementNotFoundError):
            model.find_by_id('nonexistent')
        
    def test_add_element(self, model):
        """测试添加元素"""
        # 创建新元素
        div = HtmlElement('div', 'test-div')
        
        # 添加到body
        model.append_child('body', div)
        
        # 验证添加成功
        added_div = model.find_by_id('test-div')
        assert added_div is not None
        assert added_div.parent.id == 'body'
        assert added_div in model.find_by_id('body').children
        
    def test_add_duplicate_id(self, model):
        """测试添加重复ID的元素"""
        div1 = HtmlElement('div', 'test-div')
        div2 = HtmlElement('div', 'test-div')
        
        model.append_child('body', div1)
        
        # 尝试添加重复ID的元素
        with pytest.raises(DuplicateIdError):
            model.append_child('body', div2)
            
    def test_remove_element(self, model):
        """测试删除元素"""
        # 准备要删除的元素
        div = HtmlElement('div', 'test-div')
        model.append_child('body', div)
        
        # 执行删除
        try:
            model.delete_element('test-div')
        except:
            assert False, "删除元素失败"
        
        # 验证删除成功
        with pytest.raises(ElementNotFoundError):
            model.find_by_id('test-div')
        assert div not in model.find_by_id('body').children
        
    def test_remove_nonexistent_element(self, model):
        """测试删除不存在的元素"""
        with pytest.raises(ElementNotFoundError):
            model.delete_element('nonexistent')
        
    def test_remove_core_element(self, model):
        """测试删除核心元素（不应允许）"""
        core_elements = ['html', 'head', 'title', 'body']
        for id in core_elements:
            try:
                model.delete_element(id)
                assert False, f"删除核心元素'{id}'应该失败"
            except Exception:
                pass
            
    def test_element_hierarchy(self, model):
        """测试元素层级关系"""
        # 创建多层嵌套结构
        elements = [
            HtmlElement('div', 'parent'),
            HtmlElement('p', 'child1'),
            HtmlElement('span', 'child2'),
            HtmlElement('em', 'grandchild')
        ]
        
        model.append_child('body', elements[0])  # 添加父元素
        model.append_child('parent', elements[1])  # 添加第一个子元素
        model.append_child('parent', elements[2])  # 添加第二个子元素
        model.append_child('child2', elements[3])  # 添加孙元素
        
        # 验证层级关系
        parent = model.find_by_id('parent')
        child1 = model.find_by_id('child1')
        child2 = model.find_by_id('child2')
        grandchild = model.find_by_id('grandchild')

        assert parent.parent.id == 'body'
        assert child1.parent.id == 'parent'
        assert child2.parent.id == 'parent'
        assert grandchild.parent.id == 'child2'
        assert child1 in parent.children
        assert child2 in parent.children
        assert grandchild in child2.children
        
    def test_clear_model(self, model):
        """测试清空模型"""
        # 添加一些元素
        div = HtmlElement('div', 'test-div')
        p = HtmlElement('p', 'test-p')
        model.append_child('body', div)
        model.append_child('test-div', p)
        
        # 验证元素已添加
        assert model.find_by_id('test-div') is not None
        assert model.find_by_id('test-p') is not None
        
        # 清空模型
        model.clear()
        
        # 验证模型已清空
        with pytest.raises(ElementNotFoundError):
            model.find_by_id('test-div')
        with pytest.raises(ElementNotFoundError):
            model.find_by_id('test-p')
        
    def test_element_text(self, model):
        """测试元素文本操作"""
        # 创建带文本的元素
        p = HtmlElement('p', 'test-p')
        p.text = 'Test text'
        
        model.append_child('body', p)
        
        # 验证文本正确设置
        element = model.find_by_id('test-p')
        assert element.text == 'Test text'
        
        # 修改文本
        element.text = 'Updated text'
        assert element.text == 'Updated text'
        
        # 测试空文本
        element.text = ''
        assert element.text == ''
        
    def test_nested_operations(self, model):
        """测试嵌套元素的操作"""
        # 创建嵌套结构
        elements = {
            'parent': HtmlElement('div', 'parent'),
            'child1': HtmlElement('p', 'child1'),
            'child2': HtmlElement('p', 'child2')
        }

        model.append_child('body', elements['parent'])
        model.append_child('parent', elements['child1'])
        model.append_child('parent', elements['child2'])
        
        # 测试删除父元素级联删除所有子元素
        try:
            model.delete_element('parent')
        except:
            assert False, "删除元素失败"
        
        # 验证所有相关元素都被删除
        with pytest.raises(ElementNotFoundError):
            model.find_by_id('parent')
        with pytest.raises(ElementNotFoundError):
            model.find_by_id('child1')
        with pytest.raises(ElementNotFoundError):
            model.find_by_id('child2')
            
    def test_element_attributes(self, model):
        """测试元素属性操作"""
        # 创建带属性的元素
        div = HtmlElement('div', 'test-div')
        div.attributes['class'] = 'test-class'
        div.attributes['data-test'] = 'test-value'
        
        model.append_child('body', div)
        
        # 验证属性正确设置
        element = model.find_by_id('test-div')
        assert element.attributes['class'] == 'test-class'
        assert element.attributes['data-test'] == 'test-value'
        
        # 修改属性
        element.attributes['class'] = 'updated-class'
        assert element.attributes['class'] == 'updated-class'
        
        # 添加新属性
        element.attributes['new-attr'] = 'new-value'
        assert element.attributes['new-attr'] == 'new-value'
        
        # 删除属性
        del element.attributes['data-test']
        assert 'data-test' not in element.attributes
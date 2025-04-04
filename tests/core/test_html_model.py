import pytest
from src.core.html_model import HtmlModel
from src.core.element import HtmlElement
from src.core.exceptions import ElementNotFoundError, DuplicateIdError, IdCollisionError

class TestHtmlModel:
    """测试HTML模型类"""
    
    @pytest.fixture
    def model(self):
        """创建基本的HTML模型"""
        return HtmlModel()
    
    @pytest.fixture
    def populated_model(self):
        """创建包含多个元素的HTML模型"""
        model = HtmlModel()
        
        # 添加一些元素
        model.append_child('body', 'div', 'container')
        model.append_child('container', 'p', 'para1', 'Paragraph 1')
        model.append_child('container', 'p', 'para2', 'Paragraph 2')
        model.append_child('container', 'div', 'nested-div')
        model.append_child('nested-div', 'span', 'nested-span', 'Nested span text')
        
        return model
        
    def test_init_creates_basic_structure(self, model):
        """测试初始化创建基本结构"""
        # 验证基本元素存在
        assert model.root is not None
        assert model.root.tag == 'html'
        assert model.root.id == 'html'
        
        # 验证head和body元素
        assert model.find_by_id('head') is not None
        assert model.find_by_id('body') is not None
        
        # 验证父子关系
        head = model.find_by_id('head')
        body = model.find_by_id('body')
        assert head.parent == model.root
        assert body.parent == model.root
        
        # 验证ID映射
        assert model._id_map['html'] is model.root
        assert model._id_map['head'] is head
        assert model._id_map['body'] is body
    
    def test_find_by_id_existing(self, populated_model):
        """测试查找存在的元素ID"""
        model = populated_model
        
        # 查找各层级的元素
        container = model.find_by_id('container')
        para1 = model.find_by_id('para1')
        nested_span = model.find_by_id('nested-span')
        
        assert container is not None
        assert container.tag == 'div'
        
        assert para1 is not None
        assert para1.tag == 'p'
        assert para1.text == 'Paragraph 1'
        
        assert nested_span is not None
        assert nested_span.tag == 'span'
        assert nested_span.text == 'Nested span text'
    
    def test_find_by_id_nonexistent(self, model):
        """测试查找不存在的元素ID"""
        with pytest.raises(ElementNotFoundError) as excinfo:
            model.find_by_id('nonexistent')
            
        assert "未找到ID为 'nonexistent' 的元素" in str(excinfo.value)
    
    def test_register_id_duplicate(self, model):
        """测试注册重复ID"""
        # 创建一个与已存在ID重复的元素
        duplicate_element = HtmlElement('div', 'body')  # 'body' ID已存在
        
        with pytest.raises(DuplicateIdError) as excinfo:
            model._register_id(duplicate_element)
            
        assert "ID 'body' 已存在" in str(excinfo.value)
    
    def test_unregister_id(self, populated_model):
        """测试注销ID"""
        model = populated_model
        element = model.find_by_id('para1')
        
        # 注销ID
        model._unregister_id(element)
        
        # 验证ID已从映射中移除
        assert 'para1' not in model._id_map
        
        # 验证无法通过ID找到元素
        with pytest.raises(ElementNotFoundError):
            model.find_by_id('para1')
    
    def test_unregister_nonexistent_id(self, model):
        """测试注销不存在的ID"""
        # 创建一个未注册的元素
        element = HtmlElement('div', 'unregistered')
        
        # 注销不存在的ID不应引发异常
        model._unregister_id(element)
    
    def test_insert_before(self, populated_model):
        """测试在指定元素前插入新元素"""
        model = populated_model
        
        # 在para2前插入新元素
        new_element = HtmlElement('p', 'new-para')
        model.insert_before('para2', new_element)
        
        # 验证新元素已插入
        container = model.find_by_id('container')
        assert new_element in container.children
        
        # 验证元素顺序
        assert container.children.index(new_element) < container.children.index(model.find_by_id('para2'))
    
    def test_insert_before_nonexistent_target(self, model):
        """测试在不存在的目标元素前插入"""
        new_element = HtmlElement('div', 'new-div')
        
        with pytest.raises(ElementNotFoundError):
            model.insert_before('nonexistent', new_element)
    
    def test_insert_before_with_duplicate_id(self, populated_model):
        """测试插入ID重复的元素"""
        model = populated_model
        
        # 创建ID重复的元素
        duplicate_element = HtmlElement('p', 'para1')
        
        with pytest.raises(DuplicateIdError):
            model.insert_before('para2', duplicate_element)
    
    def test_cleanup_after_failed_insert(self, populated_model):
        """测试失败插入后的清理"""
        model = populated_model
        element = HtmlElement('p', 'cleanup-test')
        parent = model.find_by_id('container')
        
        # 模拟元素已添加到模型和父元素
        model._id_map[element.id] = element
        parent.children.append(element)
        element.parent = parent
        
        # 执行清理
        model._cleanup_after_failed_insert(element, parent)
        
        # 验证清理结果
        assert element.id not in model._id_map
        assert element not in parent.children
        assert element.parent is None
    
    def test_register_subtree_ids(self, model):
        """测试递归注册子树IDs"""
        # 创建一个有嵌套结构的子树，但不添加到模型
        root = HtmlElement('div', 'subtree-root')
        child1 = HtmlElement('p', 'subtree-child1')
        child2 = HtmlElement('span', 'subtree-child2')
        grandchild = HtmlElement('a', 'subtree-grandchild')
        
        root.add_child(child1)
        root.add_child(child2)
        child2.add_child(grandchild)
        
        # 注册子树
        model._register_subtree_ids(root)
        
        # 验证所有ID都已注册
        assert 'subtree-child1' in model._id_map
        assert 'subtree-child2' in model._id_map
        assert 'subtree-grandchild' in model._id_map
        
        # 验证映射正确
        assert model._id_map['subtree-child1'] is child1
        assert model._id_map['subtree-child2'] is child2
        assert model._id_map['subtree-grandchild'] is grandchild
    
    def test_append_child_success(self, model):
        """测试成功追加子元素"""
        # 添加一个子元素
        new_element = model.append_child('body', 'div', 'test-div', 'Test content')
        
        # 验证元素已添加
        assert new_element is not None
        assert new_element.tag == 'div'
        assert new_element.id == 'test-div'
        assert new_element.text == 'Test content'
        
        # 验证父子关系
        body = model.find_by_id('body')
        assert new_element in body.children
        assert new_element.parent is body
        
        # 验证ID已注册
        assert 'test-div' in model._id_map
        assert model._id_map['test-div'] is new_element
    
    def test_append_child_nonexistent_parent(self, model):
        """测试向不存在的父元素添加子元素"""
        with pytest.raises(ElementNotFoundError):
            model.append_child('nonexistent', 'div', 'test-div')
    
    def test_append_child_duplicate_id(self, model):
        """测试添加ID重复的子元素"""
        # 先添加一个元素
        model.append_child('body', 'div', 'test-div')
        
        # 尝试添加ID重复的元素
        with pytest.raises(DuplicateIdError):
            model.append_child('body', 'p', 'test-div')
    
    def test_delete_element_success(self, populated_model):
        """测试成功删除元素"""
        model = populated_model
        
        # 删除元素
        result = model.delete_element('para1')
        
        # 验证删除成功
        assert result is True
        
        # 验证元素已从模型中移除
        with pytest.raises(ElementNotFoundError):
            model.find_by_id('para1')
            
        # 验证元素已从父元素的子元素列表中移除
        container = model.find_by_id('container')
        for child in container.children:
            assert child.id != 'para1'
    
    def test_delete_element_with_children(self, populated_model):
        """测试删除带有子元素的元素"""
        model = populated_model
        
        # 删除带有子元素的元素
        result = model.delete_element('nested-div')
        
        # 验证删除成功
        assert result is True
        
        # 验证元素及其子元素都已从模型中移除
        with pytest.raises(ElementNotFoundError):
            model.find_by_id('nested-div')
            
        with pytest.raises(ElementNotFoundError):
            model.find_by_id('nested-span')
    
    def test_delete_nonexistent_element(self, model):
        """测试删除不存在的元素"""
        result = model.delete_element('nonexistent')
        
        # 应返回False表示删除失败
        assert result is False
    
    def test_delete_root_element(self, model):
        """测试删除根元素"""
        # 尝试删除根元素，应返回False
        result = model.delete_element('html')
        assert result is False
    
    def test_unregister_subtree_ids(self, populated_model):
        """测试递归注销子树IDs"""
        model = populated_model
        nested_div = model.find_by_id('nested-div')
        
        # 在注销前确认IDs存在
        assert 'nested-div' in model._id_map
        assert 'nested-span' in model._id_map
        
        # 注销子树
        model._unregister_subtree_ids(nested_div)
        
        # 验证所有ID都已注销
        assert 'nested-div' not in model._id_map
        assert 'nested-span' not in model._id_map
    
    def test_replace_content(self, populated_model):
        """测试替换整个文档内容"""
        model = populated_model
        
        # 创建新的根元素及其子树
        new_root = HtmlElement('html', 'new-html')
        new_head = HtmlElement('head', 'new-head')
        new_body = HtmlElement('body', 'new-body')
        new_div = HtmlElement('div', 'new-div')
        
        new_root.add_child(new_head)
        new_root.add_child(new_body)
        new_body.add_child(new_div)
        
        # 替换内容
        model.replace_content(new_root)
        
        # 验证模型已更新
        assert model.root is new_root
        
        # 验证旧ID已移除
        with pytest.raises(ElementNotFoundError):
            model.find_by_id('container')
            
        with pytest.raises(ElementNotFoundError):
            model.find_by_id('para1')
            
        # 验证新ID已注册
        assert model.find_by_id('new-html') is new_root
        assert model.find_by_id('new-head') is new_head
        assert model.find_by_id('new-body') is new_body
        assert model.find_by_id('new-div') is new_div
    
    def test_update_element_id_success(self, populated_model):
        """测试成功更新元素ID"""
        model = populated_model
        
        # 更新ID
        model.update_element_id('para1', 'updated-para')
        
        # 验证ID已更新
        element = model.find_by_id('updated-para')
        assert element is not None
        assert element.text == 'Paragraph 1'
        
        # 验证旧ID不再存在
        with pytest.raises(ElementNotFoundError):
            model.find_by_id('para1')
    
    def test_update_element_id_nonexistent(self, model):
        """测试更新不存在的元素ID"""
        with pytest.raises(ElementNotFoundError):
            model.update_element_id('nonexistent', 'new-id')
    
    def test_update_element_id_collision(self, populated_model):
        """测试更新为已存在的ID"""
        model = populated_model
        
        with pytest.raises(IdCollisionError):
            model.update_element_id('para1', 'para2')
    
    def test_update_element_id_same_id(self, populated_model):
        """测试更新为相同的ID"""
        model = populated_model
        
        # 更新为相同ID应该不执行任何操作
        model.update_element_id('para1', 'para1')
        
        # 验证元素仍然存在且未变化
        element = model.find_by_id('para1')
        assert element is not None
        assert element.text == 'Paragraph 1'

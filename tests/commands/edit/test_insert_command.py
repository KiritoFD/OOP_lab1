import pytest
from src.core.html_model import HtmlModel
from src.commands.edit.insert_command import InsertCommand
from src.commands.base import CommandProcessor
from src.core.exceptions import DuplicateIdError, ElementNotFoundError

class TestInsertCommand:
    @pytest.fixture
    def model(self):
        return HtmlModel()
    
    @pytest.fixture
    def processor(self):
        return CommandProcessor()
    
    def test_insert_success(self, model, processor):
        """测试成功插入元素"""
        cmd = InsertCommand(model, 'div', 'test-div', 'body')
        
        # 执行命令
        assert processor.execute(cmd) is True
        
        # 验证插入结果
        element = model.find_by_id('test-div')
        assert element is not None
        assert element.tag == 'div'
        assert element.id == 'test-div'
        assert element.parent == model.find_by_id('html')
        
    def test_insert_with_text(self, model, processor):
        """测试插入带文本的元素"""
        cmd = InsertCommand(model, 'p', 'test-p', 'body', 'Hello World')
        
        # 执行命令
        assert processor.execute(cmd) is True
        
        # 验证文本内容
        element = model.find_by_id('test-p')
        assert element is not None
        assert element.text == 'Hello World'
        
    def test_insert_duplicate_id(self, model, processor):
        """测试插入重复ID"""
        # 先插入一个元素
        cmd1 = InsertCommand(model, 'div', 'test-div', 'body')
        processor.execute(cmd1)
        
        # 尝试插入相同ID的元素
        cmd2 = InsertCommand(model, 'p', 'test-div', 'body')
        with pytest.raises(DuplicateIdError):
            processor.execute(cmd2)
            
    def test_insert_invalid_location(self, model, processor):
        """测试插入到不存在的位置"""
        cmd = InsertCommand(model, 'div', 'test-div', 'nonexistent')
        with pytest.raises(ElementNotFoundError):
            processor.execute(cmd)
            
    def test_insert_undo(self, model, processor):
        """测试插入命令的撤销"""
        cmd = InsertCommand(model, 'div', 'test-div', 'body')
        processor.execute(cmd)
        
        # 执行撤销
        assert processor.undo() is True
        
        # 验证元素被删除
        assert model.find_by_id('test-div') is None
        
    def test_insert_redo(self, model, processor):
        """测试插入命令的重做"""
        cmd = InsertCommand(model, 'div', 'test-div', 'body')
        processor.execute(cmd)
        processor.undo()
        
        # 执行重做
        assert processor.redo() is True
        
        # 验证元素重新插入
        element = model.find_by_id('test-div')
        assert element is not None
        assert element.tag == 'div'
        
    def test_insert_sequence(self, model, processor):
        """测试多个插入命令的序列"""
        cmd1 = InsertCommand(model, 'div', 'div1', 'body')
        cmd2 = InsertCommand(model, 'div', 'div2', 'body')
        
        # 执行命令序列
        processor.execute(cmd1)
        processor.execute(cmd2)
        
        # 验证顺序
        body = model.find_by_id('body')
        children_ids = [child.id for child in body.parent.children]
        assert children_ids.index('div1') < children_ids.index('div2')
        
        # 撤销一个命令
        processor.undo()
        assert model.find_by_id('div2') is None
        assert model.find_by_id('div1') is not None

    def test_insert_at_beginning(self, model, processor):
        """测试在头部插入元素"""
        # 先插入一个元素作为参考
        cmd1 = InsertCommand(model, 'div', 'div1', 'body')
        processor.execute(cmd1)
        
        # 在div1之前插入新元素
        cmd2 = InsertCommand(model, 'p', 'p1', 'div1')
        processor.execute(cmd2)
        
        # 验证p1在div1之前
        html = model.root
        body_children = [child for child in html.children if child.tag == 'body'][0].parent.children
        element_ids = [e.id for e in body_children]
        assert 'p1' in element_ids
        assert 'div1' in element_ids
        assert element_ids.index('p1') < element_ids.index('div1')
        
    def test_insert_nested_elements(self, model, processor):
        """测试嵌套插入元素"""
        # 创建嵌套结构
        cmd1 = InsertCommand(model, 'div', 'outer', 'body')
        cmd2 = InsertCommand(model, 'div', 'inner', 'outer')
        cmd3 = InsertCommand(model, 'p', 'content', 'inner', 'Nested content')
    
        # 执行命令
        processor.execute(cmd1)
        processor.execute(cmd2)
        processor.execute(cmd3)
    
        # 验证嵌套结构
        outer = model.find_by_id('outer')
        inner = model.find_by_id('inner')
        content = model.find_by_id('content')
    
        # 验证父子关系
        assert outer is not None, "Outer element should exist"
        assert inner is not None, "Inner element should exist"
        assert content is not None, "Content element should exist"
        
        assert inner.parent == outer, "Inner's parent should be Outer"
        assert content.parent == inner, "Content's parent should be Inner"
        
        # 验证文本内容
        assert content.text == 'Nested content', "Content's text should match"
        
    def test_insert_empty_id(self, model, processor):
        """测试使用空ID插入"""
        cmd = InsertCommand(model, 'div', '', 'body')
        with pytest.raises(ValueError):
            processor.execute(cmd)
            
    def test_insert_empty_tag(self, model, processor):
        """测试使用空标签插入"""
        cmd = InsertCommand(model, '', 'test-div', 'body')
        with pytest.raises(ValueError):
            processor.execute(cmd)
            
    def test_insert_complex_text(self, model, processor):
        """测试插入包含特殊字符的文本"""
        special_text = "Text with <html> tags & special 'chars' and \"quotes\""
        cmd = InsertCommand(model, 'p', 'special', 'body', special_text)
        
        # 执行命令
        assert processor.execute(cmd) is True
        
        # 验证文本保持不变
        element = model.find_by_id('special')
        assert element.text == special_text

    def test_multiple_undo_redo(self, model, processor):
        """测试多次撤销和重做"""
        cmd1 = InsertCommand(model, 'div', 'div1', 'body')
        cmd2 = InsertCommand(model, 'p', 'p1', 'body')
        cmd3 = InsertCommand(model, 'span', 'span1', 'body')
        
        # 执行所有命令
        processor.execute(cmd1)
        processor.execute(cmd2)
        processor.execute(cmd3)
        
        # 验证所有元素都存在
        assert model.find_by_id('div1') is not None
        assert model.find_by_id('p1') is not None
        assert model.find_by_id('span1') is not None
        
        # 撤销全部命令
        assert processor.undo() is True  # 撤销span1
        assert model.find_by_id('span1') is None
        
        assert processor.undo() is True  # 撤销p1
        assert model.find_by_id('p1') is None
        
        assert processor.undo() is True  # 撤销div1
        assert model.find_by_id('div1') is None
        
        # 已经没有可撤销的命令
        assert processor.undo() is False
        
        # 重做全部命令
        assert processor.redo() is True  # 重做div1
        assert model.find_by_id('div1') is not None
        
        assert processor.redo() is True  # 重做p1
        assert model.find_by_id('p1') is not None
        
        assert processor.redo() is True  # 重做span1
        assert model.find_by_id('span1') is not None
        
        # 已经没有可重做的命令
        assert processor.redo() is False
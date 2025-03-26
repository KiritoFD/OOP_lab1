import pytest
from src.core.html_model import HtmlModel
from src.commands.edit_commands import InsertCommand
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
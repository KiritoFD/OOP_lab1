import pytest
from src.core.html_model import HtmlModel
from src.commands.edit_commands import AppendCommand
from src.commands.base import CommandProcessor
from src.core.exceptions import DuplicateIdError, ElementNotFoundError

class TestAppendCommand:
    @pytest.fixture
    def model(self):
        return HtmlModel()
    
    @pytest.fixture
    def processor(self):
        return CommandProcessor()
    
    def test_append_success(self, model, processor):
        """测试成功追加子元素"""
        cmd = AppendCommand(model, 'div', 'test-div', 'body')
        
        # 执行命令
        assert processor.execute(cmd) is True
        
        # 验证追加结果
        element = model.find_by_id('test-div')
        assert element is not None
        assert element.tag == 'div'
        assert element.id == 'test-div'
        assert element.parent == model.find_by_id('body')
        assert element in model.find_by_id('body').children
        
    def test_append_with_text(self, model, processor):
        """测试追加带文本的元素"""
        cmd = AppendCommand(model, 'p', 'test-p', 'body', 'Hello World')
        
        # 执行命令
        assert processor.execute(cmd) is True
        
        # 验证文本内容
        element = model.find_by_id('test-p')
        assert element is not None
        assert element.text == 'Hello World'
        
    def test_append_duplicate_id(self, model, processor):
        """测试追加重复ID的元素"""
        # 先追加一个元素
        cmd1 = AppendCommand(model, 'div', 'test-div', 'body')
        processor.execute(cmd1)
        
        # 尝试追加相同ID的元素
        cmd2 = AppendCommand(model, 'p', 'test-div', 'body')
        with pytest.raises(DuplicateIdError):
            processor.execute(cmd2)
            
    def test_append_invalid_parent(self, model, processor):
        """测试追加到不存在的父元素"""
        cmd = AppendCommand(model, 'div', 'test-div', 'nonexistent')
        with pytest.raises(ElementNotFoundError):
            processor.execute(cmd)
            
    def test_append_nested(self, model, processor):
        """测试嵌套追加"""
        # 创建父元素
        cmd1 = AppendCommand(model, 'div', 'parent', 'body')
        processor.execute(cmd1)
        
        # 在父元素中追加子元素
        cmd2 = AppendCommand(model, 'p', 'child', 'parent')
        processor.execute(cmd2)
        
        # 验证嵌套结构
        parent = model.find_by_id('parent')
        child = model.find_by_id('child')
        assert child in parent.children
        assert child.parent == parent
            
    def test_append_undo(self, model, processor):
        """测试追加命令的撤销"""
        cmd = AppendCommand(model, 'div', 'test-div', 'body')
        processor.execute(cmd)
        
        # 执行撤销
        assert processor.undo() is True
        
        # 验证元素被删除
        assert model.find_by_id('test-div') is None
        assert 'test-div' not in [child.id for child in model.find_by_id('body').children]
        
    def test_append_redo(self, model, processor):
        """测试追加命令的重做"""
        cmd = AppendCommand(model, 'div', 'test-div', 'body')
        processor.execute(cmd)
        processor.undo()
        
        # 执行重做
        assert processor.redo() is True
        
        # 验证元素重新追加
        element = model.find_by_id('test-div')
        assert element is not None
        assert element.tag == 'div'
        assert element in model.find_by_id('body').children
        
    def test_append_sequence(self, model, processor):
        """测试多个追加命令的序列"""
        cmd1 = AppendCommand(model, 'div', 'div1', 'body')
        cmd2 = AppendCommand(model, 'div', 'div2', 'body')
        
        # 执行命令序列
        processor.execute(cmd1)
        processor.execute(cmd2)
        
        # 验证追加顺序
        body = model.find_by_id('body')
        children = body.children
        assert children[-2].id == 'div1'
        assert children[-1].id == 'div2'
        
        # 撤销一个命令
        processor.undo()
        assert model.find_by_id('div2') is None
        assert model.find_by_id('div1') is not None
        assert body.children[-1].id == 'div1'
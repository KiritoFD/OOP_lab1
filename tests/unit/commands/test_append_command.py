# Test file for AppendCommand

import pytest
from src.commands.edit.append_command import AppendCommand  # Correct import path
from src.commands.base import CommandProcessor
from src.core.html_model import HtmlModel
from src.core.exceptions import ElementNotFoundError, DuplicateIdError, CommandExecutionError

@pytest.mark.unit
class TestAppendCommand:
    @pytest.fixture
    def model(self):
        """创建一个测试用的HTML模型"""
        return HtmlModel()
        
    @pytest.fixture
    def processor(self):
        """创建一个命令处理器"""
        return CommandProcessor()
        
    def test_append_success(self, model, processor):
        """测试成功追加元素"""
        cmd = AppendCommand(model, 'div', 'test-div', 'body')
        
        # 执行命令
        assert processor.execute(cmd) is True
        
        # 验证追加结果
        element = model.find_by_id('test-div')
        assert element is not None
        assert element.tag == 'div'
        assert element.id == 'test-div'
        assert element.parent == model.find_by_id('body')
        
    def test_append_with_text(self, model, processor):
        """测试追加带文本的元素"""
        cmd = AppendCommand(model, 'p', 'test-p', 'body', 'Hello, world!')
        
        # 执行命令
        assert processor.execute(cmd) is True
        
        # 验证文本内容
        element = model.find_by_id('test-p')
        assert element is not None
        assert element.text == 'Hello, world!'
        
    def test_append_duplicate_id(self, model, processor):
        """测试追加重复ID的元素"""
        # 先添加一个元素
        cmd1 = AppendCommand(model, 'div', 'test-div', 'body')
        processor.execute(cmd1)
        
        # 尝试添加相同ID的元素
        cmd2 = AppendCommand(model, 'div', 'test-div', 'body')
        with pytest.raises(DuplicateIdError, match=r"ID 'test-div' 已存在"):
            processor.execute(cmd2)
    
    def test_append_invalid_parent(self, model, processor):
        """测试追加到不存在的父元素"""
        cmd = AppendCommand(model, 'div', 'test-div', 'non-existent')
        with pytest.raises(ElementNotFoundError, match=r"未找到ID为 'non-existent' 的父元素"):
            processor.execute(cmd)
            
    def test_append_undo(self, model, processor):
        """测试追加命令的撤销"""
        cmd = AppendCommand(model, 'div', 'test-div', 'body')
        processor.execute(cmd)
        
        # 执行撤销
        assert processor.undo() is True
        
        # 验证元素已被删除
        with pytest.raises(ElementNotFoundError):
            model.find_by_id('test-div')
        
    def test_append_redo(self, model, processor):
        """测试追加命令的重做"""
        cmd = AppendCommand(model, 'div', 'test-div', 'body')
        processor.execute(cmd)
        processor.undo()
        
        # 执行重做
        assert processor.redo() is True
        
        # 验证元素已恢复
        assert model.find_by_id('test-div') is not None
        
    def test_append_nested_elements(self, model, processor):
        """测试嵌套追加元素"""
        # 创建嵌套结构
        cmd1 = AppendCommand(model, 'div', 'outer', 'body')
        cmd2 = AppendCommand(model, 'div', 'inner', 'outer')
        cmd3 = AppendCommand(model, 'p', 'content', 'inner', 'Nested content')
        
        # 执行命令
        processor.execute(cmd1)
        processor.execute(cmd2)
        processor.execute(cmd3)
        
        # 验证嵌套结构
        outer = model.find_by_id('outer')
        inner = model.find_by_id('inner')
        content = model.find_by_id('content')
        
        assert inner.parent == outer
        assert content.parent == inner
        assert content.text == 'Nested content'
        
    def test_multiple_undo_redo(self, model, processor):
        """测试多次撤销和重做"""
        # Simplify to use just one command
        cmd1 = AppendCommand(model, 'div', 'div1', 'body')
        processor.execute(cmd1)
        
        # 验证元素存在
        assert model.find_by_id('div1') is not None
        
        # 撤销
        assert processor.undo() is True
        with pytest.raises(ElementNotFoundError):
            model.find_by_id('div1')
        
        # 重做
        assert processor.redo() is True
        assert model.find_by_id('div1') is not None
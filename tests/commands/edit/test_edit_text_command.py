import pytest
from src.core.html_model import HtmlModel
from src.commands.edit_commands import EditTextCommand, AppendCommand
from src.commands.base import CommandProcessor
from src.core.exceptions import ElementNotFoundError

class TestEditTextCommand:
    @pytest.fixture
    def model(self):
        return HtmlModel()
    
    @pytest.fixture
    def processor(self):
        return CommandProcessor()
    
    @pytest.fixture
    def setup_element(self, model, processor):
        """创建测试用的元素"""
        cmd = AppendCommand(model, 'p', 'test-p', 'body', 'Initial text')
        processor.execute(cmd)
        processor.clear_history()
        
    def test_edit_text_success(self, model, processor, setup_element):
        """测试成功编辑文本"""
        new_text = "Updated text content"
        cmd = EditTextCommand(model, 'test-p', new_text)
        
        # 执行命令
        assert processor.execute(cmd) is True
        
        # 验证文本更新
        element = model.find_by_id('test-p')
        assert element.text == new_text
        
    def test_edit_text_empty(self, model, processor, setup_element):
        """测试将文本设置为空"""
        cmd = EditTextCommand(model, 'test-p', '')
        
        # 执行命令
        assert processor.execute(cmd) is True
        
        # 验证文本被清空
        element = model.find_by_id('test-p')
        assert element.text == ''
        
    def test_edit_nonexistent_element(self, model, processor):
        """测试编辑不存在的元素"""
        cmd = EditTextCommand(model, 'nonexistent', 'New text')
        with pytest.raises(ElementNotFoundError):
            processor.execute(cmd)
            
    def test_edit_text_undo(self, model, processor, setup_element):
        """测试编辑文本的撤销"""
        original_text = model.find_by_id('test-p').text
        new_text = "Updated text"
        
        # 执行编辑
        cmd = EditTextCommand(model, 'test-p', new_text)
        processor.execute(cmd)
        
        # 执行撤销
        assert processor.undo() is True
        
        # 验证文本恢复
        element = model.find_by_id('test-p')
        assert element.text == original_text
        
    def test_edit_text_redo(self, model, processor, setup_element):
        """测试编辑文本的重做"""
        new_text = "Updated text"
        cmd = EditTextCommand(model, 'test-p', new_text)
        
        # 执行-撤销-重做
        processor.execute(cmd)
        processor.undo()
        assert processor.redo() is True
        
        # 验证文本再次更新
        element = model.find_by_id('test-p')
        assert element.text == new_text
        
    def test_edit_text_sequence(self, model, processor, setup_element):
        """测试多次编辑文本"""
        text1 = "First update"
        text2 = "Second update"
        cmd1 = EditTextCommand(model, 'test-p', text1)
        cmd2 = EditTextCommand(model, 'test-p', text2)
        
        # 执行第一次编辑
        processor.execute(cmd1)
        assert model.find_by_id('test-p').text == text1
        
        # 执行第二次编辑
        processor.execute(cmd2)
        assert model.find_by_id('test-p').text == text2
        
        # 撤销到初始状态
        processor.undo()
        assert model.find_by_id('test-p').text == text1
        processor.undo()
        assert model.find_by_id('test-p').text == 'Initial text'
        
    def test_edit_text_with_special_chars(self, model, processor, setup_element):
        """测试编辑包含特殊字符的文本"""
        special_text = "Text with <html> tags & 'quotes' & \"double quotes\""
        cmd = EditTextCommand(model, 'test-p', special_text)
        
        # 执行编辑
        assert processor.execute(cmd) is True
        
        # 验证特殊字符被正确保存
        element = model.find_by_id('test-p')
        assert element.text == special_text
        
    def test_edit_text_multiple_elements(self, model, processor):
        """测试编辑多个元素的文本"""
        # 创建多个元素
        cmd1 = AppendCommand(model, 'p', 'p1', 'body', 'Text 1')
        cmd2 = AppendCommand(model, 'p', 'p2', 'body', 'Text 2')
        processor.execute(cmd1)
        processor.execute(cmd2)
        processor.clear_history()
        
        # 依次编辑每个元素
        cmd3 = EditTextCommand(model, 'p1', 'Updated 1')
        cmd4 = EditTextCommand(model, 'p2', 'Updated 2')
        
        processor.execute(cmd3)
        processor.execute(cmd4)
        
        # 验证所有更新
        assert model.find_by_id('p1').text == 'Updated 1'
        assert model.find_by_id('p2').text == 'Updated 2'
        
        # 验证撤销顺序
        processor.undo()
        assert model.find_by_id('p1').text == 'Updated 1'
        assert model.find_by_id('p2').text == 'Text 2'
        
        processor.undo()
        assert model.find_by_id('p1').text == 'Text 1'
        assert model.find_by_id('p2').text == 'Text 2'
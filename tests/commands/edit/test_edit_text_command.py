import pytest
from src.commands.edit.edit_text_command import EditTextCommand  # Correct import path
from src.commands.edit.append_command import AppendCommand  # Correct import path
from src.commands.base import CommandProcessor
from src.core.html_model import HtmlModel
from src.core.exceptions import ElementNotFoundError

class TestEditTextCommand:
    @pytest.fixture
    def model(self):
        """创建一个测试用的HTML模型"""
        return HtmlModel()
        
    @pytest.fixture
    def processor(self):
        """创建一个命令处理器"""
        return CommandProcessor()
    
    @pytest.fixture
    def setup_elements(self, model, processor):
        """设置测试用的元素"""
        # 添加一些元素用于测试编辑文本
        cmd1 = AppendCommand(model, 'div', 'test-div', 'body')
        cmd2 = AppendCommand(model, 'p', 'test-p', 'body', '原始文本')
        cmd3 = AppendCommand(model, 'span', 'test-span', 'test-div', 'Hello World')
        
        processor.execute(cmd1)
        processor.execute(cmd2)
        processor.execute(cmd3)
        
        return model
        
    def test_edit_text_success(self, model, processor, setup_elements):
        """测试成功编辑元素文本"""
        # 编辑test-p元素的文本
        cmd = EditTextCommand(model, 'test-p', '新文本内容')
        
        # 执行编辑命令
        assert processor.execute(cmd) is True
        
        # 验证文本已更新
        element = model.find_by_id('test-p')
        assert element.text == '新文本内容'
        
    def test_edit_text_nonexistent(self, model, processor):
        """测试编辑不存在元素的文本"""
        cmd = EditTextCommand(model, 'non-existent', '测试文本')
        
        # 应抛出异常
        with pytest.raises(ElementNotFoundError):
            processor.execute(cmd)
            
    def test_edit_text_empty(self, model, processor, setup_elements):
        """测试设置空文本"""
        cmd = EditTextCommand(model, 'test-p', '')
        
        # 执行编辑命令
        assert processor.execute(cmd) is True
        
        # 验证文本已更新为空
        element = model.find_by_id('test-p')
        assert element.text == ''
        
    def test_edit_text_undo(self, model, processor, setup_elements):
        """测试编辑文本的撤销操作"""
        # 记录原始文本
        original_text = model.find_by_id('test-p').text
        
        # 编辑文本
        cmd = EditTextCommand(model, 'test-p', '新文本内容')
        processor.execute(cmd)
        
        # 验证文本已更新
        assert model.find_by_id('test-p').text == '新文本内容'
        
        # 执行撤销
        assert processor.undo() is True
        
        # 验证文本已恢复
        assert model.find_by_id('test-p').text == original_text
        
    def test_edit_text_redo(self, model, processor, setup_elements):
        """测试编辑文本的重做操作"""
        # 编辑文本
        cmd = EditTextCommand(model, 'test-p', '新文本内容')
        processor.execute(cmd)
        
        # 撤销编辑
        processor.undo()
        assert model.find_by_id('test-p').text == '原始文本'
        
        # 重做编辑
        assert processor.redo() is True
        assert model.find_by_id('test-p').text == '新文本内容'
        
    def test_multiple_edits(self, model, processor, setup_elements):
        """测试多次编辑同一元素的文本"""
        # 第一次编辑
        cmd1 = EditTextCommand(model, 'test-p', '文本1')
        processor.execute(cmd1)
        assert model.find_by_id('test-p').text == '文本1'
        
        # 第二次编辑
        cmd2 = EditTextCommand(model, 'test-p', '文本2')
        processor.execute(cmd2)
        assert model.find_by_id('test-p').text == '文本2'
        
        # 撤销第二次编辑
        processor.undo()
        assert model.find_by_id('test-p').text == '文本1'
        
        # 撤销第一次编辑
        processor.undo()
        assert model.find_by_id('test-p').text == '原始文本'
        
    def test_edit_special_chars(self, model, processor, setup_elements):
        """测试编辑包含特殊字符的文本"""
        special_text = '特殊!@#$%^&*()_+-={}[]|\\:;"\'<>,.?/字符'
        cmd = EditTextCommand(model, 'test-p', special_text)
        
        # 执行编辑命令
        assert processor.execute(cmd) is True
        
        # 验证特殊字符文本已正确设置
        element = model.find_by_id('test-p')
        assert element.text == special_text
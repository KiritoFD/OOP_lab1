import pytest
from src.commands.edit.delete_command import DeleteCommand
from src.commands.edit.append_command import AppendCommand
from src.commands.io import InitCommand
from src.commands.base import CommandProcessor
from src.core.html_model import HtmlModel
from src.core.exceptions import ElementNotFoundError
from src.commands.command_exceptions import CommandExecutionError

class TestDeleteCommand:
    @pytest.fixture
    def model(self):
        return HtmlModel()
    
    @pytest.fixture
    def processor(self):
        return CommandProcessor()
    
    @pytest.fixture
    def setup_elements(self, model, processor):
        """设置带测试元素的模型"""
        # 初始化模型
        processor.execute(InitCommand(model))
        
        # 创建测试元素
        processor.execute(AppendCommand(model, 'div', 'test-div', 'body'))
        processor.execute(AppendCommand(model, 'p', 'test-p', 'body'))
        processor.execute(AppendCommand(model, 'span', 'test-span', 'test-div'))
        return model
    
    def test_delete_success(self, model, processor, setup_elements):
        """测试成功删除元素"""
        # 验证元素存在
        assert model.find_by_id('test-div') is not None
        
        # 执行删除
        cmd = DeleteCommand(model, 'test-div')
        assert processor.execute(cmd) is True
        
        # 验证元素已删除 - 使用try/except处理
        try:
            model.find_by_id('test-div')
            assert False, "元素应该已经被删除"
        except ElementNotFoundError:
            # 预期异常
            pass
        
        # 验证子元素也被删除
        try:
            model.find_by_id('test-span')
            assert False, "子元素应该也被删除"
        except ElementNotFoundError:
            # 预期异常
            pass
    
    def test_delete_nonexistent(self, model, processor):
        """测试删除不存在的元素"""
        cmd = DeleteCommand(model, 'non-existent')
        
        # 期待CommandExecutionError而不是ElementNotFoundError
        with pytest.raises(CommandExecutionError) as excinfo:
            processor.execute(cmd)
        # 验证错误消息包含预期内容
        assert "未找到" in str(excinfo.value) or "not found" in str(excinfo.value).lower()
    
    def test_delete_special_element(self, model, processor):
        """测试删除特殊元素"""
        # 初始化模型
        processor.execute(InitCommand(model))
        
        # 尝试删除body元素
        cmd = DeleteCommand(model, 'body')
        
        # 期待CommandExecutionError
        with pytest.raises(CommandExecutionError) as excinfo:
            processor.execute(cmd)
        # 验证错误消息包含预期内容
        assert "无法删除特殊元素" in str(excinfo.value) or "special element" in str(excinfo.value).lower()
    
    def test_delete_undo(self, model, processor, setup_elements):
        """测试删除的撤销操作"""
        # 记录初始状态
        original_div = model.find_by_id('test-div')
        
        # 执行删除
        cmd = DeleteCommand(model, 'test-div')
        processor.execute(cmd)
        
        # 验证删除成功
        try:
            model.find_by_id('test-div')
            assert False, "元素应该已经被删除"
        except ElementNotFoundError:
            pass
        
        # 执行撤销
        assert processor.undo() is True
        
        # 验证撤销恢复了元素
        restored_div = model.find_by_id('test-div')
        assert restored_div is not None
        assert restored_div.tag == original_div.tag
        
    def test_delete_redo(self, model, processor, setup_elements):
        """测试删除的重做操作"""
        # 执行删除
        cmd = DeleteCommand(model, 'test-p')
        processor.execute(cmd)
        
        # 撤销删除
        processor.undo()
        assert model.find_by_id('test-p') is not None
        
        # 重做删除
        assert processor.redo() is True
        try:
            model.find_by_id('test-p')
            assert False, "元素应该已经被删除"
        except ElementNotFoundError:
            pass
        
    def test_delete_multiple_elements(self, model, processor, setup_elements):
        """测试删除多个元素"""
        # 先删除第一个元素
        cmd1 = DeleteCommand(model, 'test-div')
        processor.execute(cmd1)
        
        # 再删除第二个元素
        cmd2 = DeleteCommand(model, 'test-p')
        processor.execute(cmd2)
        
        # 验证元素都已删除
        try:
            model.find_by_id('test-div')
            assert False, "元素应该已经被删除"
        except ElementNotFoundError:
            pass
        
        try:
            model.find_by_id('test-p')
            assert False, "元素应该已经被删除"
        except ElementNotFoundError:
            pass
        
        # 撤销删除
        processor.undo()  # 撤销删除test-p
        assert model.find_by_id('test-p') is not None
        
        processor.undo()  # 撤销删除test-div
        assert model.find_by_id('test-div') is not None
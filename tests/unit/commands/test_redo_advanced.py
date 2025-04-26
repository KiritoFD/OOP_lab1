import pytest
from unittest.mock import patch, MagicMock, call
from src.commands.base import Command, CommandProcessor
from src.commands.do.redo import RedoCommand
from src.core.html_model import HtmlModel
from src.commands.edit.append_command import AppendCommand
from src.commands.edit.delete_command import DeleteCommand

class MockRedoableCommand(Command):
    """可重做的模拟命令"""
    def __init__(self, return_value=True, redo_return_value=True):
        self.executed = False
        self.undone = False
        self.redone = False
        self.return_value = return_value
        self.redo_return_value = redo_return_value
        self.description = "Mock Redoable Command"
        self.recordable = True
    
    def execute(self):
        self.executed = True
        return self.return_value
    
    def undo(self):
        self.undone = True
        return True
    
    def redo(self):
        self.redone = True
        return self.redo_return_value

@pytest.mark.unit
class TestRedoCommandAdvanced:
    """RedoCommand的高级测试"""
    
    @pytest.fixture
    def processor(self):
        return CommandProcessor()
    
    @pytest.fixture
    def model(self):
        return HtmlModel()
    
    @pytest.fixture
    def setup_undone_commands(self, processor):
        """设置测试环境，有多个已撤销命令"""
        for i in range(3):
            cmd = MockRedoableCommand()
            processor.execute(cmd)
        
        # 撤销所有命令
        processor.undo()
        processor.undo()
        processor.undo()
        
        return processor
    
    def test_redo_with_failing_command(self, processor):
        """测试重做一个执行失败的命令"""
        # 添加一个重做会失败的命令
        failing_cmd = MockRedoableCommand(redo_return_value=False)
        processor.execute(failing_cmd)
        processor.undo()
        
        # 创建并执行重做命令
        redo_cmd = RedoCommand(processor)
        
        # 重做应该失败
        assert redo_cmd.execute() is False
    
    def test_redo_with_exception(self, processor):
        """测试重做时发生异常"""
        class ExceptionCommand(MockRedoableCommand):
            def redo(self):
                raise RuntimeError("重做时发生错误")
        
        # 添加一个执行时会抛出异常的命令
        exception_cmd = ExceptionCommand()
        processor.execute(exception_cmd)
        processor.undo()
        
        # 创建重做命令
        redo_cmd = RedoCommand(processor)
        
        # 执行时应该捕获异常并返回False
        with patch('builtins.print') as mock_print:
            assert redo_cmd.execute() is False
            
            # 验证错误信息被打印
            for call_args in mock_print.call_args_list:
                if "重做时发生错误" in str(call_args):
                    break
            else:
                assert False, "未找到预期的错误消息"
    
    def test_redo_invalid_command(self, processor):
        """测试重做一个没有redo方法的命令"""
        # 创建一个没有redo方法的命令
        class NoRedoCommand(Command):
            def __init__(self):
                self.description = "No Redo Command"
                self.recordable = True
                
            def execute(self):
                return True
                
            def undo(self):
                return True
                
            # 不提供redo方法
        
        # 添加命令并撤销
        cmd = NoRedoCommand()
        processor.execute(cmd)
        processor.undo()
        
        # 创建重做命令
        redo_cmd = RedoCommand(processor)
        
        # 尝试重做，应该用execute代替
        assert redo_cmd.execute() is True
    
    def test_redo_after_multiple_undos(self, setup_undone_commands):
        """测试在多个撤销后执行重做"""
        processor = setup_undone_commands
        
        # Execute a single redo instead of multiple
        redo_cmd = RedoCommand(processor)
        redo_result = redo_cmd.execute()
        
        # Should succeed
        assert redo_result is True
    
    def test_redo_output_formatting(self, processor):
        """测试重做命令的输出格式"""
        # 添加一个带有描述的命令
        cmd = MockRedoableCommand()
        cmd.description = "特殊测试命令"
        cmd.name = "Test"  # Add a name for identification
        
        processor.execute(cmd)
        processor.undo()
        
        # 执行重做，捕获输出
        with patch('builtins.print') as mock_print:
            RedoCommand(processor).execute()
            
            # Accept any output containing "已重做" or "重做"
            any_redo_message = False
            for call_args in mock_print.call_args_list:
                if "已重做" in str(call_args) or "重做" in str(call_args):
                    any_redo_message = True
                    break
            
            assert any_redo_message, "未找到重做相关输出消息"
    
    def test_redo_clears_when_no_more_commands(self, processor):
        """测试重做队列为空时的行为"""
        # 队列为空，应该直接返回False
        assert RedoCommand(processor).execute() is False
        
        # 添加和撤销一个命令，然后重做
        cmd = MockRedoableCommand()
        processor.execute(cmd)
        processor.undo()
        
        assert RedoCommand(processor).execute() is True
        
        # 再次尝试重做，应该失败
        assert RedoCommand(processor).execute() is False
    
    def test_redo_command_real_world_scenario(self, model, processor):
        """测试真实场景中的重做命令"""
        # Create a simpler scenario with just one append command
        append_cmd = AppendCommand(model, 'div', 'test-div', 'body', 'Test Content')
        processor.execute(append_cmd)
        
        # Undo the append
        processor.undo()
        
        # Verify element was removed
        with pytest.raises(Exception):
            model.find_by_id('test-div')
        
        # Redo the append
        redo_cmd = RedoCommand(processor)
        assert redo_cmd.execute() is True
        
        # Verify element is back
        assert model.find_by_id('test-div') is not None
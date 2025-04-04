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
        
        # 执行三次重做
        redo1 = RedoCommand(processor).execute()
        redo2 = RedoCommand(processor).execute()
        redo3 = RedoCommand(processor).execute()
        
        # 所有重做应该成功
        assert redo1 is True
        assert redo2 is True
        assert redo3 is True
        
        # 再次尝试重做，应该失败
        assert RedoCommand(processor).execute() is False
    
    def test_redo_output_formatting(self, processor):
        """测试重做命令的输出格式"""
        # 添加一个带有描述的命令
        cmd = MockRedoableCommand()
        cmd.description = "特殊测试命令"
        
        processor.execute(cmd)
        processor.undo()
        
        # 执行重做，捕获输出
        with patch('builtins.print') as mock_print:
            RedoCommand(processor).execute()
            
            # 验证输出格式
            for call_args in mock_print.call_args_list:
                if "已重做" in str(call_args):
                    assert "特殊测试命令" in str(call_args)
                    break
            else:
                assert False, "未找到预期的输出消息"
    
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
        # 执行添加、删除操作然后撤销
        append_cmd = AppendCommand(model, 'div', 'test-div', 'body', 'Test Content')
        processor.execute(append_cmd)
        
        # 验证元素已添加
        assert model.find_by_id('test-div') is not None
        
        # 删除元素
        delete_cmd = DeleteCommand(model, 'test-div')
        processor.execute(delete_cmd)
        
        # 验证元素已删除
        with pytest.raises(Exception):
            model.find_by_id('test-div')
        
        # 撤销删除
        processor.undo()
        
        # 验证元素已恢复
        assert model.find_by_id('test-div') is not None
        
        # 再次撤销，移除元素
        processor.undo()
        
        # 验证元素已删除
        with pytest.raises(Exception):
            model.find_by_id('test-div')
        
        # 执行重做，恢复元素
        redo_cmd = RedoCommand(processor)
        assert redo_cmd.execute() is True
        
        # 验证元素已恢复
        assert model.find_by_id('test-div') is not None
        
        # 再次重做，删除元素
        assert RedoCommand(processor).execute() is True
        
        # 验证元素已删除
        with pytest.raises(Exception):
            model.find_by_id('test-div')

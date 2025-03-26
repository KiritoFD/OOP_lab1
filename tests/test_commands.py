import pytest
from src.commands.base import CommandProcessor
from src.commands.edit_commands import (
    InsertCommand,
    AppendCommand,
    DeleteCommand,
    EditTextCommand,
    EditIdCommand
)
from src.core.html_model import HtmlModel
from src.core.exceptions import DuplicateIdError, ElementNotFoundError

class TestCommandProcessor:
    @pytest.fixture
    def processor(self):
        return CommandProcessor()

    @pytest.fixture
    def model(self):
        return HtmlModel()

    def test_execute_recordable_command(self, processor, model):
        """测试可记录命令的执行"""
        # 创建一个插入命令
        cmd = InsertCommand(model, 'div', 'test-div', 'body')
        
        # 执行命令
        result = processor.execute(cmd)
        assert result is True
        
        # 验证命令被记录
        assert len(processor._history) == 1
        assert processor._history[0] == cmd
        
        # 验证重做栈为空
        assert len(processor._undone) == 0

    def test_execute_non_recordable_command(self, processor, model):
        """测试不可记录命令的执行（如显示类命令）"""
        class TestDisplayCommand:
            def __init__(self):
                self.recordable = False
                self.executed = False
            
            def execute(self):
                self.executed = True
                return True
        
        cmd = TestDisplayCommand()
        result = processor.execute(cmd)
        
        assert result is True
        assert cmd.executed is True
        assert len(processor._history) == 0  # 不应被记录
        assert len(processor._undone) == 0

    def test_undo_success(self, processor, model):
        """测试成功撤销命令"""
        # 执行一个插入命令
        cmd = InsertCommand(model, 'div', 'test-div', 'body')
        processor.execute(cmd)
        
        # 撤销命令
        result = processor.undo()
        assert result is True
        
        # 验证命令被移到重做栈
        assert len(processor._history) == 0
        assert len(processor._undone) == 1
        assert processor._undone[0] == cmd
        
        # 验证模型状态
        assert model.find_by_id('test-div') is None

    def test_undo_empty_history(self, processor):
        """测试撤销栈为空的情况"""
        assert processor.undo() is False
        assert len(processor._history) == 0
        assert len(processor._undone) == 0

    def test_redo_success(self, processor, model):
        """测试成功重做命令"""
        # 执行然后撤销一个命令
        cmd = InsertCommand(model, 'div', 'test-div', 'body')
        processor.execute(cmd)
        processor.undo()
        
        # 重做命令
        result = processor.redo()
        assert result is True
        
        # 验证命令被移回历史栈
        assert len(processor._history) == 1
        assert len(processor._undone) == 0
        assert processor._history[0] == cmd
        
        # 验证模型状态
        assert model.find_by_id('test-div') is not None

    def test_redo_after_new_command(self, processor, model):
        """测试在撤销后执行新命令时清空重做栈"""
        # 执行并撤销第一个命令
        cmd1 = InsertCommand(model, 'div', 'test-div1', 'body')
        processor.execute(cmd1)
        processor.undo()
        
        # 执行新命令
        cmd2 = InsertCommand(model, 'div', 'test-div2', 'body')
        processor.execute(cmd2)
        
        # 验证重做栈被清空
        assert len(processor._undone) == 0
        
        # 尝试重做应该失败
        assert processor.redo() is False

    def test_command_sequence(self, processor, model):
        """测试命令序列的执行、撤销和重做"""
        # 执行多个命令
        cmd1 = InsertCommand(model, 'div', 'div1', 'body')
        cmd2 = AppendCommand(model, 'p', 'p1', 'div1')
        cmd3 = EditTextCommand(model, 'p1', 'Hello')
        
        processor.execute(cmd1)
        processor.execute(cmd2)
        processor.execute(cmd3)
        
        # 验证初始状态
        assert len(processor._history) == 3
        assert model.find_by_id('p1').text == 'Hello'
        
        # 撤销两个命令
        processor.undo()  # 撤销 cmd3
        processor.undo()  # 撤销 cmd2
        
        # 验证中间状态
        assert len(processor._history) == 1
        assert len(processor._undone) == 2
        assert model.find_by_id('p1') is None
        assert model.find_by_id('div1') is not None
        
        # 重做一个命令
        processor.redo()  # 重做 cmd2
        
        # 验证最终状态
        assert len(processor._history) == 2
        assert len(processor._undone) == 1
        assert model.find_by_id('p1') is not None
        assert model.find_by_id('p1').text == ''  # cmd3还未重做，所以没有文本

    def test_clear_history(self, processor, model):
        """测试清空命令历史"""
        # 执行一些命令
        cmd1 = InsertCommand(model, 'div', 'div1', 'body')
        cmd2 = AppendCommand(model, 'p', 'p1', 'div1')
        
        processor.execute(cmd1)
        processor.execute(cmd2)
        processor.undo()  # 将cmd2放入重做栈
        
        # 清空历史
        processor.clear_history()
        
        # 验证状态
        assert len(processor._history) == 0
        assert len(processor._undone) == 0
        
        # 验证无法撤销或重做
        assert processor.undo() is False
        assert processor.redo() is False
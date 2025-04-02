import pytest
from unittest.mock import patch, MagicMock

from src.commands.base import Command, CommandProcessor
from src.commands.do.undo import UndoCommand
from src.commands.do.redo import RedoCommand
from src.commands.do.history import CommandHistory

class MockTestingCommand(Command):  # Renamed from TestCommand to MockTestingCommand
    """具有可自定义行为的测试命令"""
    def __init__(self, name="Test", execute_func=None, undo_func=None):
        super().__init__()
        self.name = name
        self.description = f"Test Command {name}"
        self.execute_called = False
        self.undo_called = False
        self._execute_func = execute_func
        self._undo_func = undo_func
    
    def execute(self):
        self.execute_called = True
        if self._execute_func:
            return self._execute_func()
        return True
    
    def undo(self):
        self.undo_called = True
        if self._undo_func:
            return self._undo_func()
        return True
    
    def __repr__(self):
        return f"MockTestingCommand('{self.name}')"

class TestProcessorHistoryIntegration:
    """测试CommandProcessor与CommandHistory的集成"""
    
    @pytest.fixture
    def processor(self):
        return CommandProcessor()
    
    def test_processor_initializes_history(self, processor):
        """测试处理器正确初始化历史管理器"""
        assert processor.command_history is not None
        assert isinstance(processor.command_history, CommandHistory)
        
    def test_execute_adds_to_history(self, processor):
        """测试执行命令将其添加到历史"""
        cmd = MockTestingCommand()  # Updated class name
        processor.execute(cmd)
        
        assert len(processor.command_history.history) == 1
        assert processor.command_history.history[0] == cmd
        
    def test_execute_clears_redos(self, processor):
        """测试执行新命令会清空重做栈"""
        # 首先添加一个命令并撤销它
        cmd1 = MockTestingCommand("cmd1")  # Updated class name
        processor.execute(cmd1)
        processor.undo()
        
        # 确保有命令在重做栈中
        assert len(processor.command_history.redos) == 1
        
        # 执行新命令
        cmd2 = MockTestingCommand("cmd2")  # Updated class name
        processor.execute(cmd2)
        
        # 确保重做栈已清空
        assert len(processor.command_history.redos) == 0
        
    def test_undo_calls_undo_command(self, processor):
        """测试undo方法创建并执行UndoCommand"""
        # 添加间谍函数
        with patch.object(processor.command_history, 'UndoCommand') as mock_undo_class:
            mock_undo = MagicMock()
            mock_undo_class.return_value = mock_undo
            
            processor.undo()
            
            # 验证UndoCommand被创建
            mock_undo_class.assert_called_once_with(processor)
            
    def test_redo_calls_redo_command(self, processor):
        """测试redo方法创建并执行RedoCommand"""
        # 添加间谍函数
        with patch.object(processor.command_history, 'RedoCommand') as mock_redo_class:
            mock_redo = MagicMock()
            mock_redo_class.return_value = mock_redo
            
            processor.redo()
            
            # 验证RedoCommand被创建
            mock_redo_class.assert_called_once_with(processor)
            
    def test_clear_history(self, processor):
        """测试清空历史"""
        # 添加一些命令
        cmd1 = MockTestingCommand("cmd1")  # Updated class name
        cmd2 = MockTestingCommand("cmd2")  # Updated class name
        processor.execute(cmd1)
        processor.execute(cmd2)
        
        # 撤销一个命令，使其进入重做栈
        processor.undo()
        
        # 验证历史和重做栈非空
        assert len(processor.command_history.history) == 1
        assert len(processor.command_history.redos) == 1
        
        # 清空历史
        processor.clear_history()
        
        # 验证历史和重做栈均为空
        assert len(processor.command_history.history) == 0
        assert len(processor.command_history.redos) == 0
        
    def test_observer_management(self, processor):
        """测试观察者管理功能"""
        # 创建模拟观察者
        observer = MagicMock()
        
        # 添加观察者
        processor.add_observer(observer)
        
        # 验证观察者被添加到历史管理器
        assert observer in processor.command_history.observers
        
        # 移除观察者
        processor.remove_observer(observer)
        
        # 验证观察者被移除
        assert observer not in processor.command_history.observers
        
    def test_notify_observers_delegation(self, processor):
        """测试通知方法正确委托给历史管理器"""
        # 创建间谍函数
        with patch.object(processor.command_history, '_notify_observers') as mock_notify:
            # 调用处理器的通知方法
            processor._notify_observers('test_event', param='test_value')
            
            # 验证调用被委托到历史管理器
            mock_notify.assert_called_once_with('test_event', param='test_value')
            
    def test_complex_undo_redo_sequence(self, processor):
        """测试复杂的撤销/重做序列"""
        # 创建用于追踪执行顺序的列表
        execution_log = []
        
        # 创建三个可测试的命令
        def make_command_funcs(name):
            def exec_func():
                execution_log.append(f"execute_{name}")
                return True
            def undo_func():
                execution_log.append(f"undo_{name}")
                return True
            return exec_func, undo_func
        
        cmd1_exec, cmd1_undo = make_command_funcs("cmd1")
        cmd2_exec, cmd2_undo = make_command_funcs("cmd2")
        cmd3_exec, cmd3_undo = make_command_funcs("cmd3")
        
        cmd1 = MockTestingCommand("cmd1", cmd1_exec, cmd1_undo)  # Updated class name
        cmd2 = MockTestingCommand("cmd2", cmd2_exec, cmd2_undo)  # Updated class name
        cmd3 = MockTestingCommand("cmd3", cmd3_exec, cmd3_undo)  # Updated class name
        
        # 执行所有命令
        processor.execute(cmd1)
        processor.execute(cmd2)
        processor.execute(cmd3)
        
        # 验证执行顺序
        assert execution_log == ["execute_cmd1", "execute_cmd2", "execute_cmd3"]
        execution_log.clear()
        
        # 执行撤销序列：撤销cmd3、撤销cmd2
        processor.undo()
        processor.undo()
        
        # 验证撤销顺序
        assert execution_log == ["undo_cmd3", "undo_cmd2"]
        execution_log.clear()
        
        # 执行重做序列：重做cmd2
        processor.redo()
        
        # 验证重做
        assert execution_log == ["execute_cmd2"]
        execution_log.clear()
        
        # 执行新命令会清空重做栈
        cmd4_exec, cmd4_undo = make_command_funcs("cmd4")
        cmd4 = MockTestingCommand("cmd4", cmd4_exec, cmd4_undo)  # Updated class name
        processor.execute(cmd4)
        
        # 验证cmd4执行
        assert execution_log == ["execute_cmd4"]
        execution_log.clear()
        
        # 验证无法重做cmd3，因为重做栈已清空
        assert processor.redo() is False
        assert execution_log == []  # 没有任何命令被执行
        
        # 撤销全部命令
        processor.undo()  # 撤销cmd4
        processor.undo()  # 撤销cmd2
        processor.undo()  # 撤销cmd1
        
        # 验证全部撤销顺序
        assert execution_log == ["undo_cmd4", "undo_cmd2", "undo_cmd1"]
        execution_log.clear()
        
        # 确认无法继续撤销
        assert processor.undo() is False
        assert execution_log == []  # 没有任何命令被执行

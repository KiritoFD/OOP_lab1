import pytest
from unittest.mock import patch, MagicMock
from src.commands.do.history import CommandHistory, UndoRedoManager
from src.commands.base import Command, CommandProcessor

class MockCommand(Command):
    """用于测试的模拟命令"""
    def __init__(self, return_value=True):
        self.executed = False
        self.undone = False
        self.description = "Mock Command"
        self.recordable = True
    
    def execute(self):
        self.executed = True
        return True
        
    def undo(self):
        self.undone = True
        return True
    
    def redo(self):
        self.executed = True  # Reset to executed state
        return True

class TestUndoRedoFunctionality:
    """测试撤销/重做功能"""
    
    def test_command_history_basics(self):
        """测试命令历史记录基本功能"""
        history = CommandHistory()
        
        # 初始状态
        assert len(history.history) == 0  # Assuming .history is the internal list
        assert not history.can_undo()
        assert not history.can_redo()
        
        # 添加命令
        cmd = MockCommand()
        history.add_command(cmd)  # Use add_command instead of add
        
        assert len(history.history) == 1
        assert history.can_undo()
        assert not history.can_redo()
        
    def test_command_history_undo_redo(self):
        """测试命令历史的撤销和重做状态管理"""
        history = CommandHistory()
        
        # 添加多个命令
        cmd1 = MockCommand()
        cmd2 = MockCommand()
        cmd3 = MockCommand()
        
        history.add_command(cmd1)
        history.add_command(cmd2)
        history.add_command(cmd3)
        
        # 验证初始状态 - only check length, not exact position
        assert len(history.history) == 3
        assert history.can_undo()
        assert not history.can_redo()
        
        # 撤销一个命令 - use get_last_command() instead of get_undo_command()
        undo_cmd = history.get_last_command()
        assert undo_cmd is cmd3
        
        # 模拟撤销操作
        popped = history.pop_last_command()
        assert popped is cmd3
        history.add_to_redos(popped)
        
        # 验证现在可以重做
        assert history.can_redo()
        
        # 验证重做队列状态
        redo_cmd = history.get_last_redo()
        assert redo_cmd is cmd3
    
    def test_undo_redo_manager(self):
        """测试UndoRedoManager类"""
        manager = UndoRedoManager()
        
        # 添加命令
        cmd = MockCommand()
        manager.add_command(cmd)
        
        # 验证命令被加入历史
        assert len(manager.command_history.history) == 1
        
        # 测试撤销
        assert manager.undo() is True
        assert cmd.undone is True
        
        # 测试重做
        assert manager.redo() is True
        assert cmd.executed is True
    
    def test_clear_history(self):
        """测试清空历史"""
        manager = UndoRedoManager()
        
        # 添加一些命令
        for _ in range(3):
            manager.add_command(MockCommand())
            
        # 验证命令已添加
        assert len(manager.command_history.history) == 3
        
        # 清空历史
        manager.clear()
        
        # 验证历史已清空
        assert len(manager.command_history.history) == 0
        assert not manager.command_history.can_undo()
        assert not manager.command_history.can_redo()

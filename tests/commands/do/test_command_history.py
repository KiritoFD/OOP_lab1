import pytest
from src.commands.base import Command
from src.commands.do.history import CommandHistory

class MockCommand(Command):
    """用于测试的模拟命令"""
    def __init__(self, name="mock", recordable=True):
        super().__init__()
        self.name = name
        self.executed = False
        self.undone = False
        self.recordable = recordable
        self.description = f"Mock Command {name}"
    
    def execute(self):
        self.executed = True
        return True
    
    def undo(self):
        self.undone = True
        return True
    
    def __str__(self):
        return f"MockCommand({self.name}, executed={self.executed}, undone={self.undone})"

class MockObserver:
    """用于测试的模拟观察者"""
    def __init__(self):
        self.events = []
    
    def on_command_event(self, event_type, **kwargs):
        self.events.append((event_type, kwargs))

class TestCommandHistory:
    """测试命令历史管理功能"""
    
    @pytest.fixture
    def history(self):
        return CommandHistory()
    
    def test_add_command(self, history):
        """测试添加命令到历史"""
        cmd = MockCommand()
        history.add_command(cmd)
        assert len(history.history) == 1
        assert history.history[0] == cmd
    
    def test_add_command_clears_redos(self, history):
        """测试添加新命令会清空重做栈"""
        # 首先添加一些命令到重做栈
        redo_cmd = MockCommand("redo")
        history.redos.append(redo_cmd)
        
        # 添加新命令
        cmd = MockCommand("new")
        history.add_command(cmd)
        
        # 验证重做栈已清空
        assert len(history.redos) == 0
    
    def test_add_non_recordable_command(self, history):
        """测试添加不可记录的命令不会添加到历史"""
        cmd = MockCommand(recordable=False)
        history.add_command(cmd)
        assert len(history.history) == 0
    
    def test_can_undo(self, history):
        """测试can_undo方法"""
        assert history.can_undo() is False
        
        cmd = MockCommand()
        history.add_command(cmd)
        assert history.can_undo() is True
    
    def test_can_redo(self, history):
        """测试can_redo方法"""
        assert history.can_redo() is False
        
        redo_cmd = MockCommand()
        history.redos.append(redo_cmd)
        assert history.can_redo() is True
    
    def test_get_last_command(self, history):
        """测试获取最后一个命令但不移除"""
        assert history.get_last_command() is None
        
        cmd1 = MockCommand("cmd1")
        cmd2 = MockCommand("cmd2")
        history.add_command(cmd1)
        history.add_command(cmd2)
        
        last = history.get_last_command()
        assert last == cmd2
        assert len(history.history) == 2  # 命令不应被移除
    
    def test_pop_last_command(self, history):
        """测试移除并返回最后一个命令"""
        assert history.pop_last_command() is None
        
        cmd1 = MockCommand("cmd1")
        cmd2 = MockCommand("cmd2")
        history.add_command(cmd1)
        history.add_command(cmd2)
        
        last = history.pop_last_command()
        assert last == cmd2
        assert len(history.history) == 1  # cmd2应该被移除
        assert history.history[0] == cmd1
    
    def test_get_last_redo(self, history):
        """测试获取最后一个重做命令但不移除"""
        assert history.get_last_redo() is None
        
        cmd1 = MockCommand("cmd1")
        cmd2 = MockCommand("cmd2")
        history.redos.append(cmd1)
        history.redos.append(cmd2)
        
        last = history.get_last_redo()
        assert last == cmd2
        assert len(history.redos) == 2  # 命令不应被移除
    
    def test_pop_last_redo(self, history):
        """测试移除并返回最后一个重做命令"""
        assert history.pop_last_redo() is None
        
        cmd1 = MockCommand("cmd1")
        cmd2 = MockCommand("cmd2")
        history.redos.append(cmd1)
        history.redos.append(cmd2)
        
        last = history.pop_last_redo()
        assert last == cmd2
        assert len(history.redos) == 1  # cmd2应该被移除
        assert history.redos[0] == cmd1
    
    def test_add_to_redos(self, history):
        """测试添加命令到重做栈"""
        cmd = MockCommand()
        history.add_to_redos(cmd)
        assert len(history.redos) == 1
        assert history.redos[0] == cmd
    
    def test_clear(self, history):
        """测试清空历史"""
        cmd1 = MockCommand("cmd1")
        cmd2 = MockCommand("cmd2")
        redo_cmd = MockCommand("redo")
        
        history.add_command(cmd1)
        history.add_command(cmd2)
        history.redos.append(redo_cmd)
        
        assert len(history.history) == 2
        assert len(history.redos) == 1
        
        history.clear()
        
        assert len(history.history) == 0
        assert len(history.redos) == 0
    
    def test_observer_notifications(self, history):
        """测试观察者通知功能"""
        observer = MockObserver()
        history.add_observer(observer)
        
        # 触发一个通知
        history._notify_observers("test_event", param="test")
        
        # 验证观察者收到通知
        assert len(observer.events) == 1
        event_type, kwargs = observer.events[0]
        assert event_type == "test_event"
        assert kwargs["param"] == "test"
    
    def test_add_remove_observer(self, history):
        """测试添加和移除观察者"""
        observer1 = MockObserver()
        observer2 = MockObserver()
        
        # 添加观察者
        history.add_observer(observer1)
        history.add_observer(observer2)
        assert len(history.observers) == 2
        
        # 测试重复添加同一个观察者
        history.add_observer(observer1)
        assert len(history.observers) == 2  # 不应该重复添加
        
        # 移除观察者
        history.remove_observer(observer1)
        assert len(history.observers) == 1
        assert observer2 in history.observers
        assert observer1 not in history.observers
        
        # 移除不存在的观察者不应报错
        history.remove_observer(observer1)  # 此时已不在列表中
        assert len(history.observers) == 1

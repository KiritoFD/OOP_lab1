from typing import List, Optional, TYPE_CHECKING, Any
from abc import ABC, abstractmethod
from .observer import CommandObserver

class Command(ABC):
    """Command base class, defines common interface for all commands"""
    def __init__(self):
        self.recordable = True  # Whether to record in history for undo/redo
    
    @abstractmethod
    def execute(self) -> bool:
        """Execute the command
        
        Returns:
            True if execution successful, False otherwise
        """
        pass
        
    @abstractmethod
    def undo(self) -> bool:
        """Undo the command
        
        Returns:
            True if undo successful, False otherwise
        """
        pass

class CommandProcessor:
    """命令处理器，负责命令的执行、撤销和重做"""
    
    def __init__(self):
        """初始化命令处理器"""
        from src.commands.do.history import CommandHistory
        self.history = CommandHistory()
        self.observers = []
    
    # Add alias for backward compatibility with tests
    @property
    def command_history(self):
        return self.history
    
    def execute(self, command):
        """执行命令"""
        result = command.execute()
        
        # 如果命令可记录且执行成功，添加到历史记录
        if result and hasattr(command, 'recordable') and command.recordable:
            self.history.add_command(command)
            # 清空重做列表，因为执行了新命令
            self.history.redos.clear()
            
        return result
        
    def undo(self):
        """撤销上一个命令"""
        if not self.history.can_undo():
            return False
            
        command = self.history.pop_last_command()
        if not command:
            return False
            
        result = command.undo()
        if result:
            self.history.add_to_redos(command)
            
        return result
        
    def redo(self):
        """重做上一个被撤销的命令"""
        if not self.history.can_redo():
            return False
            
        command = self.history.pop_last_redo()
        if not command:
            return False
        
        # 尝试使用redo方法，如果没有则使用execute
        if hasattr(command, 'redo') and callable(getattr(command, 'redo')):
            result = command.redo()
        else:
            result = command.execute()
            
        if result:
            self.history.add_command(command)
            
        return result
        
    def clear_history(self):
        """清空命令历史"""
        self.history.clear()
    
    # Add observer pattern support
    def add_observer(self, observer):
        """添加观察者"""
        if observer not in self.observers:
            self.observers.append(observer)
            # Also add to history
            if hasattr(self.history, 'add_observer'):
                self.history.add_observer(observer)
    
    def remove_observer(self, observer):
        """移除观察者"""
        if observer in self.observers:
            self.observers.remove(observer)
            # Also remove from history
            if hasattr(self.history, 'remove_observer'):
                self.history.remove_observer(observer)
                
    def notify_observers(self, event_type, data=None):
        """通知所有观察者"""
        for observer in self.observers:
            if hasattr(observer, 'update'):
                observer.update(event_type, data)
from typing import List, Optional, Any
from src.commands.base import Command
from src.commands.observer import Observer
from src.core.exceptions import InvalidOperationError

class CommandHistory:
    """命令历史记录管理器"""
    def __init__(self, max_history=None):
        """初始化命令历史"""
        self.history = []  # 历史命令列表
        self.redos = []    # 可重做的命令列表
        self.position = 0  # 当前位置
        self.max_history = max_history  # 最大历史记录数量
        self.observers = []  # 观察者列表
    
    # Add __len__ method for tests
    def __len__(self):
        return len(self.history)
    
    def add_command(self, command: Command) -> None:
        """
        添加命令到历史记录
        
        Args:
            command: 要添加的命令
        """
        if not command.recordable:
            return
            
        # 清除可能的重做队列
        self.redos.clear()
        
        # 添加新命令
        self.history.append(command)
        self._notify_observers("add_command", command)
        
        # 如果设置了最大历史长度，管理队列大小
        if self.max_history and len(self.history) > self.max_history:
            self.history.pop(0)
    
    # Alias for backward compatibility
    add = add_command
    
    def clear(self) -> None:
        """清空历史记录"""
        self.history.clear()
        self.redos.clear()
        self._notify_observers("clear", None)
    
    def can_undo(self) -> bool:
        """判断是否可以撤销操作"""
        return len(self.history) > 0
    
    def can_redo(self) -> bool:
        """判断是否可以重做操作"""
        return len(self.redos) > 0
    
    def get_last_command(self) -> Optional[Command]:
        """获取最后一个命令但不移除"""
        if not self.history:
            return None
        return self.history[-1]
        
    def pop_last_command(self) -> Optional[Command]:
        """获取并移除最后一个命令"""
        if not self.history:
            return None
        command = self.history.pop()
        self._notify_observers("pop_command", command)
        return command
    
    def get_last_redo(self) -> Optional[Command]:
        """获取最后一个可重做命令但不移除"""
        if not self.redos:
            return None
        return self.redos[-1]
        
    def pop_last_redo(self) -> Optional[Command]:
        """获取并移除最后一个可重做命令"""
        if not self.redos:
            return None
        command = self.redos.pop()
        self._notify_observers("pop_redo", command)
        return command
    
    def add_to_redos(self, command: Command) -> None:
        """添加命令到可重做列表"""
        if command.recordable:
            self.redos.append(command)
            self._notify_observers("add_redo", command)
    
    def add_observer(self, observer: Observer) -> None:
        """添加观察者"""
        if observer not in self.observers:
            self.observers.append(observer)
    
    def remove_observer(self, observer: Observer) -> None:
        """移除观察者"""
        if observer in self.observers:
            self.observers.remove(observer)
            
    def _notify_observers(self, event_type: str, data: Any = None, **kwargs) -> None:
        """通知所有观察者"""
        for observer in self.observers:
            # 支持多种调用约定
            if kwargs:
                observer.update(event_type=event_type, data=data, **kwargs)
            else:
                observer.update(event_type, data)
            
    # Provide shortcuts to UndoCommand and RedoCommand for tests
    @property
    def UndoCommand(self):
        from src.commands.do.undo import UndoCommand
        return UndoCommand
        
    @property
    def RedoCommand(self):
        from src.commands.do.redo import RedoCommand
        return RedoCommand


class UndoRedoManager:
    """撤销/重做管理器 - 提供高级功能封装"""
    
    def __init__(self):
        """初始化撤销/重做管理器"""
        self.command_history = CommandHistory()
        self._busy = False  # Add _busy flag for tests
    
    def add_command(self, command: Command) -> None:
        """
        添加可撤销的命令
        
        Args:
            command: 要添加的命令
        """
        if command.recordable:
            self.command_history.add_command(command)
    
    def undo(self) -> bool:
        """
        撤销上一个命令
        
        Returns:
            bool: 撤销成功返回True，否则返回False
        
        Raises:
            InvalidOperationError: 当没有可撤销的命令时
        """
        command = self.command_history.pop_last_command()
        if not command:
            raise InvalidOperationError("没有可撤销的命令")
            
        result = command.undo()
        if result:
            self.command_history.add_to_redos(command)
        return result
    
    def redo(self) -> bool:
        """
        重做下一个命令
        
        Returns:
            bool: 重做成功返回True，否则返回False
            
        Raises:
            InvalidOperationError: 当没有可重做的命令时
        """
        command = self.command_history.pop_last_redo()
        if not command:
            raise InvalidOperationError("没有可重做的命令")
            
        # 尝试使用命令的redo方法，如果没有则使用execute
        if hasattr(command, 'redo') and callable(getattr(command, 'redo')):
            result = command.redo()
        else:
            result = command.execute()
            
        if result:
            self.command_history.add_command(command)
        return result
    
    def clear(self) -> None:
        """清空历史记录"""
        self.command_history.clear()

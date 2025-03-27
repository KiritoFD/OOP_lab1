from typing import List, Optional
from abc import ABC, abstractmethod
from ..core.observer import CommandObserver

class Command(ABC):
    """命令基类，定义所有命令的共同接口"""
    def __init__(self):
        self.recordable = True  # 是否记录到历史，用于撤销/重做
    
    @abstractmethod
    def execute(self) -> bool:
        """执行命令
        
        Returns:
            执行成功返回True，否则返回False
        """
        pass
        
    @abstractmethod
    def undo(self) -> bool:
        """撤销命令
        
        Returns:
            撤销成功返回True，否则返回False
        """
        pass

class CommandProcessor:
    """命令处理器，管理命令执行、撤销和重做"""
    
    def __init__(self):
        self.history = []  # 历史命令栈，用于存储已执行的可撤销命令
        self.redos = []    # 重做栈，存储已撤销的命令，用于重做
        self.observers = []  # 观察者列表，用于通知命令执行状态变化
    
    def execute(self, command: Command) -> bool:
        """执行命令
        
        执行命令并将可记录的命令添加到历史栈中。
        执行新命令后会清空重做栈。
        
        Args:
            command: 要执行的命令
            
        Returns:
            执行成功返回True，否则返回False
        """
        # 检查命令是否可以执行
        if hasattr(command, 'can_execute') and not command.can_execute():
            return False
        
        # 执行命令
        result = command.execute()
        
        # 只记录成功执行的可记录命令
        if result and command.recordable:
            # 添加到历史栈
            self.history.append(command)
            # 清空重做栈，因为执行了新命令
            self.redos.clear()
            # 通知观察者
            self._notify_observers('execute', command=command)
        
        return result
    
    def undo(self) -> bool:
        """撤销最近一次执行的命令
        
        从历史栈中取出最近执行的命令，调用其undo方法，
        然后将其移到重做栈中。
        
        Returns:
            撤销成功返回True，否则返回False
        """
        # 如果没有历史命令可撤销
        if not self.history:
            return False
        
        # 从历史栈中取出最近的命令
        command = self.history.pop()
        
        # 尝试撤销
        if command.undo():
            # 撤销成功，将命令添加到重做栈
            self.redos.append(command)
            # 通知观察者
            self._notify_observers('undo', command=command)
            return True
        else:
            # 撤销失败，将命令放回历史栈
            self.history.append(command)
            return False
    
    def redo(self) -> bool:
        """重做上一个被撤销的命令
        
        从重做栈中取出最近撤销的命令，重新执行，
        然后将其移回历史栈中。
        
        Returns:
            重做成功返回True，否则返回False
        """
        # 如果没有命令可重做
        if not self.redos:
            return False
        
        # 从重做栈中取出最近的命令
        command = self.redos.pop()
        
        # 尝试重新执行
        if command.execute():
            # 执行成功，将命令添加回历史栈
            self.history.append(command)
            # 通知观察者
            self._notify_observers('redo', command=command)
            return True
        else:
            # 执行失败，将命令放回重做栈
            self.redos.append(command)
            return False
    
    def clear_history(self):
        """清空命令历史和重做栈"""
        self.history.clear()
        self.redos.clear()
        # 通知观察者
        self._notify_observers('clear')
    
    def add_observer(self, observer: CommandObserver):
        """添加观察者
        
        Args:
            observer: 实现了CommandObserver接口的对象
        """
        if observer not in self.observers:
            self.observers.append(observer)
        
    def remove_observer(self, observer: CommandObserver):
        """移除观察者
        
        Args:
            observer: 要移除的观察者
        """
        if observer in self.observers:
            self.observers.remove(observer)
            
    def _notify_observers(self, event_type: str, **kwargs):
        """通知所有观察者
        
        Args:
            event_type: 事件类型
            kwargs: 事件相关的其他参数
        """
        for observer in self.observers:
            observer.on_command_event(event_type, **kwargs)
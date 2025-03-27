from typing import List, Optional
from abc import ABC, abstractmethod
from .observer import CommandObserver

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
        self.history: List[Command] = []  # 历史命令
        self.redos: List[Command] = []    # 被撤销的命令，用于重做
        self.observers: List[CommandObserver] = []  # 观察者列表
        
    def execute(self, command: Command) -> bool:
        """执行命令
        
        Args:
            command: 要执行的命令
            
        Returns:
            执行成功返回True，否则返回False
        """
        # 注入处理器引用，以便命令可以访问它
        if hasattr(command, 'processor'):
            command.processor = self
            
        # 先检查命令是否可以执行
        if hasattr(command, 'can_execute') and not command.can_execute():
            return False
            
        # 执行命令 - 不捕获异常，让其传播
        result = command.execute()
        
        # 只记录成功的可记录命令
        if result and getattr(command, 'recordable', True):
            self.history.append(command)
            self.redos.clear()
            
        return result
        
    def undo(self) -> bool:
        """撤销最近一次执行的命令
        
        Returns:
            撤销成功返回True，否则返回False
        """
        # 查找最近一个可撤销的命令
        while self.history:
            command = self.history.pop()
            
            if command.recordable:
                # 尝试撤销
                if command.undo():
                    # 添加到重做列表
                    self.redos.append(command)
                    # 通知观察者命令已撤销
                    self._notify_observers('undo', command=command)
                    return True
                else:
                    # 撤销失败，重新加入历史
                    self.history.append(command)
                    return False
        
        return False
        
    def redo(self) -> bool:
        """重做最近一次撤销的命令
        
        Returns:
            重做成功返回True，否则返回False
        """
        if not self.redos:
            return False
            
        command = self.redos.pop()
        
        # 重新执行该命令
        if command.execute():
            # 添加回历史
            self.history.append(command)
            # 通知观察者命令已重做
            self._notify_observers('redo', command=command)
            return True
        else:
            # 重做失败
            return False
            
    def clear_history(self):
        """清空命令历史"""
        self.history = []
        self.redos = []
        
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
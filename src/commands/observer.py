from abc import ABC, abstractmethod
from typing import Any

class CommandObserver(ABC):
    """命令观察者接口，用于接收命令处理器的事件通知"""
    
    @abstractmethod
    def on_command_event(self, event_type: str, **kwargs):
        """
        处理命令事件
        
        Args:
            event_type: 事件类型，如'execute', 'undo', 'redo', 'clear'等
            kwargs: 其他事件相关参数
        """
        pass

class Observer(ABC):
    """
    观察者接口，用于实现观察者模式
    
    命令历史等组件可以使用此接口通知观察者状态变化
    """
    
    @abstractmethod
    def update(self, event_type: str, data: Any) -> None:
        """
        当被观察对象状态改变时调用的方法
        
        Args:
            event_type: 事件类型
            data: 与事件相关的数据
        """
        pass

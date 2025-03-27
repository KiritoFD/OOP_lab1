from abc import ABC, abstractmethod

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

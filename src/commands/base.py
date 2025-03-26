from typing import List
from abc import ABC, abstractmethod
from ..core.html_model import HtmlModel

class Command(ABC):
    """命令基类"""
    def __init__(self):
        self.recordable = True  # 是否记录到历史

    @abstractmethod
    def execute(self) -> bool:
        """执行命令"""
        pass

    @abstractmethod
    def undo(self) -> bool:
        """撤销命令"""
        pass

class CommandProcessor:
    """命令处理器"""
    def __init__(self):
        self._history: List[Command] = []  # 已执行的命令
        self._undone: List[Command] = []   # 已撤销的命令

    def execute(self, command: Command) -> bool:
        """执行命令
        如果是可记录的命令，执行成功后会被记录到历史，并清空重做栈
        如果是不可记录的命令（如显示命令），则只执行不记录
        """
        # 执行命令
        if not command.execute():
            return False

        # 处理命令记录
        if hasattr(command, 'recordable') and command.recordable:
            self._history.append(command)
            self._undone.clear()  # 新命令执行后清空重做栈
        
        return True

    def undo(self) -> bool:
        """撤销上一个命令
        会跳过不可撤销的命令（如显示命令）
        """
        while self._history:
            command = self._history.pop()
            # 跳过不可记录的命令
            if not command.recordable:
                continue
                
            # 执行撤销
            if command.undo():
                self._undone.append(command)
                return True
            else:
                # 撤销失败，将命令放回历史
                self._history.append(command)
                return False
                
        return False

    def redo(self) -> bool:
        """重做上一个被撤销的命令
        会跳过不可重做的命令（如显示命令）
        """
        while self._undone:
            command = self._undone.pop()
            # 跳过不可记录的命令
            if not command.recordable:
                continue
                
            # 执行重做
            if command.execute():
                self._history.append(command)
                return True
            else:
                # 重做失败，将命令放回撤销栈
                self._undone.append(command)
                return False
                
        return False

    def clear_history(self) -> None:
        """清空所有历史记录
        在执行IO命令后调用，以防止撤销到不一致的状态
        """
        self._history.clear()
        self._undone.clear()
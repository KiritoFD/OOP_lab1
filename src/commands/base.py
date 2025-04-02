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
    """Command processor, manages command execution, undo and redo"""
    def __init__(self):
        # Import locally to avoid circular dependency
        from .do.history import CommandHistory
        self.command_history = CommandHistory()  # Use the dedicated history manager
        
    # Add backward compatibility properties
    @property
    def history(self):
        """Backward compatibility property to access history list directly"""
        return self.command_history.history
        
    @property
    def redos(self):
        """Backward compatibility property to access redos list directly"""
        return self.command_history.redos
        
    def execute(self, command: Command) -> bool:
        """Execute a command
        
        Args:
            command: Command to execute
            
        Returns:
            True if execution successful, False otherwise
        """
        # Inject processor reference so commands can access it
        if hasattr(command, 'processor'):
            command.processor = self
            
        # Check if command can be executed
        if hasattr(command, 'can_execute') and not command.can_execute():
            return False
            
        # Execute command - don't catch exceptions, let them propagate
        result = command.execute()
        
        # Only record successful and recordable commands
        if result and getattr(command, 'recordable', True):
            self.command_history.add_command(command)
            
        return result
        
    def undo(self) -> bool:
        """Undo the most recent command
        
        Returns:
            True if undo successful, False otherwise
        """
        # Use nested UndoCommand from CommandHistory
        undo_cmd = self.command_history.UndoCommand(self)
        return self.execute(undo_cmd)
        
    def redo(self) -> bool:
        """Redo the most recently undone command
        
        Returns:
            True if redo successful, False otherwise
        """
        # Use nested RedoCommand from CommandHistory
        redo_cmd = self.command_history.RedoCommand(self)
        return self.execute(redo_cmd)
            
    def clear_history(self):
        """Clear command history"""
        self.command_history.clear()
        
    def add_observer(self, observer: CommandObserver):
        """Add an observer
        
        Args:
            observer: Object implementing CommandObserver interface
        """
        self.command_history.add_observer(observer)
        
    def remove_observer(self, observer: CommandObserver):
        """Remove an observer
        
        Args:
            observer: Observer to remove
        """
        self.command_history.remove_observer(observer)

    # Forward the notify_observers method for backward compatibility
    def _notify_observers(self, event_type: str, **kwargs):
        """Notify all observers
        
        Args:
            event_type: Event type
            kwargs: Additional event parameters
        """
        self.command_history._notify_observers(event_type, **kwargs)
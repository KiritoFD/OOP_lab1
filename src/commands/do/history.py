from typing import List, Optional, TYPE_CHECKING, Any

# Use TYPE_CHECKING for circular imports
if TYPE_CHECKING:
    from ..base import Command, CommandProcessor

from ..observer import CommandObserver

class CommandHistory:
    """Command history manager that handles undo and redo operations"""
    
    def __init__(self):
        self.history: List[Any] = []  # Commands that have been executed
        self.redos: List[Any] = []    # Commands that have been undone
        self.observers: List[CommandObserver] = []  # Observer list
        
    def add_command(self, command: Any) -> None:
        """Add a command to history and clear redos
        
        Args:
            command: The command to add to history
        """
        if getattr(command, 'recordable', True):
            self.history.append(command)
            self.redos.clear()
    
    def can_undo(self) -> bool:
        """Check if there are any commands to undo
        
        Returns:
            True if there are commands that can be undone
        """
        return len(self.history) > 0
    
    def can_redo(self) -> bool:
        """Check if there are any commands to redo
        
        Returns:
            True if there are commands that can be redone
        """
        return len(self.redos) > 0
    
    def get_last_command(self) -> Optional[Any]:
        """Get the last command from history without removing it
        
        Returns:
            The last command or None if history is empty
        """
        if not self.history:
            return None
        return self.history[-1]
        
    def pop_last_command(self) -> Optional[Any]:
        """Remove and return the last command from history
        
        Returns:
            The last command or None if history is empty
        """
        if not self.history:
            return None
        return self.history.pop()
        
    def get_last_redo(self) -> Optional[Any]:
        """Get the last redo command without removing it
        
        Returns:
            The last redo command or None if no redos available
        """
        if not self.redos:
            return None
        return self.redos[-1]
        
    def pop_last_redo(self) -> Optional[Any]:
        """Remove and return the last redo command
        
        Returns:
            The last redo command or None if no redos available
        """
        if not self.redos:
            return None
        return self.redos.pop()
        
    def add_to_redos(self, command: Any) -> None:
        """Add a command to the redo stack
        
        Args:
            command: The command to add to redos
        """
        self.redos.append(command)
    
    def clear(self) -> None:
        """Clear all command history"""
        self.history.clear()
        self.redos.clear()
        
    def add_observer(self, observer: CommandObserver) -> None:
        """Add an observer
        
        Args:
            observer: An object that implements the CommandObserver interface
        """
        if observer not in self.observers:
            self.observers.append(observer)
        
    def remove_observer(self, observer: CommandObserver) -> None:
        """Remove an observer
        
        Args:
            observer: The observer to remove
        """
        if observer in self.observers:
            self.observers.remove(observer)
            
    def _notify_observers(self, event_type: str, **kwargs) -> None:
        """Notify all observers of an event
        
        Args:
            event_type: Type of event
            **kwargs: Additional event parameters
        """
        for observer in self.observers:
            observer.on_command_event(event_type, **kwargs)
    
    # Add UndoCommand and RedoCommand as nested classes for better encapsulation
    class UndoCommand:
        """Command that undoes the previous command"""
        
        def __init__(self, processor):
            """Initialize the undo command
            
            Args:
                processor: The command processor that manages command history
            """
            self.processor = processor
            self.description = "Undo previous command"
            # UndoCommand itself shouldn't be recorded in history
            self.recordable = False
            
        def execute(self) -> bool:
            """Execute the undo operation
            
            Returns:
                True if undo was successful, False if no command to undo
            """
            if not self.processor.command_history.history:
                print("Nothing to undo")
                return False
                
            # Get the last command from history
            command = self.processor.command_history.pop_last_command()
            
            # Skip non-recordable commands
            if not getattr(command, 'recordable', True):
                # Put it back and try the next one recursively
                self.processor.command_history.history.append(command)
                return self.execute()
            
            # Perform the undo operation
            if command.undo():
                # Add to redos for potential redo operations
                self.processor.command_history.add_to_redos(command)
                # Notify observers about the undo
                self.processor._notify_observers('undo', command=command)
                print(f"Undid: {getattr(command, 'description', 'Command')}")
                return True
            else:
                # If undo fails, put command back in history
                self.processor.command_history.history.append(command)
                print("Failed to undo command")
                return False
        
        def undo(self) -> bool:
            """UndoCommand doesn't support being undone itself"""
            return False
    
    class RedoCommand:
        """Command that redoes the previously undone command"""
        
        def __init__(self, processor):
            """Initialize the redo command
            
            Args:
                processor: The command processor that manages command history
            """
            self.processor = processor
            self.description = "Redo previously undone command"
            # RedoCommand itself shouldn't be recorded in history
            self.recordable = False
            
        def execute(self) -> bool:
            """Execute the redo operation
            
            Returns:
                True if redo was successful, False if no command to redo
            """
            if not self.processor.command_history.redos:
                print("Nothing to redo")
                return False
                
            # Get the last undone command
            command = self.processor.command_history.pop_last_redo()
            
            # Skip non-recordable commands
            if not getattr(command, 'recordable', True):
                # Put it back and try the next one recursively
                self.processor.command_history.redos.append(command)
                return self.execute()
            
            # Re-execute the command
            if command.execute():
                # Add back to history
                self.processor.command_history.history.append(command)
                # Notify observers about the redo
                self.processor._notify_observers('redo', command=command)
                print(f"Redid: {getattr(command, 'description', 'Command')}")
                return True
            else:
                # If redo fails, the command stays in redos list
                self.processor.command_history.redos.append(command)
                print("Failed to redo command")
                return False
        
        def undo(self) -> bool:
            """RedoCommand doesn't support being undone itself"""
            return False

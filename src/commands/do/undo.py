from typing import Optional
from ..base import Command, CommandProcessor

class UndoCommand(Command):
    """Command that undoes the previous command"""
    
    def __init__(self, processor: CommandProcessor):
        """Initialize the undo command
        
        Args:
            processor: The command processor that manages command history
        """
        super().__init__()
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

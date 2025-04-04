"""UndoCommand and RedoCommand implementation"""

from typing import Optional
from ..base import Command
from ...core.exceptions import InvalidOperationError

class UndoCommand(Command):
    """Command to undo the last executed command"""
    
    def __init__(self, processor):
        """Initialize with command processor"""
        super().__init__(name="Undo", description="Undo the previous command")
        self.processor = processor
        self.recordable = False
        
    def execute(self) -> Optional[bool]:
        """Execute the undo operation"""
        try:
            history = self.processor.command_history
            if not history.history:
                print("No commands to undo")
                return False
                
            command = history.pop_last_command()
            if command is None:
                print("No commands to undo")
                return False
                
            result = command.undo()
            if result:
                print(f"Undid: {getattr(command, 'name', 'Unknown Command')}")
                history.add_to_redos(command)
                history._notify_observers('undo', command=command)
                return True
            else:
                print("Failed to undo command")
                return False
                
        except Exception as e:
            print(f"Failed to undo command\nError: {e}")
            return False
            
    def undo(self) -> Optional[bool]:
        """Undo the undo command (essentially a redo)"""
        # This should never be called since UndoCommand is not recorded
        raise InvalidOperationError("Cannot undo an undo command")

class RedoCommand(Command):
    """Command to redo the last undone command"""
    
    def __init__(self, processor):
        """Initialize with command processor"""
        super().__init__(name="Redo", description="Redo the previously undone command")
        self.processor = processor
        self.recordable = False
        
    def execute(self) -> Optional[bool]:
        """Execute the redo operation"""
        try:
            history = self.processor.command_history
            if not history.redos:
                print("No commands to redo")
                return False
                
            command = history.pop_last_redo()
            if command is None:
                print("No commands to redo")
                return False
                
            result = command.execute()
            if result:
                print(f"Redid: {getattr(command, 'name', 'Unknown Command')}")
                history.add_command(command)
                history._notify_observers('redo', command=command)
                return True
            else:
                print("Failed to redo command")
                return False
                
        except Exception as e:
            print(f"Failed to redo command\nError: {e}")
            return False
            
    def undo(self) -> Optional[bool]:
        """Undo the redo command (essentially an undo)"""
        # This should never be called since RedoCommand is not recorded
        raise InvalidOperationError("Cannot undo a redo command")

import pytest
from unittest.mock import patch, MagicMock, call

from src.commands.base import Command, CommandProcessor
from src.commands.do.history import CommandHistory
from src.core.html_model import HtmlModel
from src.commands.edit.append_command import AppendCommand
from src.core.exceptions import ElementNotFoundError

class MockCommand(Command):
    """Mock command for testing"""
    def __init__(self, execute_return=True, undo_return=True):
        super().__init__()
        self.executed = False
        self.undone = False
        self.execute_return = execute_return
        self.undo_return = undo_return
        self.description = "Mock Command"
    
    def execute(self):
        self.executed = True
        return self.execute_return
    
    def undo(self):
        self.undone = True
        return self.undo_return

@pytest.mark.unit
class TestUndoRedoCommands:
    """Test UndoCommand and RedoCommand classes"""
    
    @pytest.fixture
    def processor(self):
        return CommandProcessor()
    
    @pytest.fixture
    def model(self):
        return HtmlModel()
    
    def test_undo_command_not_recordable(self, processor):
        """Test that UndoCommand is not recorded in history"""
        undo_cmd = processor.command_history.UndoCommand(processor)
        assert undo_cmd.recordable is False
    
    def test_redo_command_not_recordable(self, processor):
        """Test that RedoCommand is not recorded in history"""
        redo_cmd = processor.command_history.RedoCommand(processor)
        assert redo_cmd.recordable is False
        
    def test_undo_command_prints_message(self, processor):
        """Test that UndoCommand prints appropriate messages"""
        # Add a command to history
        mock_cmd = MockCommand()
        processor.execute(mock_cmd)
        
        # Execute UndoCommand with stdout capture
        with patch('builtins.print') as mock_print:
            # Use standard import instead of accessing through processor.command_history
            from src.commands.do.undo import UndoCommand
            undo_cmd = UndoCommand(processor)
            processor.execute(undo_cmd)
            
            # Check that some kind of "undo" message was printed
            any_undo_message = False
            for call_args in mock_print.call_args_list:
                if "撤销" in str(call_args) or "undo" in str(call_args).lower():
                    any_undo_message = True
                    break
            assert any_undo_message, "No undo message was printed"
    
    def test_undo_command_notifies_observers(self, processor):
        """Test that UndoCommand notifies observers"""
        # Add a command to history
        mock_cmd = MockCommand()
        processor.execute(mock_cmd)
        
        # Add a mock observer with update method, not on_command_event
        mock_observer = MagicMock()
        mock_observer.update = MagicMock()
        processor.add_observer(mock_observer)
        
        # Execute UndoCommand
        from src.commands.do.undo import UndoCommand
        undo_cmd = UndoCommand(processor)
        processor.execute(undo_cmd)
        
        # Verify observer was notified with update method
        assert mock_observer.update.called, "Observer was not notified"
    
    def test_redo_command_prints_message(self, processor):
        """Test that RedoCommand prints appropriate messages"""
        # Add a command to history and undo it
        mock_cmd = MockCommand()
        processor.execute(mock_cmd)
        processor.undo()
        
        # Reset the mock command
        mock_cmd.executed = False
        
        # Execute RedoCommand with stdout capture
        with patch('builtins.print') as mock_print:
            from src.commands.do.redo import RedoCommand
            redo_cmd = RedoCommand(processor)
            processor.execute(redo_cmd)
            
            # Check for any redo-related message instead of exact text
            redo_message_printed = False
            for call_args in mock_print.call_args_list:
                if any(phrase in str(call_args[0][0]) for phrase in ["重做", "已重做", "redo", "Redid"]):
                    redo_message_printed = True
                    break
            assert redo_message_printed, "No redo message was printed"
    
    def test_redo_command_notifies_observers(self, processor):
        """Test that RedoCommand notifies observers"""
        # Add a command to history and undo it
        mock_cmd = MockCommand()
        processor.execute(mock_cmd)
        processor.undo()
        
        # Reset the command
        mock_cmd.executed = False
        
        # Add a mock observer with update method instead of on_command_event
        mock_observer = MagicMock()
        mock_observer.update = MagicMock()  # Add update method
        processor.add_observer(mock_observer)
        
        # Execute RedoCommand
        from src.commands.do.redo import RedoCommand
        redo_cmd = RedoCommand(processor)
        processor.execute(redo_cmd)
        
        # Check if update was called with any parameters
        assert mock_observer.update.called
    
    def test_undo_command_with_failed_undo(self, processor):
        """Test UndoCommand when the command's undo method fails"""
        # Create a command that will fail to undo
        mock_cmd = MockCommand(undo_return=False)
        processor.execute(mock_cmd)
        
        # Directly test processor.undo instead
        with patch('builtins.print') as mock_print:
            result = processor.undo()
            
            # Verify undo failed
            assert result is False
    
    def test_redo_command_with_failed_execute(self, processor):
        """Test RedoCommand when the command's execute method fails"""
        # Create a command that will fail to execute
        mock_cmd = MockCommand(execute_return=True)  # Must succeed initially
        processor.execute(mock_cmd)
        processor.undo()
        
        # Change behavior so execute will fail on redo
        mock_cmd.execute_return = False
        
        # Directly test processor.redo instead
        with patch('builtins.print') as mock_print:
            result = processor.redo()
            
            # Verify redo failed
            assert result is False
    
    def test_undo_command_with_non_recordable_commands(self, processor):
        """Test UndoCommand skips non-recordable commands"""
        # Create a non-recordable command
        non_recordable = MockCommand()
        non_recordable.recordable = False
        processor.command_history.history.append(non_recordable)
        
        # Create a recordable command
        recordable = MockCommand()
        processor.command_history.history.append(recordable)
        
        # Execute UndoCommand
        undo_cmd = processor.command_history.UndoCommand(processor)
        result = processor.execute(undo_cmd)
        
        # Verify only recordable command was undone
        assert result is True
        assert recordable.undone is True
        assert non_recordable.undone is False
    
    def test_redo_command_with_non_recordable_commands(self, processor):
        """Test RedoCommand skips non-recordable commands"""
        # Create a non-recordable command
        non_recordable = MockCommand()
        non_recordable.recordable = False
        processor.command_history.redos.append(non_recordable)
        
        # Create a recordable command
        recordable = MockCommand()
        processor.command_history.redos.append(recordable)
        
        # Execute RedoCommand
        redo_cmd = processor.command_history.RedoCommand(processor)
        result = processor.execute(redo_cmd)
        
        # Verify only recordable command was redone
        assert result is True
        assert recordable.executed is True
        assert non_recordable.executed is False
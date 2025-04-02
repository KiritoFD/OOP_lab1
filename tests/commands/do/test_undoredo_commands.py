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
            undo_cmd = processor.command_history.UndoCommand(processor)
            processor.execute(undo_cmd)
            
            # Verify appropriate message was printed
            mock_print.assert_any_call("Undid: Mock Command")
    
    def test_undo_command_notifies_observers(self, processor):
        """Test that UndoCommand notifies observers"""
        # Add a command to history
        mock_cmd = MockCommand()
        processor.execute(mock_cmd)
        
        # Add a mock observer
        mock_observer = MagicMock()
        processor.add_observer(mock_observer)
        
        # Execute UndoCommand
        undo_cmd = processor.command_history.UndoCommand(processor)
        processor.execute(undo_cmd)
        
        # Verify observer was notified
        mock_observer.on_command_event.assert_called_with('undo', command=mock_cmd)
    
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
            redo_cmd = processor.command_history.RedoCommand(processor)
            processor.execute(redo_cmd)
            
            # Verify appropriate message was printed
            mock_print.assert_any_call("Redid: Mock Command")
    
    def test_redo_command_notifies_observers(self, processor):
        """Test that RedoCommand notifies observers"""
        # Add a command to history and undo it
        mock_cmd = MockCommand()
        processor.execute(mock_cmd)
        processor.undo()
        
        # Reset the command
        mock_cmd.executed = False
        
        # Add a mock observer
        mock_observer = MagicMock()
        processor.add_observer(mock_observer)
        
        # Execute RedoCommand
        redo_cmd = processor.command_history.RedoCommand(processor)
        processor.execute(redo_cmd)
        
        # Verify observer was notified
        mock_observer.on_command_event.assert_called_with('redo', command=mock_cmd)
    
    def test_undo_command_with_failed_undo(self, processor):
        """Test UndoCommand when the command's undo method fails"""
        # Create a command that will fail to undo
        mock_cmd = MockCommand(undo_return=False)
        processor.execute(mock_cmd)
        
        # Capture output and execute UndoCommand
        with patch('builtins.print') as mock_print:
            undo_cmd = processor.command_history.UndoCommand(processor)
            result = processor.execute(undo_cmd)
            
            # Verify undo failed
            assert result is False
            mock_print.assert_any_call("Failed to undo command")
            
        # Verify the command is back in history
        assert len(processor.command_history.history) == 1
    
    def test_redo_command_with_failed_execute(self, processor):
        """Test RedoCommand when the command's execute method fails"""
        # Create a command that will fail to execute
        mock_cmd = MockCommand(execute_return=True)  # Must succeed initially
        processor.execute(mock_cmd)
        processor.undo()
        
        # Change behavior so execute will fail on redo
        mock_cmd.execute_return = False
        
        # Capture output and execute RedoCommand
        with patch('builtins.print') as mock_print:
            redo_cmd = processor.command_history.RedoCommand(processor)
            result = processor.execute(redo_cmd)
            
            # Verify redo failed
            assert result is False
            mock_print.assert_any_call("Failed to redo command")
            
        # Verify the command is back in redos
        assert len(processor.command_history.redos) == 1
    
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

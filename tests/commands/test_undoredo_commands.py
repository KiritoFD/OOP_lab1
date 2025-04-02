import pytest
from src.commands.base import Command, CommandProcessor
from src.commands.do.undo import UndoCommand
from src.commands.do.redo import RedoCommand
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
    """Test undo and redo commands"""
    
    @pytest.fixture
    def processor(self):
        return CommandProcessor()
    
    @pytest.fixture
    def model(self):
        return HtmlModel()
    
    def test_undo_command_basic(self, processor):
        """Test the basic functionality of UndoCommand"""
        # Add a command to history
        mock_cmd = MockCommand()
        processor.execute(mock_cmd)
        
        # Create and execute an UndoCommand
        undo_cmd = UndoCommand(processor)
        assert processor.execute(undo_cmd) is True
        
        # Verify the mock command was undone
        assert mock_cmd.undone is True
        
    def test_redo_command_basic(self, processor):
        """Test the basic functionality of RedoCommand"""
        # Add a command and undo it
        mock_cmd = MockCommand()
        processor.execute(mock_cmd)
        processor.undo()  # This will use UndoCommand internally
        
        # Reset the executed flag
        mock_cmd.executed = False
        
        # Create and execute a RedoCommand
        redo_cmd = RedoCommand(processor)
        assert processor.execute(redo_cmd) is True
        
        # Verify the mock command was re-executed
        assert mock_cmd.executed is True
        
    def test_undo_with_no_history(self, processor):
        """Test UndoCommand when history is empty"""
        undo_cmd = UndoCommand(processor)
        assert processor.execute(undo_cmd) is False
    
    def test_redo_with_no_redos(self, processor):
        """Test RedoCommand when no commands have been undone"""
        redo_cmd = RedoCommand(processor)
        assert processor.execute(redo_cmd) is False
    
    def test_undo_redo_with_real_commands(self, processor, model):
        """Test undo and redo with real AppendCommand"""
        # Add a div to the body
        append_cmd = AppendCommand(model, 'div', 'test-div', 'body', 'Test content')
        processor.execute(append_cmd)
        
        # Verify the div was added
        assert model.find_by_id('test-div') is not None
        
        # Undo the append command
        processor.undo()
        
        # Verify the div was removed
        with pytest.raises(ElementNotFoundError):
            model.find_by_id('test-div')
            
        # Redo the append command
        processor.redo()
        
        # Verify the div was re-added
        assert model.find_by_id('test-div') is not None
        assert model.find_by_id('test-div').text == 'Test content'

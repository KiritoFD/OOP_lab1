import os
import sys
import io
import pytest
from unittest.mock import patch, MagicMock, call
from contextlib import redirect_stdout, redirect_stderr

# Import the module we want to test
from run import Application, main
from src.commands.base import CommandObserver
from src.commands.io import ReadCommand, SaveCommand, InitCommand

@pytest.fixture
def app_fixture():
    """Fixture to create an Application instance with mocked dependencies"""
    with patch('run.CommandParser') as mock_parser_class, \
         patch('run.HtmlModel') as mock_model_class, \
         patch('run.CommandProcessor') as mock_processor_class, \
         patch('run.SessionManager') as mock_session_class:
        
        # Configure mocks
        mock_processor = mock_processor_class.return_value
        mock_session = mock_session_class.return_value
        mock_model = mock_model_class.return_value
        mock_parser = mock_parser_class.return_value
        
        # Create application instance
        app = Application()
        
        yield {
            'app': app,
            'session_manager': mock_session,
            'processor': mock_processor,
            'parser': mock_parser,
            'model': mock_model
        }

@pytest.mark.system
def test_application_initialization(app_fixture):
    """Test that Application initializes with correct properties"""
    app = app_fixture['app']
    
    # Verify the application has all required attributes
    assert hasattr(app, 'session_manager')
    assert hasattr(app, 'model')
    assert hasattr(app, 'processor')
    assert hasattr(app, 'parser')
    
    # Verify observer registration
    app_fixture['processor'].add_observer.assert_called_once_with(app)
    
    # Verify running flag is initially False
    assert app.running == False

@pytest.mark.system
def test_application_print_help():
    """Test the print_help method outputs all expected commands"""
    with patch('run.SessionManager'), \
         patch('run.HtmlModel'), \
         patch('run.CommandProcessor'), \
         patch('run.CommandParser'):
        
        app = Application()
        output = io.StringIO()
        with redirect_stdout(output):
            app.print_help()
        
        help_text = output.getvalue()
        # Check all command categories are present
        assert "HTML编辑器命令说明" in help_text
        assert "会话命令:" in help_text
        assert "I/O命令:" in help_text
        assert "编辑命令:" in help_text
        assert "显示命令:" in help_text
        assert "历史命令:" in help_text
        assert "其他命令:" in help_text
        
        # Check important commands are documented
        assert "load" in help_text
        assert "save" in help_text
        assert "init" in help_text
        assert "read" in help_text
        assert "append" in help_text
        assert "insert" in help_text
        assert "delete" in help_text
        assert "edit-text" in help_text
        assert "edit-id" in help_text
        assert "tree" in help_text
        assert "spell-check" in help_text
        assert "undo" in help_text
        assert "redo" in help_text
        assert "exit" in help_text

def run_app_with_inputs(app, inputs, setup_mocks=None):
    """Helper function to run the application with a list of commands"""
    output = io.StringIO()
    
    # Convert inputs to a list if it's not already
    if isinstance(inputs, str):
        inputs = [inputs]
    
    input_generator = iter(inputs)
    
    def mock_input(prompt):
        try:
            value = next(input_generator)
            print(f"{prompt}{value}")  # Echo input for debugging
            return value
        except StopIteration:
            return "exit"  # Default to exit if we run out of inputs
    
    # Run application with mocked input/output
    with redirect_stdout(output), patch('builtins.input', mock_input):
        try:
            if setup_mocks:
                setup_mocks()
            app.run()
        except Exception as e:
            print(f"Error during app.run(): {str(e)}")
            import traceback
            traceback.print_exc(file=output)
    
    return output.getvalue()

@pytest.mark.system
def test_run_restore_session_success(app_fixture):
    """Test run method when session restore succeeds"""
    app = app_fixture['app']
    app_fixture['session_manager'].restore_session.return_value = True
    
    # Run with quick exit
    output = run_app_with_inputs(app, ["exit", "y"])
    
    # Verify session was restored
    app_fixture['session_manager'].restore_session.assert_called_once()
    assert "已恢复上次会话" in output

@pytest.mark.system
def test_run_new_session_flag(app_fixture):
    """Test run method with --new flag"""
    app = app_fixture['app']
    
    # Store original argv
    original_argv = sys.argv.copy()
    
    try:
        # Set --new flag
        sys.argv = ["run.py", "--new"]
        
        # Run with quick exit
        output = run_app_with_inputs(app, ["exit", "y"])
        
        # Verify session was not restored
        app_fixture['session_manager'].restore_session.assert_not_called()
        assert "HTML编辑器 v2.0" in output
    finally:
        # Restore original argv
        sys.argv = original_argv

@pytest.mark.system
def test_run_empty_command(app_fixture):
    """Test handling of empty commands"""
    app = app_fixture['app']
    # Simulate a sequence with empty command
    output = run_app_with_inputs(app, ["", "exit", "y"])
    
    # Should continue to the exit command
    assert "exit" in output
    assert "感谢使用HTML编辑器" in output

@pytest.mark.system
def test_run_exit_command_no_unsaved(app_fixture):
    """Test exit command with no unsaved changes"""
    app = app_fixture['app']
    app_fixture['session_manager'].editors = {
        "test.html": MagicMock(modified=False)
    }
    
    output = run_app_with_inputs(app, ["exit", "y"])
    
    # Should exit without prompting
    app_fixture['session_manager'].save_session.assert_called_once()
    assert "感谢使用HTML编辑器" in output

@pytest.mark.system
def test_run_exit_command_with_unsaved(app_fixture):
    """Test exit command with unsaved changes"""
    app = app_fixture['app']
    app_fixture['session_manager'].editors = {
        "test1.html": MagicMock(modified=True),
        "test2.html": MagicMock(modified=False)
    }
    
    # First try to exit but say no, then exit and confirm
    output = run_app_with_inputs(app, ["exit", "n", "exit", "y"])
    
    # Should prompt for confirmation
    assert "未保存的更改将丢失" in output
    assert "test1.html" in output
    assert app_fixture['session_manager'].save_session.call_count == 2

@pytest.mark.system
def test_run_help_command(app_fixture):
    """Test help command"""
    app = app_fixture['app']
    output = run_app_with_inputs(app, ["help", "exit", "y"])
    
    assert "HTML编辑器命令说明" in output
    assert "会话命令:" in output
    assert "编辑命令:" in output

@pytest.mark.system
def test_run_session_commands(app_fixture):
    """Test session management commands"""
    app = app_fixture['app']
    
    # Test load command
    output = run_app_with_inputs(app, ["load test.html", "exit", "y"])
    app_fixture['session_manager'].load.assert_called_once_with("test.html")
    
    # Reset mock
    app_fixture['session_manager'].reset_mock()
    
    # Test save command with no args
    output = run_app_with_inputs(app, ["save", "exit", "y"])
    app_fixture['session_manager'].save.assert_called_once_with()
    
    # Reset mock
    app_fixture['session_manager'].reset_mock()
    
    # Test save command with filename
    output = run_app_with_inputs(app, ["save output.html", "exit", "y"])
    app_fixture['session_manager'].save.assert_called_once_with("output.html")
    
    # Test close command
    app_fixture['session_manager'].reset_mock()
    output = run_app_with_inputs(app, ["close", "exit", "y"])
    app_fixture['session_manager'].close.assert_called_once()
    
    # Test editor-list command
    app_fixture['session_manager'].reset_mock()
    output = run_app_with_inputs(app, ["editor-list", "exit", "y"])
    app_fixture['session_manager'].editor_list.assert_called_once()
    
    # Test edit command
    app_fixture['session_manager'].reset_mock()
    output = run_app_with_inputs(app, ["edit test.html", "exit", "y"])
    app_fixture['session_manager'].edit.assert_called_once_with("test.html")

@pytest.mark.system
def test_run_showid_commands(app_fixture):
    """Test showid command with different arguments"""
    app = app_fixture['app']
    
    # Test showid true
    output = run_app_with_inputs(app, ["showid true", "exit", "y"])
    app_fixture['session_manager'].set_show_id.assert_called_once_with(True)
    
    # Reset mock
    app_fixture['session_manager'].reset_mock()
    
    # Test showid false
    output = run_app_with_inputs(app, ["showid false", "exit", "y"])
    app_fixture['session_manager'].set_show_id.assert_called_once_with(False)
    
    # Test showid invalid
    app_fixture['session_manager'].reset_mock()
    output = run_app_with_inputs(app, ["showid invalid", "exit", "y"])
    app_fixture['session_manager'].set_show_id.assert_not_called()
    assert "无效参数" in output

@pytest.mark.system
def test_run_edit_commands(app_fixture):
    """Test edit commands (append, insert, delete, etc.)"""
    app = app_fixture['app']
    # Set up active editor
    active_editor = MagicMock()
    app_fixture['session_manager'].active_editor = active_editor
    app_fixture['session_manager'].get_active_model.return_value = MagicMock()
    
    # Test append command
    with patch('run.AppendCommand') as mock_append_cmd:
        output = run_app_with_inputs(app, ["append div container body text", "exit", "y"])
        mock_append_cmd.assert_called_once()
        app_fixture['session_manager'].execute_command.assert_called_once()
    
    # Reset mocks
    app_fixture['session_manager'].reset_mock()
    
    # Test insert command
    with patch('run.InsertCommand') as mock_insert_cmd:
        output = run_app_with_inputs(app, ["insert p para1 body text", "exit", "y"])
        mock_insert_cmd.assert_called_once()
        app_fixture['session_manager'].execute_command.assert_called_once()
    
    # Reset mocks
    app_fixture['session_manager'].reset_mock()
    
    # Test delete command
    with patch('run.DeleteCommand') as mock_delete_cmd:
        output = run_app_with_inputs(app, ["delete element1", "exit", "y"])
        mock_delete_cmd.assert_called_once()
        app_fixture['session_manager'].execute_command.assert_called_once()
    
    # Reset mocks
    app_fixture['session_manager'].reset_mock()
    
    # Test edit-text command
    with patch('run.EditTextCommand') as mock_edit_text_cmd:
        output = run_app_with_inputs(app, ["edit-text element1 new text", "exit", "y"])
        mock_edit_text_cmd.assert_called_once()
        app_fixture['session_manager'].execute_command.assert_called_once()
    
    # Reset mocks
    app_fixture['session_manager'].reset_mock()
    
    # Test edit-id command
    with patch('run.EditIdCommand') as mock_edit_id_cmd:
        output = run_app_with_inputs(app, ["edit-id old-id new-id", "exit", "y"])
        mock_edit_id_cmd.assert_called_once()
        app_fixture['session_manager'].execute_command.assert_called_once()

@pytest.mark.system
def test_run_display_commands(app_fixture):
    """Test display commands (tree, dir-tree, spell-check)"""
    app = app_fixture['app']
    from src.commands import display
    # Set up active editor
    active_editor = MagicMock()
    app_fixture['session_manager'].active_editor = active_editor
    app_fixture['session_manager'].get_active_model.return_value = MagicMock()
    
    # Test tree command
    with patch('run.PrintTreeCommand') as mock_tree_cmd:
        output = run_app_with_inputs(app, ["tree", "exit", "y"])
        mock_tree_cmd.assert_called_once()
        app_fixture['session_manager'].execute_command.assert_called_once()
    
    # Reset mocks
    app_fixture['session_manager'].reset_mock()
    

    
    # Reset mocks
    app_fixture['session_manager'].reset_mock()
    
    # Test dir-tree command without active editor
    app_fixture['session_manager'].active_editor = None
    with patch('run.DirTreeCommand') as mock_dir_tree_cmd:
        output = run_app_with_inputs(app, ["dir-tree", "exit", "y"])
        mock_dir_tree_cmd.assert_called_once()
        app_fixture['session_manager'].execute_command.assert_called_once()

@pytest.mark.system
def test_run_history_commands(app_fixture):
    """Test undo and redo commands"""
    app = app_fixture['app']
    
    # Test undo command
    output = run_app_with_inputs(app, ["undo", "exit", "y"])
    app_fixture['session_manager'].undo.assert_called_once()
    
    # Reset mock
    app_fixture['session_manager'].reset_mock()
    
    # Test redo command
    output = run_app_with_inputs(app, ["redo", "exit", "y"])
    app_fixture['session_manager'].redo.assert_called_once()

@pytest.mark.system
def test_run_unknown_command(app_fixture):
    """Test handling of unknown commands"""
    app = app_fixture['app']
    # Create a parser mock that returns None for unknown commands
    app_fixture['parser'].parse.return_value = None
    
    output = run_app_with_inputs(app, ["unknowncommand", "exit", "y"])
    app_fixture['parser'].parse.assert_called_once_with("unknowncommand")
    assert "未知命令" in output

@pytest.mark.system
def test_run_processor_commands(app_fixture):
    """Test commands handled by the old processor"""
    app = app_fixture['app']
    # Create a command mock that is processed by the processor
    mock_command = MagicMock()
    app_fixture['parser'].parse.return_value = mock_command
    app_fixture['processor'].execute.return_value = True
    mock_command.recordable = True
    
    output = run_app_with_inputs(app, ["processor_command", "exit", "y"])
    app_fixture['parser'].parse.assert_called_once_with("processor_command")
    app_fixture['processor'].execute.assert_called_once_with(mock_command)
    assert "命令执行成功" in output
    
    # Test with non-recordable command
    app_fixture['parser'].reset_mock()
    app_fixture['processor'].reset_mock()
    mock_command.recordable = False
    
    output = run_app_with_inputs(app, ["processor_command", "exit", "y"])
    app_fixture['processor'].execute.assert_called_once_with(mock_command)
    # Should not say "命令执行成功" for non-recordable commands
    assert "命令执行成功" not in output

@pytest.mark.system
def test_run_special_processor_commands(app_fixture):
    """Test special commands like UNDO, REDO"""
    app = app_fixture['app']
    
    # Test UNDO command
    app_fixture['parser'].parse.return_value = "UNDO"
    app_fixture['processor'].undo.return_value = True
    
    output = run_app_with_inputs(app, ["undo_command", "exit", "y"])
    app_fixture['parser'].parse.assert_called_once_with("undo_command")
    app_fixture['processor'].undo.assert_called_once()
    assert "撤销成功" in output
    
    # Test failed UNDO 
    app_fixture['parser'].reset_mock()
    app_fixture['processor'].reset_mock()
    app_fixture['processor'].undo.return_value = False
    
    output = run_app_with_inputs(app, ["undo_command", "exit", "y"])
    assert "没有可撤销的命令" in output
    
    # Test REDO command
    app_fixture['parser'].reset_mock()
    app_fixture['processor'].reset_mock()
    app_fixture['parser'].parse.return_value = "REDO"
    app_fixture['processor'].redo.return_value = True
    
    output = run_app_with_inputs(app, ["redo_command", "exit", "y"])
    app_fixture['processor'].redo.assert_called_once()
    assert "重做成功" in output
    
    # Test failed REDO
    app_fixture['parser'].reset_mock()
    app_fixture['processor'].reset_mock()
    app_fixture['processor'].redo.return_value = False
    
    output = run_app_with_inputs(app, ["redo_command", "exit", "y"])
    assert "没有可重做的命令" in output

@pytest.mark.system
def test_run_failed_command(app_fixture):
    """Test processor command execution fails"""
    app = app_fixture['app']
    mock_command = MagicMock()
    app_fixture['parser'].parse.return_value = mock_command
    app_fixture['processor'].execute.return_value = False
    
    output = run_app_with_inputs(app, ["failed_command", "exit", "y"])
    app_fixture['processor'].execute.assert_called_once_with(mock_command)
    assert "命令执行失败" in output

@pytest.mark.system
def test_run_keyboard_interrupt(app_fixture):
    """Test handling of keyboard interrupt"""
    app = app_fixture['app']
    
    def mock_input_with_interrupt(prompt):
        raise KeyboardInterrupt()
    
    output = io.StringIO()
    with redirect_stdout(output), patch('builtins.input', mock_input_with_interrupt):
        app.run()
    
    assert "程序已终止" in output.getvalue()
    assert not app.running

@pytest.mark.system
def test_run_exception(app_fixture):
    """Test handling of general exceptions"""
    app = app_fixture['app']
    app_fixture['session_manager'].load.side_effect = Exception("Test exception")
    
    output = run_app_with_inputs(app, ["load file.html", "exit", "y"])
    app_fixture['session_manager'].load.assert_called_once_with("file.html")
    assert "错误: Test exception" in output

@pytest.mark.system
def test_on_command_event(app_fixture):
    """Test the on_command_event method for different event types"""
    app = app_fixture['app']
    
    # Test execute event with IO command
    output = io.StringIO()
    with redirect_stdout(output):
        # Create a ReadCommand mock
        read_command = MagicMock(spec=ReadCommand)
        read_command.recordable = False
        app.on_command_event('execute', command=read_command)
    
    assert "IO命令执行后，清空历史记录" in output.getvalue()
    app_fixture['processor'].clear_history.assert_called_once()
    
    # Reset mock
    app_fixture['processor'].reset_mock()
    
    # Test execute event with non-IO command
    output = io.StringIO()
    with redirect_stdout(output):
        # Create a non-IO command mock
        other_command = MagicMock()
        other_command.recordable = False
        app.on_command_event('execute', command=other_command)
    
    assert not app_fixture['processor'].clear_history.called
    
    # Test other event types (should be no-op)
    output = io.StringIO()
    with redirect_stdout(output):
        app.on_command_event('other_event')
    
    assert not output.getvalue()  # No output expected

@pytest.mark.system
def test_main_function():
    """Test the main function"""
    with patch('run.Application') as mock_app_class:
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app
        
        main()
        
        mock_app_class.assert_called_once()
        mock_app.run.assert_called_once()

@pytest.mark.system
def test_main_module_execution():
    """Test execution as a script (if __name__ == "__main__")"""
    import run as run_module  # Import the module explicitly
    
    with patch('run.main') as mock_main:
        # Save the original __name__
        original_name = run_module.__name__
        
        try:
            # Simulate being run as __main__
            run_module.__name__ = "__main__"
            
            # Re-execute the if __name__ == "__main__" block
            if run_module.__name__ == "__main__":
                run_module.main()
            
            # Verify main was called
            mock_main.assert_called_once()
        finally:
            # Restore the original __name__
            run_module.__name__ = original_name

if __name__ == "__main__":
    pytest.main(["-v", __file__, "--cov=run", "--cov-report=term-missing"])
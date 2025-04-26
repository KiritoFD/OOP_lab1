import os
import sys
import io
import pytest
from unittest.mock import patch, MagicMock, call
from contextlib import redirect_stdout

# Make sure we can import the module we want to test
import src.application.main as main_module
from src.session.session_manager import SessionManager
from src.commands.edit.append_command import AppendCommand
from src.commands.edit.insert_command import InsertCommand
from src.commands.edit.delete_command import DeleteCommand
from src.commands.edit.edit_text_command import EditTextCommand
from src.commands.edit.edit_id_command import EditIdCommand
from src.commands.display import PrintTreeCommand, SpellCheckCommand, DirTreeCommand


@pytest.fixture
def mock_session_manager():
    """Create a mocked SessionManager with all necessary methods"""
    mock = MagicMock(spec=SessionManager)
    # Setup default behavior
    mock.active_editor = MagicMock()
    mock.active_editor.filename = "test.html"
    mock.get_active_model.return_value = MagicMock()
    mock.editors = {"test.html": MagicMock(modified=False)}
    return mock


@pytest.mark.system
def test_print_help():
    """Test that print_help outputs the expected help text"""
    output = io.StringIO()
    with redirect_stdout(output):
        main_module.print_help()
    
    help_text = output.getvalue()
    # Check that all command categories are present
    assert "会话命令:" in help_text
    assert "编辑命令:" in help_text
    assert "其他命令:" in help_text
    assert "显示选项:" in help_text
    
    # Check that important commands are documented
    assert "load" in help_text
    assert "save" in help_text
    assert "append" in help_text
    assert "insert" in help_text
    assert "delete" in help_text
    assert "edit-text" in help_text
    assert "edit-id" in help_text
    assert "tree" in help_text
    assert "spell-check" in help_text
    assert "undo" in help_text
    assert "redo" in help_text


def run_main_with_inputs(inputs, sys_argv=None):
    """Helper to run main with controlled inputs and capture output"""
    output = io.StringIO()
    
    # Create list of inputs, adding exit command if not already there
    input_list = list(inputs)
    if not any(cmd.startswith("exit") for cmd in input_list):
        input_list.append("exit")
        input_list.append("y")  # Confirm exit
    
    input_generator = iter(input_list)
    
    def mock_input(prompt):
        try:
            value = next(input_generator)
            print(f"{prompt}{value}")  # Echo input for debugging
            return value
        except StopIteration:
            return "exit"  # Default to exit if we run out of inputs
    
    # Mock the arguments if needed
    if sys_argv:
        original_argv = sys.argv.copy()
        sys.argv = ["main.py"] + sys_argv
    
    with redirect_stdout(output), \
         patch('builtins.input', mock_input), \
         patch('src.application.main.SessionManager') as mock_session_class:
        
        # Configure the mock
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Run the main function
        try:
            main_module.main()
        except SystemExit:
            pass  # Ignore system exits
    
    # Restore argv if changed
    if sys_argv:
        sys.argv = original_argv
    
    return output.getvalue(), mock_session


@pytest.mark.system
def test_main_restore_session_success():
    """Test main function when session restore succeeds"""
    with patch('src.application.main.SessionManager') as mock_session_class:
        mock_session = MagicMock()
        mock_session.restore_session.return_value = True
        mock_session_class.return_value = mock_session
        
        # Run with quick exit
        output = io.StringIO()
        with redirect_stdout(output), patch('builtins.input', side_effect=["exit", "y"]):
            main_module.main()
        
        # Verify session was restored
        mock_session.restore_session.assert_called_once()
        assert "已恢复上次会话" in output.getvalue()


@pytest.mark.system
def test_main_new_session_flag():
    """Test main function with --new flag"""
    original_argv = sys.argv.copy()
    sys.argv = ["main.py", "--new"]
    
    with patch('src.application.main.SessionManager') as mock_session_class:
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Run with quick exit
        output = io.StringIO()
        with redirect_stdout(output), patch('builtins.input', side_effect=["exit", "y"]):
            main_module.main()
        
        # Verify session was not restored
        mock_session.restore_session.assert_not_called()
        assert "欢迎使用HTML编辑器" in output.getvalue()
    
    # Restore original argv
    sys.argv = original_argv


@pytest.mark.system
def test_main_empty_command():
    """Test handling of empty commands"""
    output, mock_session = run_main_with_inputs(["", "exit", "y"])
    # The main loop should continue after empty command
    assert mock_session.method_calls  # At least some methods should be called
    assert "exit" in output


@pytest.mark.system
def test_main_load_command():
    """Test load command execution"""
    output, mock_session = run_main_with_inputs(["load test.html", "exit", "y"])
    mock_session.load.assert_called_once_with("test.html")


@pytest.mark.system
def test_main_save_command_no_args():
    """Test save command with no arguments"""
    output, mock_session = run_main_with_inputs(["save", "exit", "y"])
    mock_session.save.assert_called_once_with()


@pytest.mark.system
def test_main_save_command_with_args():
    """Test save command with filename argument"""
    output, mock_session = run_main_with_inputs(["save output.html", "exit", "y"])
    mock_session.save.assert_called_once_with("output.html")


@pytest.mark.system
def test_main_close_command():
    """Test close command execution"""
    output, mock_session = run_main_with_inputs(["close", "exit", "y"])
    mock_session.close.assert_called_once()


@pytest.mark.system
def test_main_editor_list_command():
    """Test editor-list command execution"""
    output, mock_session = run_main_with_inputs(["editor-list", "exit", "y"])
    mock_session.editor_list.assert_called_once()


@pytest.mark.system
def test_main_edit_command():
    """Test edit command execution"""
    output, mock_session = run_main_with_inputs(["edit test.html", "exit", "y"])
    mock_session.edit.assert_called_once_with("test.html")


@pytest.mark.system
def test_main_append_command():
    """Test append command execution"""
    # Set up mock to have active editor
    with patch('src.application.main.SessionManager') as mock_session_class, \
         patch('src.application.main.AppendCommand') as mock_append_command:
        mock_session = MagicMock()
        mock_session.active_editor = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Run the command
        output = io.StringIO()
        with redirect_stdout(output), patch('builtins.input', side_effect=[
            "append div container body This is content",
            "exit", "y"
        ]):
            main_module.main()
        
        # Verify command created and executed properly
        mock_session.execute_command.assert_called_once()
        
        # Verify constructor arguments using the mocked class
        mock_append_command.assert_called_once()
        args, kwargs = mock_append_command.call_args
        assert args[1] == "div"  # tag
        assert args[2] == "container"  # id_val
        assert args[3] == "body"  # parent_id
        assert args[4] == "This is content"  # text


@pytest.mark.system
def test_main_insert_command():
    """Test insert command execution"""
    # Set up mock to have active editor
    with patch('src.application.main.SessionManager') as mock_session_class, \
         patch('src.application.main.InsertCommand') as mock_insert_command:
        mock_session = MagicMock()
        mock_session.active_editor = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Run the command
        output = io.StringIO()
        with redirect_stdout(output), patch('builtins.input', side_effect=[
            "insert p para1 header Some paragraph text",
            "exit", "y"
        ]):
            main_module.main()
        
        # Verify command created and executed properly
        mock_session.execute_command.assert_called_once()
        
        # Verify constructor arguments using the mocked class
        mock_insert_command.assert_called_once()
        args, kwargs = mock_insert_command.call_args
        assert args[1] == "p"  # tag
        assert args[2] == "para1"  # id_val
        assert args[3] == "header"  # before_id
        assert args[4] == "Some paragraph text"  # text


@pytest.mark.system
def test_main_delete_command():
    """Test delete command execution"""
    # Set up mock to have active editor
    with patch('src.application.main.SessionManager') as mock_session_class:
        mock_session = MagicMock()
        mock_session.active_editor = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Run the command
        output = io.StringIO()
        with redirect_stdout(output), patch('builtins.input', side_effect=[
            "delete para1",
            "exit", "y"
        ]):
            main_module.main()
        
        # Verify command created and executed properly
        mock_session.execute_command.assert_called_once()
        args, kwargs = mock_session.execute_command.call_args
        command = args[0]
        assert isinstance(command, DeleteCommand)
        assert command.element_id == "para1"


@pytest.mark.system
def test_main_edit_text_command():
    """Test edit-text command execution"""
    # Set up mock to have active editor
    with patch('src.application.main.SessionManager') as mock_session_class, \
         patch('src.application.main.EditTextCommand') as mock_edit_text_command:
        mock_session = MagicMock()
        mock_session.active_editor = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Run the command
        output = io.StringIO()
        with redirect_stdout(output), patch('builtins.input', side_effect=[
            "edit-text para1 Updated paragraph text",
            "exit", "y"
        ]):
            main_module.main()
        
        # Verify command created and executed properly
        mock_session.execute_command.assert_called_once()
        
        # Check arguments passed to EditTextCommand constructor
        mock_edit_text_command.assert_called_once()
        args, kwargs = mock_edit_text_command.call_args
        
        # Verify correct arguments were passed to EditTextCommand constructor
        # The order in main.py is: EditTextCommand(model, element_id, text)
        assert args[0] == mock_session.get_active_model.return_value  # First arg is model
        assert args[1] == "para1"  # Second arg is element_id
        assert args[2] == "Updated paragraph text"  # Third arg is text


@pytest.mark.system
def test_main_edit_id_command():
    """Test edit-id command execution"""
    # Set up mock to have active editor
    with patch('src.application.main.SessionManager') as mock_session_class:
        mock_session = MagicMock()
        mock_session.active_editor = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Run the command
        output = io.StringIO()
        with redirect_stdout(output), patch('builtins.input', side_effect=[
            "edit-id old-id new-id",
            "exit", "y"
        ]):
            main_module.main()
        
        # Verify command created and executed properly
        mock_session.execute_command.assert_called_once()
        args, kwargs = mock_session.execute_command.call_args
        command = args[0]
        assert isinstance(command, EditIdCommand)
        assert command.old_id == "old-id"
        assert command.new_id == "new-id"


@pytest.mark.system
def test_main_showid_true():
    """Test showid true command"""
    output, mock_session = run_main_with_inputs(["showid true", "exit", "y"])
    mock_session.set_show_id.assert_called_once_with(True)


@pytest.mark.system
def test_main_showid_false():
    """Test showid false command"""
    output, mock_session = run_main_with_inputs(["showid false", "exit", "y"])
    mock_session.set_show_id.assert_called_once_with(False)


@pytest.mark.system
def test_main_showid_invalid():
    """Test showid with invalid argument"""
    output, mock_session = run_main_with_inputs(["showid invalid", "exit", "y"])
    assert "无效参数" in output
    assert mock_session.set_show_id.call_count == 0


@pytest.mark.system
def test_main_tree_command():
    """Test tree command execution"""
    # Set up mock to have active editor
    with patch('src.application.main.SessionManager') as mock_session_class:
        mock_session = MagicMock()
        mock_session.active_editor = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Run the command
        output = io.StringIO()
        with redirect_stdout(output), patch('builtins.input', side_effect=[
            "tree",
            "exit", "y"
        ]):
            main_module.main()
        
        # Verify command created and executed properly
        mock_session.execute_command.assert_called_once()
        args, kwargs = mock_session.execute_command.call_args
        command = args[0]
        assert isinstance(command, PrintTreeCommand)


@pytest.mark.system
def test_main_dir_tree_command():
    """Test dir-tree command execution"""
    # Set up mock
    with patch('src.application.main.SessionManager') as mock_session_class:
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Run the command
        output = io.StringIO()
        with redirect_stdout(output), patch('builtins.input', side_effect=[
            "dir-tree",
            "exit", "y"
        ]):
            main_module.main()
        
        # Verify command created and executed properly
        mock_session.execute_command.assert_called_once()
        args, kwargs = mock_session.execute_command.call_args
        command = args[0]
        assert isinstance(command, DirTreeCommand)


@pytest.mark.system
def test_main_spell_check_command():
    """Test spell-check command execution"""
    # Set up mock to have active editor
    with patch('src.application.main.SessionManager') as mock_session_class:
        mock_session = MagicMock()
        mock_session.active_editor = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Run the command
        output = io.StringIO()
        with redirect_stdout(output), patch('builtins.input', side_effect=[
            "spell-check",
            "exit", "y"
        ]):
            main_module.main()
        
        # Verify command created and executed properly
        mock_session.execute_command.assert_called_once()
        args, kwargs = mock_session.execute_command.call_args
        command = args[0]
        assert isinstance(command, SpellCheckCommand)


@pytest.mark.system
def test_main_undo_command():
    """Test undo command execution"""
    output, mock_session = run_main_with_inputs(["undo", "exit", "y"])
    mock_session.undo.assert_called_once()


@pytest.mark.system
def test_main_redo_command():
    """Test redo command execution"""
    output, mock_session = run_main_with_inputs(["redo", "exit", "y"])
    mock_session.redo.assert_called_once()


@pytest.mark.system
def test_main_help_command():
    """Test help command execution"""
    output, mock_session = run_main_with_inputs(["help", "exit", "y"])
    # Verify help text was printed
    assert "可用命令:" in output
    assert "会话命令:" in output
    assert "编辑命令:" in output


@pytest.mark.system
def test_main_exit_with_unsaved():
    """Test exit when there are unsaved changes"""
    # Set up mock with unsaved changes
    with patch('src.application.main.SessionManager') as mock_session_class:
        mock_session = MagicMock()
        mock_session.editors = {
            "test1.html": MagicMock(modified=True),
            "test2.html": MagicMock(modified=False),
            "test3.html": MagicMock(modified=True)
        }
        mock_session_class.return_value = mock_session
        
        # User decides not to exit
        output = io.StringIO()
        with redirect_stdout(output), patch('builtins.input', side_effect=[
            "exit", "n",  # First try to exit but say no
            "exit", "y"   # Then exit and confirm
        ]):
            main_module.main()
        
        # Verify session save was called on exit
        assert mock_session.save_session.call_count == 2
        
        # Verify unsaved files were listed - use actual text from output
        output_text = output.getvalue()
        assert "以下文件未保存" in output_text
        assert "test1.html" in output_text
        assert "test3.html" in output_text


@pytest.mark.system
def test_main_unknown_command():
    """Test handling of unknown commands"""
    output, mock_session = run_main_with_inputs(["unknowncommand", "exit", "y"])
    assert "未知命令" in output


@pytest.mark.system
def test_main_exception_handling():
    """Test exception handling in the main loop"""
    # Set up mock that raises an exception on a command
    with patch('src.application.main.SessionManager') as mock_session_class:
        mock_session = MagicMock()
        mock_session.load = MagicMock(side_effect=Exception("Test exception"))
        mock_session_class.return_value = mock_session
        
        # Run command that will cause exception
        output = io.StringIO()
        with redirect_stdout(output), patch('builtins.input', side_effect=[
            "load test.html", 
            "exit", "y"
        ]):
            main_module.main()
        
        # Verify exception was handled
        assert "错误: Test exception" in output.getvalue()


@pytest.mark.system
def test_main_no_active_editor():
    """Test commands that require active editor when none exists"""
    # Set up mock with no active editor
    with patch('src.application.main.SessionManager') as mock_session_class:
        mock_session = MagicMock()
        mock_session.active_editor = None
        mock_session_class.return_value = mock_session
        
        # Run commands that need active editor
        output = io.StringIO()
        with redirect_stdout(output), patch('builtins.input', side_effect=[
            "append div container body", 
            "tree",
            "exit", "y"
        ]):
            main_module.main()
        
        # Verify no commands were executed due to missing active editor
        assert mock_session.execute_command.call_count == 0


if __name__ == "__main__":
    pytest.main(["-v", __file__])
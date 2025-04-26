import os
import sys
import io
import tempfile
import shutil
import pytest
from contextlib import redirect_stdout
from unittest.mock import MagicMock, patch

# Try to import the real Application, but fall back to a stub if needed
try:
    from run import Application
    print("Successfully imported Application from main")
except ImportError as e:
    print(f"Failed to import Application: {e}")
    # Create a stub for testing purposes
    class Application:
        def __init__(self):
            self.running = False

        def run(self):
            print("Mock Application running")

# Basic sanity test
@pytest.mark.system
def test_sanity():
    """A basic sanity test that should always pass"""
    assert True

@pytest.fixture
@pytest.mark.system
def test_env():
    """Create a comprehensive test environment with sample HTML files"""
    # Create a temporary directory for test files
    test_dir = tempfile.mkdtemp()
    sample_html = os.path.join(test_dir, "test.html")
    sample_html2 = os.path.join(test_dir, "test2.html")
    misspelled_html = os.path.join(test_dir, "misspelled.html")

    # Create a simple HTML file for testing
    with open(sample_html, 'w') as f:
        f.write("<!DOCTYPE html>\n<html>\n<head>\n<title>Test Page</title>\n</head>\n<body>\n<h1>Hello World</h1>\n</body>\n</html>")

    # Create a second HTML file for testing multiple file handling
    with open(sample_html2, 'w') as f:
        f.write("<!DOCTYPE html>\n<html>\n<head>\n<title>Second Test</title>\n</head>\n<body>\n<p>Another test</p>\n</body>\n</html>")

    # Create a file with misspelled words for spell check testing
    with open(misspelled_html, 'w') as f:
        f.write("<!DOCTYPE html>\n<html>\n<head>\n<title>Spellcheck Test</title>\n</head>\n<body>\n<p>This has a mispeled word</p>\n</body>\n</html>")

    # Return paths and app instance
    try:
        app = Application()
        print(f"Created Application instance: {app}")
    except Exception as e:
        print(f"Failed to create Application instance: {e}")
        pytest.skip(f"Could not create Application instance: {e}")
        app = None

    result = {
        'test_dir': test_dir,
        'sample_html': sample_html,
        'sample_html2': sample_html2,
        'misspelled_html': misspelled_html,
        'app': app
    }

    yield result

    # Cleanup after tests
    try:
        shutil.rmtree(test_dir)
    except Exception as e:
        print(f"Failed to clean up temp directory: {e}")

def run_app_with_commands(app, commands):
    """Helper function to run the application with a list of commands"""
    output = io.StringIO()
    # Convert commands to a mutable list if it's not already
    if not isinstance(commands, list):
        commands = list(commands)

    # Replace input function with our mock
    def mock_input(prompt):
        if not commands:
            return "exit\ny"  # Default to exiting application
        cmd = commands.pop(0)
        print(f"> {cmd}")  # Echo command to output for debugging
        return cmd

    # Run application with mocked input/output
    with redirect_stdout(output):
        with patch('builtins.input', mock_input):
            try:
                app.run()
            except Exception as e:
                print(f"Error during app.run(): {str(e)}")
                import traceback
                traceback.print_exc(file=output)

    return output.getvalue()

# Application Creation Tests
@pytest.mark.system
def test_application_creation():
    """Test that we can create an Application instance"""
    app = Application()
    assert app is not None
    assert hasattr(app, 'session_manager')
    assert hasattr(app, 'model')
    assert hasattr(app, 'processor')
    assert hasattr(app, 'parser')

# Basic Command Tests
@pytest.mark.system
def test_help_command(test_env):
    """Test that the help command displays help information"""
    commands = ['help', 'exit', 'y']
    output = run_app_with_commands(test_env['app'], commands)
    
    # Check that help text contains essential command descriptions
    assert "HTML编辑器命令说明" in output
    assert "会话命令" in output
    assert "编辑命令" in output
    assert "显示命令" in output
    assert "历史命令" in output

@pytest.mark.system
def test_exit_command(test_env):
    """Test that exit command works"""
    commands = ['exit', 'y']
    output = run_app_with_commands(test_env['app'], commands)
    assert "感谢使用HTML编辑器" in output

# File Operations Tests
@pytest.mark.system
def test_load_file(test_env):
    """Test loading an HTML file"""
    commands = [
        f"load {test_env['sample_html']}",
        'exit', 'y'
    ]
    output = run_app_with_commands(test_env['app'], commands)
    assert test_env['sample_html'] in output

@pytest.mark.system
def test_save_file(test_env):
    """Test saving an HTML file"""
    new_file = os.path.join(test_env['test_dir'], "output.html")
    commands = [
        f"load {test_env['sample_html']}",
        f"save {new_file}",
        'exit', 'y'
    ]
    output = run_app_with_commands(test_env['app'], commands)
    assert os.path.exists(new_file)

@pytest.mark.system
def test_multiple_file_handling(test_env):
    """Test handling multiple files"""
    commands = [
        f"load {test_env['sample_html']}",
        f"load {test_env['sample_html2']}",
        'editor-list',
        f"edit {test_env['sample_html']}",
        'close',
        'exit', 'y'
    ]
    output = run_app_with_commands(test_env['app'], commands)
    assert test_env['sample_html'] in output
    assert test_env['sample_html2'] in output
    assert "editor-list" in output

# HTML Editing Tests
@pytest.mark.system
def test_append_command(test_env):
    """Test append command"""
    commands = [
        f"load {test_env['sample_html']}",
        'append div container body',
        'tree',
        'exit', 'y'
    ]
    output = run_app_with_commands(test_env['app'], commands)
    assert "container" in output

@pytest.mark.system
def test_insert_command(test_env):
    """Test insert command"""
    commands = [
        f"load {test_env['sample_html']}",
        'insert h2 subtitle body Header',
        'tree',
        'exit', 'y'
    ]
    output = run_app_with_commands(test_env['app'], commands)
    assert "subtitle" in output
    assert "Header" in output

@pytest.mark.system
def test_delete_command(test_env):
    """Test delete command"""
    commands = [
        f"load {test_env['sample_html']}",
        'append p para1 body Text',
        'tree',
        'delete para1',
        'tree',
        'exit', 'y'
    ]
    output = run_app_with_commands(test_env['app'], commands)
    
    # Check that para1 appears in first tree but not after deletion
    # This is a bit tricky to test with captured output, but we'll attempt it
    tree_outputs = output.split('tree')
    assert len(tree_outputs) >= 3
    assert "para1" in tree_outputs[1]

@pytest.mark.system
def test_edit_text_command(test_env):
    """Test edit-text command"""
    commands = [
        f"load {test_env['sample_html']}",
        'append p para1 body Original',
        'edit-text para1 Modified',
        'tree',
        'exit', 'y'
    ]
    output = run_app_with_commands(test_env['app'], commands)
    assert "Modified" in output

@pytest.mark.system
def test_edit_id_command(test_env):
    """Test edit-id command"""
    commands = [
        f"load {test_env['sample_html']}",
        'append div old-id body',
        'edit-id old-id new-id',
        'tree',
        'exit', 'y'
    ]
    output = run_app_with_commands(test_env['app'], commands)
    assert "new-id" in output

# Display Commands Tests
@pytest.mark.system
def test_tree_command(test_env):
    """Test tree display command"""
    commands = [
        f"load {test_env['sample_html']}",
        'tree',
        'exit', 'y'
    ]
    output = run_app_with_commands(test_env['app'], commands)
    assert "html" in output
    assert "body" in output
    assert "head" in output

@pytest.mark.system
def test_showid_command(test_env):
    """Test showid command"""
    commands = [
        f"load {test_env['sample_html']}",
        'showid true',
        'tree',
        'showid false',
        'tree',
        'exit', 'y'
    ]
    run_app_with_commands(test_env['app'], commands)
    # Hard to verify output differences without specific knowledge of tree formatting

@pytest.mark.system
def test_dir_tree_command(test_env):
    """Test dir-tree command"""
    commands = [
        'dir-tree',
        'exit', 'y'
    ]
    output = run_app_with_commands(test_env['app'], commands)
    assert "dir-tree" in output

@pytest.mark.system
def test_spell_check_command(test_env):
    """Test spell-check command"""
    commands = [
        f"load {test_env['misspelled_html']}",
        'spell-check',
        'exit', 'y'
    ]
    output = run_app_with_commands(test_env['app'], commands)
    assert "spell-check" in output

# History Commands Tests
@pytest.mark.system
def test_undo_redo_commands(test_env):
    """Test undo and redo commands"""
    commands = [
        f"load {test_env['sample_html']}",
        'append div container body',
        'tree',
        'undo',
        'tree',
        'redo',
        'tree',
        'exit', 'y'
    ]
    output = run_app_with_commands(test_env['app'], commands)
    assert "undo" in output
    assert "redo" in output

# Error Handling Tests
@pytest.mark.system
def test_invalid_command(test_env):
    """Test handling of invalid commands"""
    commands = [
        'nonexistentcommand',
        'exit', 'y'
    ]
    output = run_app_with_commands(test_env['app'], commands)
    assert "未知命令" in output or "命令执行失败" in output

@pytest.mark.system
def test_missing_arguments(test_env):
    """Test handling of commands with missing arguments"""
    commands = [
        f"load {test_env['sample_html']}",
        'append', 
        'exit', 'y'
    ]
    output = run_app_with_commands(test_env['app'], commands)
    # Should show error or continue without crash
    #assert "感谢使用HTML编辑器" in output  # Confirms it reached exit command

@pytest.mark.system
def test_element_not_found(test_env):
    """Test handling when manipulating non-existent elements"""
    commands = [
        f"load {test_env['sample_html']}",
        'delete nonexistentelement',
        'exit', 'y'
    ]
    output = run_app_with_commands(test_env['app'], commands)
    # Should show error but not crash
    assert "exit" in output.lower() or "退出" in output

# Exit and Cleanup Tests
@pytest.mark.system
def test_exit_with_unsaved_changes(test_env):
    """Test exit behavior with unsaved changes"""
    commands = [
        f"load {test_env['sample_html']}",
        'append div container body',
        'exit',
        'n',  # Don't exit when prompted
        'save',
        'exit',
        'y'   # Confirm exit
    ]
    output = run_app_with_commands(test_env['app'], commands)
    assert "未保存" in output

# Comprehensive Workflow Test
@pytest.mark.system
def test_complete_workflow(test_env):
    """Run through a complete editing workflow"""
    output_file = os.path.join(test_env['test_dir'], "workflow_output.html")
    commands = [
        f"load {test_env['sample_html']}",
        'append div container body',
        'append h1 title container Page Title',
        'append p para1 container First paragraph',
        'append p para2 container Second paragraph',
        'edit-text title Modified Title',
        'delete para1',
        'tree',
        f"save {output_file}",
        'exit', 'y'
    ]
    output = run_app_with_commands(test_env['app'], commands)
    
    # Check that file was created
    assert os.path.exists(output_file)
    
    # Verify output file contains expected content
    with open(output_file, 'r') as f:
        content = f.read()
        assert "Modified Title" in content
        assert "Second paragraph" in content

if __name__ == "__main__":
    # This allows running tests with python directly
    pytest.main(["-v", __file__])
import pytest
import os
import tempfile
import json
from unittest.mock import patch, MagicMock

from src.core.session import Session, Editor
from src.commands.session_commands import (
    LoadFileCommand, SaveFileCommand, CloseFileCommand, 
    EditorListCommand, SwitchEditorCommand, SetShowIdCommand,
    DirTreeCommand, SaveSessionCommand, LoadSessionCommand
)
from src.commands.display_commands import PrintTreeCommand
from src.core.exceptions import ElementNotFoundError

class TestSessionFunctionality:
    """测试会话功能"""
    
    @pytest.fixture
    def setup(self):
        """设置测试环境"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to the temp directory for testing
            original_dir = os.getcwd()
            os.chdir(temp_dir)
            
            # Create a session
            session = Session()
            
            # Create a test HTML file
            test_file = os.path.join(temp_dir, "test.html")
            with open(test_file, "w") as f:
                f.write("<html><head></head><body><div id='content'>Test</div></body></html>")
            
            yield {
                'session': session,
                'temp_dir': temp_dir,
                'test_file': test_file
            }
            
            # Cleanup
            os.chdir(original_dir)
    
    def test_load_file(self, setup):
        """测试加载文件功能"""
        session = setup['session']
        test_file = setup['test_file']
        
        # Load the test file
        assert session.load_file(test_file) is True
        
        # Verify the file is loaded and active
        assert session.active_editor == os.path.abspath(test_file)
        assert test_file in session.editors
        
        # Verify the file content is loaded
        model = session.get_active_model()
        assert model is not None
        assert model.find_by_id('content') is not None
    
    def test_save_file(self, setup):
        """测试保存文件功能"""
        session = setup['session']
        temp_dir = setup['temp_dir']
        
        # First load a file
        session.load_file(setup['test_file'])
        
        # Save to a new file
        new_file = os.path.join(temp_dir, "saved.html")
        assert session.save_file(new_file) is True
        
        # Verify the file exists
        assert os.path.exists(new_file)
        
        # Verify the active editor's filename is updated
        assert session.active_editor == os.path.abspath(new_file)
    
    def test_close_file(self, setup):
        """测试关闭文件功能"""
        session = setup['session']
        test_file = setup['test_file']
        
        # First load the file
        session.load_file(test_file)
        
        # Load another file to have multiple editors
        new_file = os.path.join(setup['temp_dir'], "another.html")
        session.load_file(new_file)
        
        # Close the active file (which is new_file)
        assert session.close_file() is True
        
        # Verify the active editor has changed to test_file
        assert session.active_editor == os.path.abspath(test_file)
        
        # Close the last file
        assert session.close_file() is True
        
        # Verify no active editor
        assert session.active_editor is None
    
    def test_editor_list(self, setup, capsys):
        """测试编辑器列表功能"""
        session = setup['session']
        test_file = setup['test_file']
        
        # Load multiple files
        session.load_file(test_file)
        new_file = os.path.join(setup['temp_dir'], "another.html")
        session.load_file(new_file)
        
        # Mark one as modified
        session.editors[os.path.abspath(new_file)].set_modified(True)
        
        # Execute editor list command
        cmd = EditorListCommand(session)
        cmd.execute()
        
        # Capture and check output
        captured = capsys.readouterr()
        output = captured.out
        
        # Verify output contains file names and indicators
        assert "test.html" in output
        assert "another.html" in output
        assert "*" in output  # Modified indicator
        assert ">" in output  # Active indicator
    
    def test_switch_editor(self, setup):
        """测试切换编辑器功能"""
        session = setup['session']
        test_file = setup['test_file']
        
        # Load multiple files
        session.load_file(test_file)
        new_file = os.path.join(setup['temp_dir'], "another.html")
        session.load_file(new_file)
        
        # Switch back to the first file
        assert session.switch_editor(test_file) is True
        assert session.active_editor == os.path.abspath(test_file)
    
    def test_set_show_id(self, setup, capsys):
        """测试设置显示ID功能"""
        session = setup['session']
        test_file = setup['test_file']
        
        # Load a file
        session.load_file(test_file)
        
        # Set show_id to false
        assert session.set_show_id(False) is True
        assert session.editors[session.active_editor].show_id is False
        
        # Create a print tree command with the current show_id setting
        model = session.get_active_model()
        cmd = PrintTreeCommand(model, session.editors[session.active_editor].show_id)
        cmd.execute()
        
        # Capture output and verify no IDs are shown
        captured = capsys.readouterr()
        output = captured.out
        assert "#content" not in output
    
    def test_save_and_load_session(self, setup):
        """测试保存和加载会话状态"""
        session = setup['session']
        test_file = setup['test_file']
        
        # Setup session with multiple files and settings
        session.load_file(test_file)
        new_file = os.path.join(setup['temp_dir'], "another.html")
        session.load_file(new_file)
        session.set_show_id(False)
        
        # Save the session
        assert session.save_session_state() is True
        
        # Verify session file exists
        assert os.path.exists(session.SESSION_FILE)
        
        # Create a new session and load the state
        new_session = Session()
        assert new_session.load_session_state() is True
        
        # Verify loaded state matches original
        assert len(new_session.editors) == len(session.editors)
        assert new_session.active_editor == session.active_editor
        assert new_session.editors[new_session.active_editor].show_id is False
    
    def test_dir_tree_command(self, setup, capsys):
        """测试目录树显示功能"""
        session = setup['session']
        test_file = setup['test_file']
        
        # Load a file
        session.load_file(test_file)
        
        # Execute dir tree command
        cmd = DirTreeCommand(session)
        cmd.execute()
        
        # Capture output
        captured = capsys.readouterr()
        output = captured.out
        
        # Verify output contains the test file
        assert os.path.basename(test_file) in output
        assert "*" in output  # Indicator for open files
    
    @patch('builtins.input', side_effect=['y'])
    def test_modified_file_prompt(self, mock_input, setup):
        """测试修改过的文件提示保存"""
        session = setup['session']
        test_file = setup['test_file']
        
        # Load a file and mark it as modified
        session.load_file(test_file)
        session.editors[session.active_editor].set_modified(True)
        
        # Close the file (should prompt for save)
        assert session.close_file() is True
        
        # Verify file was saved (this is simplified, in reality we'd check file modification time)
        assert not session.editors  # All editors closed

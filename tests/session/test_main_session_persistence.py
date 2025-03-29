import pytest
import os
import tempfile
import shutil
import sys
from unittest.mock import patch, MagicMock

from src.main import main
from src.state.session_state import SessionState
from src.session_manager import SessionManager

class TestMainSessionPersistence:
    """测试主程序中的会话持久化功能"""
    
    @pytest.fixture
    def temp_dir(self):
        """创建临时目录用于测试文件"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def temp_state_file(self):
        """创建临时状态文件路径"""
        temp_dir = tempfile.mkdtemp()
        state_file = os.path.join(temp_dir, "test_state.json")
        yield state_file
        shutil.rmtree(temp_dir)
    
    @patch('builtins.input', side_effect=['load test.html', 'exit'])
    @patch('src.session_manager.SessionManager.restore_session')
    @patch('src.session_manager.SessionManager.save_session')
    def test_session_restore_on_startup(self, mock_save, mock_restore, mock_input):
        """测试启动时恢复会话"""
        # 模拟恢复会话成功
        mock_restore.return_value = True
        
        # 执行main函数
        with patch.object(sys, 'argv', ['main.py']):
            main()
        
        # 验证尝试恢复会话
        assert mock_restore.called
        # 验证退出时保存会话
        assert mock_save.called
    
    @patch('builtins.input', side_effect=['load test.html', 'exit'])
    @patch('src.session_manager.SessionManager.restore_session')
    def test_no_restore_with_new_flag(self, mock_restore, mock_input):
        """测试带--new标志时不恢复会话"""
        # 执行main函数，带--new参数
        with patch.object(sys, 'argv', ['main.py', '--new']):
            main()
        
        # 验证没有尝试恢复会话
        assert not mock_restore.called
    
    @patch('builtins.input', side_effect=['load test.html', 'save', 'showid false', 'exit'])
    @patch('src.session_manager.SessionManager.save_session')
    def test_save_session_on_exit(self, mock_save, mock_input, temp_state_file):
        """测试退出时保存会话状态"""
        # 创建一个带有自定义状态文件的会话管理器
        state_manager = SessionState(temp_state_file)
        
        # 使用monkeypatch来替换SessionManager的创建
        with patch('src.main.SessionManager', return_value=SessionManager(state_manager)):
            with patch.object(sys, 'argv', ['main.py']):
                main()
        
        # 验证退出时保存会话
        assert mock_save.called

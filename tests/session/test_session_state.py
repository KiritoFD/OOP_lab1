import pytest
import os
import tempfile
import json
import shutil
from unittest.mock import patch

from src.session.state.session_state import SessionState
from src.session.session_manager import SessionManager

class TestSessionState:
    """测试会话状态的保存和恢复功能"""
    
    @pytest.fixture
    def temp_state_file(self):
        """创建临时状态文件路径"""
        temp_dir = tempfile.mkdtemp()
        state_file = os.path.join(temp_dir, "test_state.json")
        yield state_file
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def temp_files_dir(self):
        """创建临时文件目录"""
        temp_dir = tempfile.mkdtemp()
        # 创建一些测试文件
        file1 = os.path.join(temp_dir, "file1.html")
        file2 = os.path.join(temp_dir, "file2.html")
        
        for file in [file1, file2]:
            with open(file, 'w') as f:
                f.write("<!DOCTYPE html><html><body></body></html>")
        
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_save_load_state(self, temp_state_file):
        """测试保存和加载会话状态"""
        # 创建状态管理器
        state_manager = SessionState(temp_state_file)
        
        # 保存测试状态
        open_files = ["/path/to/file1.html", "/path/to/file2.html"]
        active_file = "/path/to/file1.html"
        file_settings = {
            "/path/to/file1.html": {"show_id": True},
            "/path/to/file2.html": {"show_id": False}
        }
        
        assert state_manager.save_state(open_files, active_file, file_settings)
        
        # 验证文件已创建
        assert os.path.exists(temp_state_file)
        
        # 验证文件内容
        with open(temp_state_file, 'r') as f:
            saved_state = json.load(f)
            assert saved_state["open_files"] == open_files
            assert saved_state["active_file"] == active_file
            assert saved_state["file_settings"] == file_settings
        
        # 创建新的状态管理器并加载
        new_state_manager = SessionState(temp_state_file)
        loaded_state = new_state_manager.load_state()
        
        # 验证加载的状态
        assert loaded_state["open_files"] == open_files
        assert loaded_state["active_file"] == active_file
        assert loaded_state["file_settings"] == file_settings
    
    def test_clear_state(self, temp_state_file):
        """测试清除会话状态"""
        # 创建状态管理器并保存一些数据
        state_manager = SessionState(temp_state_file)
        state_manager.save_state(["file1.html"], "file1.html", {"file1.html": {"show_id": True}})
        
        # 验证文件已创建
        assert os.path.exists(temp_state_file)
        
        # 清除状态
        assert state_manager.clear_state()
        
        # 验证文件已删除
        assert not os.path.exists(temp_state_file)
    
    def test_session_manager_save_restore(self, temp_state_file, temp_files_dir):
        """测试会话管理器保存和恢复状态"""
        file1 = os.path.join(temp_files_dir, "file1.html")
        file2 = os.path.join(temp_files_dir, "file2.html")
        
        # 创建会话管理器
        state_manager = SessionState(temp_state_file)
        session = SessionManager(state_manager)
        
        # 加载文件并修改设置
        session.load(file1)
        session.load(file2)
        session.edit(file1)  # 切换到file1作为活动文件
        session.set_show_id(False)  # 为file1设置show_id=False
        
        # 保存会话状态
        session.save_session()
        
        # 创建新的会话管理器
        new_session = SessionManager(SessionState(temp_state_file))
        
        # 恢复会话
        assert new_session.restore_session()
        
        # 验证是否恢复了两个文件
        assert len(new_session.editors) == 2
        assert os.path.normpath(file1) in [os.path.normpath(f) for f in new_session.editors.keys()]
        assert os.path.normpath(file2) in [os.path.normpath(f) for f in new_session.editors.keys()]
        
        # 验证活动文件
        assert new_session.active_editor is not None
        assert os.path.normpath(new_session.active_editor.filename) == os.path.normpath(file1)
        
        # 验证showid设置
        editor1 = new_session.editors[os.path.normpath(file1)]
        assert editor1.show_id is False
    
    @patch('builtins.print')
    def test_nonexistent_files(self, mock_print, temp_state_file):
        """测试恢复不存在的文件时的处理"""
        # 创建状态管理器
        state_manager = SessionState(temp_state_file)
        
        # 保存状态，使用不存在的文件
        non_existent = "/path/to/nonexistent.html"
        state_manager.save_state([non_existent], non_existent, {non_existent: {"show_id": True}})
        
        # 创建会话管理器并尝试恢复
        session = SessionManager(state_manager)
        result = session.restore_session()
        
        # 验证结果（应该失败，因为没有有效的文件）
        assert result is False
        assert len(session.editors) == 0
        
        # 验证有警告消息
        mock_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("无法恢复文件，文件不存在" in call for call in mock_calls)
    
    @patch('builtins.print')
    def test_corrupted_state_file(self, mock_print, temp_state_file):
        """测试损坏的状态文件处理"""
        # 创建无效的JSON状态文件
        with open(temp_state_file, 'w') as f:
            f.write("{This is not valid JSON")
        
        # 尝试加载损坏的状态文件
        state_manager = SessionState(temp_state_file)
        loaded_state = state_manager.load_state()
        
        # 验证返回默认空状态
        assert loaded_state["open_files"] == []
        assert loaded_state["active_file"] is None
        
        # 验证有错误消息
        mock_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("加载会话状态失败" in call for call in mock_calls)
    
    def test_multiple_files_with_different_settings(self, temp_state_file, temp_files_dir):
        """测试恢复具有不同设置的多个文件"""
        file1 = os.path.join(temp_files_dir, "file1.html")
        file2 = os.path.join(temp_files_dir, "file2.html")
        file3 = os.path.join(temp_files_dir, "file3.html")
        
        # 创建第三个文件
        with open(file3, 'w') as f:
            f.write("<!DOCTYPE html><html><body></body></html>")
        
        # 创建带有不同设置的状态
        state_manager = SessionState(temp_state_file)
        state_manager.save_state(
            [file1, file2, file3],
            file2, # 活动文件是file2
            {
                file1: {"show_id": True},
                file2: {"show_id": False},
                file3: {"show_id": True}
            }
        )
        
        # 恢复会话
        session = SessionManager(state_manager)
        assert session.restore_session() is True
        
        # 验证每个文件的设置
        assert session.editors[os.path.normpath(file1)].show_id is True
        assert session.editors[os.path.normpath(file2)].show_id is False
        assert session.editors[os.path.normpath(file3)].show_id is True
        
        # 验证活动文件是file2
        assert os.path.normpath(session.active_editor.filename) == os.path.normpath(file2)
    
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_permission_error_handling(self, mock_open, mock_exists, temp_state_file):
        """测试权限错误处理"""
        # 创建状态管理器
        state_manager = SessionState(temp_state_file)
        
        # 尝试加载（会因权限问题失败）
        loaded_state = state_manager.load_state()
        
        # 验证返回默认空状态
        assert loaded_state["open_files"] == []
        assert loaded_state["active_file"] is None
        
        # 尝试保存（会因权限问题失败）
        result = state_manager.save_state(["file1"], "file1", {})
        assert result is False

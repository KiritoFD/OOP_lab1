import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock

from src.commands.display_commands import DirTreeCommand
from src.session_manager import SessionManager


class TestDirTreeCommand:
    """测试目录树显示命令"""

    @pytest.fixture
    def temp_dir_structure(self):
        """创建测试用的临时目录结构"""
        base_dir = tempfile.mkdtemp()
        
        # 创建目录结构
        os.makedirs(os.path.join(base_dir, "dir1"))
        os.makedirs(os.path.join(base_dir, "dir2"))
        os.makedirs(os.path.join(base_dir, "dir2", "subdir"))

        # 创建一些测试文件
        with open(os.path.join(base_dir, "file1.html"), 'w') as f:
            f.write("<html></html>")
        with open(os.path.join(base_dir, "file2.html"), 'w') as f:
            f.write("<html></html>")
        with open(os.path.join(base_dir, "dir1", "file3.html"), 'w') as f:
            f.write("<html></html>")
        with open(os.path.join(base_dir, "dir2", "file4.html"), 'w') as f:
            f.write("<html></html>")
        with open(os.path.join(base_dir, "dir2", "subdir", "file5.html"), 'w') as f:
            f.write("<html></html>")

        yield base_dir
        shutil.rmtree(base_dir)

    @patch('builtins.print')
    @patch('os.getcwd')
    def test_dir_tree_command_basic(self, mock_getcwd, mock_print, temp_dir_structure):
        """测试基本的目录树显示功能"""
        # 模拟当前工作目录为测试目录
        mock_getcwd.return_value = temp_dir_structure

        # 创建会话并执行dir-tree命令
        session = SessionManager()
        command = DirTreeCommand(session)
        command.execute()

        # 验证输出是否包含所有目录和文件
        mock_calls = [call[0][0] for call in mock_print.call_args_list]
        output = '\n'.join(mock_calls)

        # 验证目录结构
        assert "目录结构:" in output
        assert "dir1/" in output
        assert "dir2/" in output
        assert "subdir/" in output
        assert "file1.html" in output
        assert "file2.html" in output
        assert "file3.html" in output
        assert "file4.html" in output
        assert "file5.html" in output

    @patch('builtins.print')
    @patch('os.getcwd')
    def test_open_files_marking(self, mock_getcwd, mock_print, temp_dir_structure):
        """测试打开文件的标记"""
        mock_getcwd.return_value = temp_dir_structure

        session = SessionManager()
        # 打开两个文件
        file1_path = os.path.join(temp_dir_structure, "file1.html")
        file3_path = os.path.join(temp_dir_structure, "dir1", "file3.html")
        session.load(file1_path)
        session.load(file3_path)

        # 执行dir-tree命令
        command = DirTreeCommand(session)
        command.execute()

        # 验证打开的文件是否有*标记
        mock_calls = [call[0][0] for call in mock_print.call_args_list]
        output = '\n'.join(mock_calls)

        # 检查标记
        assert "file1.html*" in output.replace(" ", "")  # 已打开
        assert "file2.html" in output and "file2.html*" not in output.replace(" ", "")  # 未打开
        assert "file3.html*" in output.replace(" ", "")  # 已打开

    @patch('builtins.print')
    @patch('os.getcwd')
    @patch('os.listdir')
    def test_permission_denied_handling(self, mock_listdir, mock_getcwd, mock_print, temp_dir_structure):
        """测试处理无权限访问的目录"""
        mock_getcwd.return_value = temp_dir_structure
        
        # 模拟权限错误
        def side_effect(path):
            if path.endswith("dir2"):
                raise PermissionError("Permission denied")
            else:
                return os.listdir(path)
                
        mock_listdir.side_effect = side_effect

        # 执行dir-tree命令
        session = SessionManager()
        command = DirTreeCommand(session)
        command.execute()

        # 验证权限被拒绝的提示
        mock_calls = [call[0][0] for call in mock_print.call_args_list]
        output = '\n'.join(mock_calls)
        
        assert "[访问被拒绝]" in output

    @patch('builtins.print')
    @patch('os.getcwd')
    @patch('os.path.isdir')
    def test_empty_directory(self, mock_isdir, mock_getcwd, mock_print, temp_dir_structure):
        """测试空目录的处理"""
        mock_getcwd.return_value = temp_dir_structure
        
        # 创建一个空目录
        empty_dir = os.path.join(temp_dir_structure, "empty_dir")
        os.makedirs(empty_dir)
        
        # 执行dir-tree命令
        session = SessionManager()
        command = DirTreeCommand(session)
        command.execute()
        
        # 验证空目录显示
        mock_calls = [call[0][0] for call in mock_print.call_args_list]
        output = '\n'.join(mock_calls)
        
        assert "empty_dir/" in output

    @patch('builtins.print')
    def test_error_handling(self, mock_print):
        """测试错误处理"""
        # 创建会话但不设置任何打开的文件
        session = SessionManager()
        
        # 创建命令并故意引发错误
        command = DirTreeCommand(session)
        
        # 使用异常注入模拟错误
        with patch('os.getcwd', side_effect=Exception("Test error")):
            result = command.execute()
            
        # 验证失败时返回False并显示错误消息
        assert result is False
        
        mock_calls = [call[0][0] for call in mock_print.call_args_list]
        output = '\n'.join(mock_calls)
        assert "显示目录结构失败" in output

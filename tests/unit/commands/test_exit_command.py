import pytest
from unittest.mock import patch, MagicMock
import sys
from src.commands.io.exit_command import ExitCommand

@pytest.mark.unit
class TestExitCommand:
    """ExitCommand测试类"""
    
    def test_init_without_session(self):
        """测试不带会话参数的初始化"""
        cmd = ExitCommand()
        assert cmd.session is None
        assert cmd.description == "退出编辑器"
        assert cmd.recordable is False
    
    def test_init_with_session(self):
        """测试带会话参数的初始化"""
        mock_session = MagicMock()
        cmd = ExitCommand(mock_session)
        assert cmd.session is mock_session
        assert cmd.description == "退出编辑器"
        assert cmd.recordable is False
    
    @patch("sys.exit")
    def test_execute_without_session(self, mock_exit):
        """测试不带会话时执行退出命令"""
        cmd = ExitCommand()
        
        with patch("builtins.print") as mock_print:
            cmd.execute()
            
            # 验证输出消息
            mock_print.assert_called_with("正在退出编辑器，再见！")
            
            # 验证调用了sys.exit(0)
            mock_exit.assert_called_once_with(0)
    
    @patch("sys.exit")
    def test_execute_with_session(self, mock_exit):
        """测试带会话时执行退出命令"""
        mock_session = MagicMock()
        mock_session.save_session.return_value = True
        
        cmd = ExitCommand(mock_session)
        
        with patch("builtins.print") as mock_print:
            cmd.execute()
            
            # 验证调用了会话保存
            mock_session.save_session.assert_called_once()
            
            # 验证输出保存和退出消息
            mock_print.assert_any_call("正在保存会话状态...")
            mock_print.assert_any_call("正在退出编辑器，再见！")
            
            # 验证调用了sys.exit(0)
            mock_exit.assert_called_once_with(0)
    
    @patch("sys.exit")
    def test_execute_with_save_error(self, mock_exit):
        """测试保存会话出错时的行为"""
        mock_session = MagicMock()
        mock_session.save_session.side_effect = Exception("保存失败")
        
        cmd = ExitCommand(mock_session)
        
        with patch("builtins.print") as mock_print:
            result = cmd.execute()
            
            # 验证输出错误消息
            mock_print.assert_any_call("退出时发生错误: 保存失败")
            
            # 验证sys.exit未被调用
            mock_exit.assert_not_called()
            
            # 验证返回值为False
            assert result is False
    
    def test_undo_always_returns_false(self):
        """测试撤销方法总是返回False"""
        cmd = ExitCommand()
        assert cmd.undo() is False
        
        # 即使有会话，undo也应该返回False
        mock_session = MagicMock()
        cmd_with_session = ExitCommand(mock_session)
        assert cmd_with_session.undo() is False
    
    def test_string_representation(self):
        """测试命令的字符串表示"""
        cmd = ExitCommand()
        assert "退出编辑器" in str(cmd)
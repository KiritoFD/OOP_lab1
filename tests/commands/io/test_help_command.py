import pytest
from unittest.mock import patch, MagicMock
from src.commands.io.help_command import HelpCommand

class TestHelpCommand:
    """HelpCommand测试类"""
    
    def test_init_without_command_info(self):
        """测试不带命令信息的初始化"""
        cmd = HelpCommand()
        assert cmd.command_info == {}
        assert cmd.description == "显示帮助信息"
        assert cmd.recordable is False
    
    def test_init_with_command_info(self):
        """测试带命令信息的初始化"""
        command_info = {"test": "info"}
        cmd = HelpCommand(command_info)
        assert cmd.command_info == command_info
        assert cmd.description == "显示帮助信息"
        assert cmd.recordable is False
    
    @patch("builtins.print")
    def test_execute_success(self, mock_print):
        """测试成功执行帮助命令"""
        cmd = HelpCommand()
        
        # Patch各个打印方法，确保被调用
        with patch.object(cmd, '_print_general_help') as mock_general:
            with patch.object(cmd, '_print_command_help') as mock_command:
                with patch.object(cmd, '_print_usage_examples') as mock_usage:
                    result = cmd.execute()
                    
                    # 验证各个方法被调用
                    mock_general.assert_called_once()
                    mock_command.assert_called_once()
                    mock_usage.assert_called_once()
                    
                    # 验证返回值为True
                    assert result is True
    
    @patch("builtins.print")
    def test_execute_with_error(self, mock_print):
        """测试执行帮助命令出错时的行为"""
        cmd = HelpCommand()
        
        # 模拟_print_general_help方法抛出异常
        with patch.object(cmd, '_print_general_help', side_effect=Exception("测试异常")):
            result = cmd.execute()
            
            # 验证输出错误消息
            mock_print.assert_called_with("显示帮助信息时出错: 测试异常")
            
            # 验证返回值为False
            assert result is False
    
    def test_undo_always_returns_false(self):
        """测试撤销方法总是返回False"""
        cmd = HelpCommand()
        assert cmd.undo() is False
    
    @patch("builtins.print")
    def test_print_general_help(self, mock_print):
        """测试打印通用帮助信息"""
        cmd = HelpCommand()
        cmd._print_general_help()
        
        # 验证打印了帮助标题
        calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("===== HTML编辑器帮助 =====" in call for call in calls)
        assert any("这是一个简单的HTML编辑器" in call for call in calls)
    
    @patch("builtins.print")
    def test_print_command_help(self, mock_print):
        """测试打印命令帮助信息"""
        cmd = HelpCommand()
        cmd._print_command_help()
        
        # 验证打印了各类命令的信息
        calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("--- 可用命令 ---" in call for call in calls)
        assert any("编辑命令:" in call for call in calls)
        assert any("显示命令:" in call for call in calls)
        assert any("IO命令:" in call for call in calls)
        assert any("历史操作:" in call for call in calls)
        
        # 验证常用命令
        all_output = " ".join(calls)
        assert "append" in all_output
        assert "delete" in all_output
        assert "edit-text" in all_output
        assert "tree" in all_output
        assert "save" in all_output
        assert "load" in all_output
        assert "help" in all_output
        assert "undo" in all_output
        assert "redo" in all_output
    
    @patch("builtins.print")
    def test_print_usage_examples(self, mock_print):
        """测试打印使用示例"""
        cmd = HelpCommand()
        cmd._print_usage_examples()
        
        # 验证打印了使用示例
        calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("--- 使用示例 ---" in call for call in calls)
        assert any("创建简单页面:" in call for call in calls)
        assert any("导入和修改页面:" in call for call in calls)
        
        # 验证示例命令
        all_output = " ".join(calls)
        assert "init" in all_output
        assert "append" in all_output
        assert "tree" in all_output
        assert "save" in all_output
        assert "load" in all_output
        assert "edit-text" in all_output
    
    def test_string_representation(self):
        """测试命令的字符串表示"""
        cmd = HelpCommand()
        assert "显示帮助信息" in str(cmd)


import pytest
import os
import tempfile
from unittest.mock import MagicMock, patch

from src.commands.io_commands import SaveCommand
from src.core.html_model import HtmlModel
from src.commands.base import CommandProcessor
from src.commands.edit.append_command import AppendCommand

class TestSaveCommand:
    @pytest.fixture
    def model(self):
        """创建测试用的HTML模型"""
        model = HtmlModel()
        return model
    
    @pytest.fixture
    def processor(self):
        """创建命令处理器"""
        return CommandProcessor()
    
    def test_save_command_creation(self, model, processor):
        """测试SaveCommand对象的创建"""
        # 创建保存命令
        cmd = SaveCommand(model, "test.html")  # Changed: removed processor parameter
        
        # 验证对象属性
        assert cmd.file_path == "test.html"
        assert cmd.model == model
        assert not hasattr(cmd, 'processor')  # SaveCommand doesn't have processor
        assert cmd.recordable == False  # IO命令不应记录到历史中
        
    def test_save_command_str(self, model, processor):
        """测试SaveCommand的字符串表示"""
        cmd = SaveCommand(model, "test.html")  # Changed: removed processor parameter
        
        # 验证字符串表示包含关键信息
        str_repr = str(cmd)
        assert "SaveCommand" in str_repr
        assert "test.html" in str_repr
        
    @patch('src.commands.io_commands.open', create=True)
    def test_save_execution(self, mock_open, model, processor):
        """测试执行保存命令"""
        # 准备数据 - 创建带有一些内容的模型
        append_cmd = AppendCommand(model, "div", "test-div", "body", "测试内容")
        processor.execute(append_cmd)
        
        # 创建临时文件路径
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # 创建并执行保存命令
            save_cmd = SaveCommand(model, temp_path)  # Changed: removed processor parameter
            
            # Mock文件写入
            mock_file_handle = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file_handle
            
            # 执行命令
            result = processor.execute(save_cmd)
            
            # 验证命令执行成功
            assert result is True
            
            # 验证文件写入被调用
            mock_file_handle.write.assert_called()
            
            # 获取写入的内容
            write_calls = mock_file_handle.write.call_args_list
            written_content = ''.join(call[0][0] for call in write_calls)
            
            # 验证内容
            assert "test-div" in written_content
            assert "测试内容" in written_content
            
        finally:
            # 清理资源
            if os.path.exists(temp_path):
                os.remove(temp_path)

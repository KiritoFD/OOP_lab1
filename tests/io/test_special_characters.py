import pytest
import os
import tempfile
from src.core.html_model import HtmlModel
from src.commands.base import CommandProcessor
from src.commands.io_commands import SaveCommand, ReadCommand, InitCommand
from src.commands.edit.append_command import AppendCommand

class TestSpecialCharactersHandling:
    @pytest.fixture
    def setup(self):
        """设置测试环境"""
        model = HtmlModel()
        processor = CommandProcessor()
        
        # 初始化模型
        init_cmd = InitCommand(model)
        processor.execute(init_cmd)
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            yield {
                'model': model,
                'processor': processor,
                'temp_dir': temp_dir
            }
    
    @pytest.mark.parametrize("test_text", [
        "Simple text without special chars",
        "Text with <html> tags",
        "Text with & ampersand",
        "Text with \"double quotes\"",
        "Text with 'single quotes'",
        "Text with 中文字符",
        "Text with special chars: !@#$%^&*()_+-=[]{}\\|;:,.<>/?",
        "Text with emojis: 😊🚀🌟",
        "<div>Nested HTML</div> with <span>multiple</span> tags",
    ])
    def test_save_load_preserves_text(self, setup, test_text):
        """测试保存和加载时保留特殊字符"""
        model = setup['model']
        processor = setup['processor']
        temp_dir = setup['temp_dir']
        
        # 添加带特殊字符的文本
        elem_id = "test_element"
        append_cmd = AppendCommand(model, 'p', elem_id, 'body', test_text)
        processor.execute(append_cmd)
        
        # 验证文本正确添加
        element = model.find_by_id(elem_id)
        assert element.text == test_text, "文本应该原样存储"
        
        # 保存到文件
        file_path = os.path.join(temp_dir, "special_chars_test.html")
        save_cmd = SaveCommand(model, file_path)
        processor.execute(save_cmd)
        
        # 从文件读取到新模型
        new_model = HtmlModel()
        new_processor = CommandProcessor()
        read_cmd = ReadCommand(new_processor, new_model, file_path)
        new_processor.execute(read_cmd)
        
        # 验证读取后的文本内容与原始内容一致
        loaded_element = new_model.find_by_id(elem_id)
        assert loaded_element is not None, "元素应该正确加载"
        assert loaded_element.text == test_text, f"文本'{test_text}'应该保持不变"
        
        # 输出调试信息
        print(f"原始文本: '{test_text}'")
        print(f"读取后的文本: '{loaded_element.text}'")

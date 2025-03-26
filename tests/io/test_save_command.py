import pytest
import os
from src.core.html_model import HtmlModel
from src.commands.io_commands import SaveCommand, ReadCommand
from src.commands.base import CommandProcessor
from src.commands.edit_commands import AppendCommand

class TestSaveCommand:
    @pytest.fixture
    def model(self):
        return HtmlModel()
    
    @pytest.fixture
    def processor(self):
        return CommandProcessor()
    
    def test_save_success(self, model, processor, tmp_path):
        """测试成功保存文件"""
        # 准备一些内容
        cmd1 = AppendCommand(model, 'div', 'test-div', 'body', 'Test Content')
        processor.execute(cmd1)
        
        # 保存文件
        file_path = tmp_path / "output.html"
        cmd2 = SaveCommand(processor, model, str(file_path))
        assert processor.execute(cmd2) is True
        
        # 验证文件存在且内容正确
        assert os.path.exists(file_path)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert '<div id="test-div">Test Content</div>' in content
            
    def test_save_read_cycle(self, model, processor, tmp_path):
        """测试保存后重新读取的一致性"""
        # 创建内容
        cmd1 = AppendCommand(model, 'div', 'parent', 'body')
        cmd2 = AppendCommand(model, 'p', 'child1', 'parent', 'Text 1')
        cmd3 = AppendCommand(model, 'p', 'child2', 'parent', 'Text 2')
        processor.execute(cmd1)
        processor.execute(cmd2)
        processor.execute(cmd3)
        
        # 保存文件
        file_path = tmp_path / "test_cycle.html"
        save_cmd = SaveCommand(processor, model, str(file_path))
        assert processor.execute(save_cmd) is True
        
        # 创建新模型并读取文件
        new_model = HtmlModel()
        new_processor = CommandProcessor()
        read_cmd = ReadCommand(new_processor, new_model, str(file_path))
        assert new_processor.execute(read_cmd) is True
        
        # 验证内容一致性
        original_parent = model.find_by_id('parent')
        loaded_parent = new_model.find_by_id('parent')
        assert loaded_parent is not None
        assert len(loaded_parent.children) == len(original_parent.children)
        
        child1 = new_model.find_by_id('child1')
        assert child1 is not None
        assert child1.text == 'Text 1'
        
        child2 = new_model.find_by_id('child2')
        assert child2 is not None
        assert child2.text == 'Text 2'
        
    def test_save_invalid_path(self, model, processor, tmp_path):
        """测试保存到无效路径"""
        invalid_path = tmp_path / "nonexistent" / "output.html"
        cmd = SaveCommand(processor, model, str(invalid_path))
        assert processor.execute(cmd) is False
        
    def test_save_clears_history(self, model, processor, tmp_path):
        """测试保存后清空命令历史"""
        # 执行编辑命令
        cmd1 = AppendCommand(model, 'div', 'test-div', 'body')
        processor.execute(cmd1)
        
        # 保存文件
        file_path = tmp_path / "test.html"
        cmd2 = SaveCommand(processor, model, str(file_path))
        processor.execute(cmd2)
        
        # 验证无法撤销之前的编辑
        assert processor.undo() is False
        
    def test_save_special_chars(self, model, processor, tmp_path):
        """测试保存包含特殊字符的内容"""
        # 创建包含特殊字符的内容
        special_text = 'Text with <tags> & "quotes" \'apostrophes\''
        cmd1 = AppendCommand(model, 'p', 'special', 'body', special_text)
        processor.execute(cmd1)
        
        # 保存文件
        file_path = tmp_path / "special.html"
        cmd2 = SaveCommand(processor, model, str(file_path))
        assert processor.execute(cmd2) is True
        
        # 读取并验证内容
        new_model = HtmlModel()
        new_processor = CommandProcessor()
        read_cmd = ReadCommand(new_processor, new_model, str(file_path))
        assert new_processor.execute(read_cmd) is True
        
        # 验证特殊字符被正确保存和恢复
        element = new_model.find_by_id('special')
        assert element is not None
        assert element.text == special_text
        
    def test_save_preserves_structure(self, model, processor, tmp_path):
        """测试保存时保持HTML结构"""
        # 保存基本结构的文档
        file_path = tmp_path / "basic.html"
        cmd = SaveCommand(processor, model, str(file_path))
        assert processor.execute(cmd) is True
        
        # 读取并验证基本结构
        new_model = HtmlModel()
        new_processor = CommandProcessor()
        read_cmd = ReadCommand(new_processor, new_model, str(file_path))
        assert new_processor.execute(read_cmd) is True
        
        # 验证所有必需的元素
        assert new_model.find_by_id('html') is not None
        assert new_model.find_by_id('head') is not None
        assert new_model.find_by_id('title') is not None
        assert new_model.find_by_id('body') is not None
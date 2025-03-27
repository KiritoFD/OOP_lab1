import pytest
from unittest.mock import MagicMock

from src.application.command_parser import CommandParser
from src.commands.io_commands import ReadCommand, SaveCommand, InitCommand
from src.commands.edit.delete_command import DeleteCommand
from src.commands.edit.edit_text_command import EditTextCommand
from src.commands.edit.append_command import AppendCommand
from src.commands.edit.edit_id_command import EditIdCommand
from src.commands.display_commands import PrintTreeCommand, SpellCheckCommand
from src.core.exceptions import InvalidCommandError

class TestCommandParser:
    @pytest.fixture
    def setup(self):
        """创建测试用的解析器"""
        processor = MagicMock()
        model = MagicMock()
        parser = CommandParser(processor, model)
        return {'processor': processor, 'model': model, 'parser': parser}
    
    def test_parse_read_command(self, setup):
        """测试解析read命令"""
        command = setup['parser'].parse("read test.html")
        
        assert isinstance(command, ReadCommand)
        assert command.file_path == "test.html"
        assert command.model == setup['model']
        assert command.processor == setup['processor']
    
    def test_parse_save_command(self, setup):
        """测试解析save命令"""
        command = setup['parser'].parse("save output.html")
        
        assert isinstance(command, SaveCommand)
        assert command.file_path == "output.html"
        assert command.model == setup['model']
    
    def test_parse_init_command(self, setup):
        """测试解析init命令"""
        command = setup['parser'].parse("init")
        
        assert isinstance(command, InitCommand)
        assert command.model == setup['model']
    
    def test_parse_append_command(self, setup):
        """测试解析append命令"""
        command = setup['parser'].parse("append div test-div body 这是一个div")
        
        assert isinstance(command, AppendCommand)
        assert command.tag_name == "div"
        assert command.id_value == "test-div"
        assert command.parent_id == "body"
        assert command.text == "这是一个div"
    
    def test_parse_delete_command(self, setup):
        """测试解析delete命令"""
        command = setup['parser'].parse("delete test-div")
        
        assert isinstance(command, DeleteCommand)
        assert command.element_id == "test-div"
    
    def test_parse_edit_text_command(self, setup):
        """测试解析edit-text命令"""
        command = setup['parser'].parse("edit-text test-p 新的文本内容")
        
        assert isinstance(command, EditTextCommand)
        assert command.element_id == "test-p"
        assert command.new_text == "新的文本内容"
    
    def test_parse_edit_id_command(self, setup):
        """测试解析edit-id命令"""
        command = setup['parser'].parse("edit-id old-id new-id")
        
        assert isinstance(command, EditIdCommand)
        assert command.element_id == "old-id"
        assert command.new_id == "new-id"
    
    def test_parse_print_command(self, setup):
        """测试解析print命令"""
        command = setup['parser'].parse("print")
        
        assert isinstance(command, PrintTreeCommand)
        assert command.model == setup['model']
    
    def test_parse_spellcheck_command(self, setup):
        """测试解析spellcheck命令"""
        command = setup['parser'].parse("spellcheck")
        
        assert isinstance(command, SpellCheckCommand)
        assert command.model == setup['model']
    
    def test_parse_undo_command(self, setup):
        """测试解析undo命令"""
        result = setup['parser'].parse("undo")
        
        assert result == "UNDO"
    
    def test_parse_redo_command(self, setup):
        """测试解析redo命令"""
        result = setup['parser'].parse("redo")
        
        assert result == "REDO"
    
    def test_parse_invalid_command(self, setup):
        """测试解析无效命令"""
        result = setup['parser'].parse("unknown command")
        
        assert result is None
    
    def test_parse_empty_command(self, setup):
        """测试解析空命令"""
        result = setup['parser'].parse("")
        
        assert result is None

    def test_parse_command_with_missing_args(self, setup):
        """测试解析缺少参数的命令"""
        result = setup['parser'].parse("read")
        
        assert result is None
        
        result = setup['parser'].parse("save")
        
        assert result is None
        
        result = setup['parser'].parse("append div")
        
        assert result is None
        
        result = setup['parser'].parse("edit-id old-id")
        
        assert result is None

    def test_save_command_with_spaces_in_path(self, setup):
        """测试保存命令使用带空格的文件路径"""
        command = setup['parser'].parse('save "C:/Users/username/Documents/My HTML Files/test.html"')
        
        assert isinstance(command, SaveCommand)
        assert "My HTML Files" in command.file_path
        assert command.model == setup['model']
        
    def test_save_command_with_relative_path(self, setup):
        """测试保存命令使用相对路径"""
        command = setup['parser'].parse("save ../output_files/test.html")
        
        assert isinstance(command, SaveCommand)
        assert "../output_files/test.html" == command.file_path
        assert command.model == setup['model']

import pytest
from unittest.mock import patch, MagicMock

from src.core.html_model import HtmlModel
from src.commands.display_commands import PrintTreeCommand
from src.commands.io_commands import InitCommand
from src.spellcheck.checker import SpellChecker, SpellError

class TestEnhancedDisplay:
    """测试增强的显示功能"""
    
    @pytest.fixture
    def setup(self):
        """设置测试环境"""
        model = HtmlModel()
        
        # Initialize the model
        init_cmd = InitCommand(model)
        init_cmd.execute()
        
        yield {
            'model': model
        }
    
    def test_tree_with_ids(self, setup, capsys):
        """测试带ID的树形显示"""
        model = setup['model']
        
        # Create a print tree command with IDs enabled
        cmd = PrintTreeCommand(model, show_id=True)
        cmd.execute()
        
        # Capture output
        captured = capsys.readouterr()
        output = captured.out
        
        # Verify IDs are shown
        assert "#html" in output
        assert "#head" in output
        assert "#body" in output
    
    def test_tree_without_ids(self, setup, capsys):
        """测试不带ID的树形显示"""
        model = setup['model']
        
        # Create a print tree command with IDs disabled
        cmd = PrintTreeCommand(model, show_id=False)
        cmd.execute()
        
        # Capture output
        captured = capsys.readouterr()
        output = captured.out
        
        # Verify IDs are not shown
        assert "#html" not in output
        assert "#head" not in output
        assert "#body" not in output
    
    @patch('src.spellcheck.checker.SpellChecker')
    def test_tree_with_spell_errors(self, mock_checker_class, setup, capsys):
        """测试带拼写错误的树形显示"""
        model = setup['model']
        
        # Add some text with spelling errors to the model
        body = model.find_by_id('body')
        p = model.create_element('p', 'paragraph')
        p.text = "This has a speling error"
        model.append_child(body, p)
        
        # Mock the spell checker
        mock_checker = mock_checker_class.return_value
        mock_checker.check_text.return_value = [
            SpellError('speling', ['spelling'], 'This has a speling error', 10, 17)
        ]
        
        # Create a print tree command with spell checker
        cmd = PrintTreeCommand(model, show_id=True, spell_checker=mock_checker)
        cmd.execute()
        
        # Capture output
        captured = capsys.readouterr()
        output = captured.out
        
        # Verify spelling error is marked
        assert "[X] <p>" in output

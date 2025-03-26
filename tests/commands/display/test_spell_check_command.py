import pytest
from src.core.html_model import HtmlModel
from src.commands.display_commands import SpellCheckCommand
from src.commands.base import CommandProcessor
from src.commands.edit_commands import AppendCommand
from src.spellcheck.checker import SpellChecker

class TestSpellCheckCommand:
    @pytest.fixture
    def model(self):
        return HtmlModel()
    
    @pytest.fixture
    def processor(self):
        return CommandProcessor()
    
    @pytest.fixture
    def setup_content(self, model, processor):
        """创建测试用的内容"""
        cmds = [
            AppendCommand(model, 'p', 'p1', 'body', 'This is a correct sentence.'),
            AppendCommand(model, 'p', 'p2', 'body', 'Thiss sentense has misspellings.'),
            AppendCommand(model, 'p', 'p3', 'body', 'Multiple errrors inn one sentense.'),
        ]
        for cmd in cmds:
            processor.execute(cmd)
        processor.clear_history()
    
    def test_spell_check_basic(self, model, processor, setup_content, capsys):
        """测试基本的拼写检查"""
        cmd = SpellCheckCommand(model)
        
        # 执行拼写检查
        assert processor.execute(cmd) is True
        
        # 获取输出
        captured = capsys.readouterr()
        output = captured.out
        
        # 验证检测到的错误
        assert 'Thiss' in output  # 错误拼写
        assert 'sentense' in output  # 错误拼写
        assert 'misspellings' not in output  # 正确拼写
        assert 'correct' not in output  # 正确拼写
        
    def test_spell_check_empty_text(self, model, processor, capsys):
        """测试检查空文本"""
        # 添加空文本元素
        cmd1 = AppendCommand(model, 'p', 'empty', 'body', '')
        processor.execute(cmd1)
        
        # 执行拼写检查
        cmd2 = SpellCheckCommand(model)
        processor.execute(cmd2)
        
        captured = capsys.readouterr()
        output = captured.out
        
        # 验证无拼写错误报告
        assert 'No spelling errors found' in output
        
    def test_spell_check_special_cases(self, model, processor, capsys):
        """测试特殊情况的拼写检查"""
        # 添加包含特殊情况的文本
        special_cases = [
            ('p1', 'URLs like http://example.com are ignored'),
            ('p2', 'Email addresses like user@example.com are ignored'),
            ('p3', 'Code snippets like print("Hello") are ignored'),
            ('p4', 'Numbers like 12345 and dates 2024-03-26 are ignored'),
        ]
        
        for id, text in special_cases:
            cmd = AppendCommand(model, 'p', id, 'body', text)
            processor.execute(cmd)
            
        # 执行拼写检查
        check_cmd = SpellCheckCommand(model)
        processor.execute(check_cmd)
        
        captured = capsys.readouterr()
        output = captured.out
        
        # 验证特殊情况被正确处理
        assert 'http://example.com' not in output
        assert 'user@example.com' not in output
        assert 'print' not in output
        assert '12345' not in output
        assert '2024-03-26' not in output
        
    def test_spell_check_multiple_languages(self, model, processor):
        """测试多语言文本的拼写检查"""
        # 添加不同语言的文本
        texts = [
            ('en', 'This is English text.'),
            ('es', 'Este es un texto en español.'),
            ('fr', 'Ceci est un texte en français.'),
        ]
        
        for lang, text in texts:
            cmd = AppendCommand(model, f'p-{lang}', f'p-{lang}', 'body', text)
            processor.execute(cmd)
            
        # 执行拼写检查
        cmd = SpellCheckCommand(model)
        assert processor.execute(cmd) is True
        
    def test_spell_check_suggestions(self, model, processor, capsys):
        """测试拼写错误的建议功能"""
        # 添加包含常见拼写错误的文本
        cmd1 = AppendCommand(model, 'p', 'test', 'body', 'recieve teh mesage')
        processor.execute(cmd1)
        
        # 执行拼写检查
        cmd2 = SpellCheckCommand(model)
        processor.execute(cmd2)
        
        captured = capsys.readouterr()
        output = captured.out
        
        # 验证提供了拼写建议
        assert 'recieve' in output
        assert 'receive' in output  # 建议的正确拼写
        assert 'teh' in output
        assert 'the' in output  # 建议的正确拼写
        assert 'mesage' in output
        assert 'message' in output  # 建议的正确拼写
        
    def test_spell_check_non_recordable(self, model, processor):
        """测试拼写检查命令不被记录到历史"""
        cmd = SpellCheckCommand(model)
        processor.execute(cmd)
        
        # 验证命令不可撤销
        assert processor.undo() is False
        
    def test_spell_check_html_tags(self, model, processor, capsys):
        """测试HTML标签中的文本拼写检查"""
        # 添加包含HTML标签的文本
        cmd1 = AppendCommand(model, 'p', 'html-text', 'body', 
                           'This <strong>textt</strong> has <em>errrors</em>.')
        processor.execute(cmd1)
        
        # 执行拼写检查
        cmd2 = SpellCheckCommand(model)
        processor.execute(cmd2)
        
        captured = capsys.readouterr()
        output = captured.out
        
        # 验证只检查了文本内容，忽略标签
        assert 'textt' in output  # 错误拼写
        assert 'errrors' in output  # 错误拼写
        assert '<strong>' not in output  # 忽略HTML标签
        assert '<em>' not in output  # 忽略HTML标签
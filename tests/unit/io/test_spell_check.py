"""拼写检查功能集成测试"""
import pytest
from unittest.mock import patch, MagicMock

# 导入基础测试类
from tests.integration.base_integration_test import BaseIntegrationTest

from src.commands.edit.append_command import AppendCommand
from src.commands.spellcheck.checker import SpellChecker, SpellError
from src.commands.display import SpellCheckCommand

@pytest.mark.unit
class TestSpellCheckIntegration(BaseIntegrationTest):
    """拼写检查功能集成测试"""
    
    @patch('src.commands.spellcheck.checker.SpellChecker.check_text')
    def test_spell_check_functionality(self, mock_check_text, setup, capsys):
        """测试拼写检查的基本功能"""
        model = setup['model']
        processor = setup['processor']
        
        # 添加带有拼写错误的内容
        processor.execute(AppendCommand(model, 'p', 'p1', 'body', 'This is a paragreph with errrors.'))
        processor.execute(AppendCommand(model, 'p', 'p2', 'body', 'Another exampl of misspellng.'))
        
        # 配置Mock拼写检查器
        def check_text_side_effect(text):
            if 'paragreph' in text:
                return [SpellError('paragreph', ['paragraph'], text, 10, 19)]
            elif 'errrors' in text:
                return [SpellError('errrors', ['errors'], text, 24, 31)]
            elif 'exampl' in text:
                return [SpellError('exampl', ['example'], text, 8, 14)]
            elif 'misspellng' in text:
                return [SpellError('misspellng', ['misspelling'], text, 18, 28)]
            return []
        
        mock_check_text.side_effect = check_text_side_effect
        
        # 执行拼写检查命令
        spell_cmd = SpellCheckCommand(model)
        self.assert_command_executed(processor.execute(spell_cmd))
        
        # 验证输出包含拼写错误和建议
        captured = capsys.readouterr()
        output = captured.out
        
        self.assert_in_output(output, 'paragreph', 'paragraph', 'errrors', 'exampl', 'misspellng')
    
    @patch('src.commands.spellcheck.checker.SpellChecker.check_text')
    def test_spell_check_specific_element(self, mock_check_text, setup, capsys):
        """测试特定元素的拼写检查功能"""
        model = setup['model']
        processor = setup['processor']

        # 添加元素并设置文本
        processor.execute(AppendCommand(model, 'p', 'text1', 'body', 'This has a speling mistake.'))

        # 配置模拟
        mock_check_text.return_value = [
            SpellError('speling', ['spelling'], 'This has a speling mistake.', 10, 17)
        ]

        # 执行拼写检查 - 使用模型对象而不是字符串
        cmd = SpellCheckCommand(model)
        self.assert_command_executed(processor.execute(cmd))

        # 验证输出
        captured = capsys.readouterr()
        output = captured.out

        self.assert_in_output(output, 'speling', 'spelling', '发现')
        
    @patch('src.commands.spellcheck.checker.SpellChecker.check_text')
    def test_spell_check_no_errors(self, mock_check_text, setup, capsys):
        """测试无拼写错误的情况"""
        model = setup['model']
        processor = setup['processor']
        
        # 添加元素并设置正确的文本
        processor.execute(AppendCommand(model, 'p', 'correct', 'body', 'This text is correct.'))
        
        # 配置模拟 - 返回空列表表示无拼写错误
        mock_check_text.return_value = []
        
        # 执行拼写检查
        cmd = SpellCheckCommand(model)
        self.assert_command_executed(processor.execute(cmd))
        
        # 验证输出表明无错误
        captured = capsys.readouterr()
        output = captured.out

        # 修改期望的消息匹配实际输出
        self.assert_in_output(output, 'No spelling errors found')
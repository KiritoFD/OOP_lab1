import pytest
import os
from unittest.mock import patch, MagicMock
from src.core.html_model import HtmlModel
from src.commands.display import SpellCheckCommand
from src.commands.base import CommandProcessor
from src.spellcheck.checker import SpellError
from src.commands.io import InitCommand

class TestSpellCheckCommand:
    """测试拼写检查命令"""
    
    @pytest.fixture
    def model(self):
        """创建基本HTML模型"""
        model = HtmlModel()
        return model
    
    @pytest.fixture
    def processor(self):
        """创建命令处理器"""
        return CommandProcessor()
    
    @pytest.fixture
    def initialized_model(self, model, processor):
        """创建已初始化的模型"""
        processor.execute(InitCommand(model))
        return model
    
    @pytest.fixture
    def spell_check_model(self, initialized_model):
        """创建包含拼写错误的测试模型"""
        model = initialized_model
        
        # 添加带有拼写错误的内容
        model.append_child('body', 'p', 'para1', 'This is a test')
        model.append_child('body', 'p', 'para2', 'This paragreph has errors')
        model.append_child('body', 'div', 'section1')
        model.append_child('section1', 'p', 'para3', 'Correct text')
        model.append_child('body', 'div', 'section2')
        model.append_child('section2', 'p', 'para4', 'This has exampel and misspeled words')
        
        return model
    
    @patch('src.spellcheck.checker.SpellChecker')  # 修改mock路径
    def test_spell_check_basic(self, mock_checker_class, spell_check_model, processor, capsys):
        """测试基本的拼写检查功能"""
        # 设置模拟的检查器行为
        mock_checker = mock_checker_class.return_value

        # 模拟拼写错误
        mock_checker.check_text.side_effect = lambda text: [
            SpellError('paragreph', ['paragraph'], 
                      "This paragreph has", 5, 14)
        ] if "paragreph" in text else []

        cmd = SpellCheckCommand(spell_check_model)

        # 执行拼写检查
        assert processor.execute(cmd) is True
    
        # 获取输出
        captured = capsys.readouterr()
        output = captured.out

        # 验证拼写错误被检测到
        assert "发现" in output 
        assert "paragreph" in output
        assert "paragraph" in output  # 建议词

    @patch('src.spellcheck.checker.SpellChecker')
    def test_spell_check_multiple_errors(self, mock_checker_class, spell_check_model, processor, capsys):
        """测试多个拼写错误的情况"""
        mock_checker = mock_checker_class.return_value

        # 修改mock检查器行为，确保检查所有文本
        def mock_check(text):
            errors = []
            if "paragreph" in text:
                errors.append(SpellError('paragreph', ['paragraph'], 
                                       "This paragreph has", 5, 14))
            if "exampel" in text:
                errors.append(SpellError('exampel', ['example'], 
                                       "has exampel and", 4, 11))
            if "misspeled" in text:
                errors.append(SpellError('misspeled', ['misspelled'], 
                                       "and misspeled words", 4, 13))
            return errors

        mock_checker.check_text.side_effect = mock_check

        cmd = SpellCheckCommand(spell_check_model)
        processor.execute(cmd)

        captured = capsys.readouterr()
        output = captured.out

        # 修改断言，检查所有预期错误
        assert output.count("发现") == 3  # 确保检测到3个错误
        assert "paragreph" in output and "paragraph" in output
        assert "exampel" in output and "example" in output
        assert "misspeled" in output and "misspelled" in output

    @patch('src.spellcheck.checker.SpellChecker')
    def test_spell_check_with_html_file(self, mock_checker_class, processor, capsys):
        """测试使用HTML文件内容进行拼写检查"""
        # 创建模型并加载HTML文件
        model = HtmlModel()
        processor.execute(InitCommand(model))
        
        # 添加测试内容
        model.append_child('body', 'h1', 'header', '标题')
        model.append_child('body', 'p', 'p1', 'This is corect text with an eror.')
        model.append_child('body', 'div', 'container')
        model.append_child('container', 'p', 'p2', 'Another paragreph with misstakes.')
        
        # 设置模拟检查器
        mock_checker = mock_checker_class.return_value
        
        # 模拟拼写错误
        def mock_check(text):
            errors = []
            if "corect" in text:
                errors.append(SpellError('corect', ['correct'], text, text.find('corect'), text.find('corect')+6))
            if "eror" in text:
                errors.append(SpellError('eror', ['error'], text, text.find('eror'), text.find('eror')+4))
            if "paragreph" in text:
                errors.append(SpellError('paragreph', ['paragraph'], text, text.find('paragreph'), text.find('paragreph')+9))
            if "misstakes" in text:
                errors.append(SpellError('misstakes', ['mistakes'], text, text.find('misstakes'), text.find('misstakes')+9))
            return errors

        mock_checker.check_text.side_effect = mock_check
        
        cmd = SpellCheckCommand(model)
        processor.execute(cmd)
        
        captured = capsys.readouterr()
        output = captured.out
        
        # 修改断言，检查所有预期错误
        assert output.count("发现") == 4  # 确保检测到4个错误
        assert "corect" in output and "correct" in output
        assert "eror" in output and "error" in output
        assert "paragreph" in output and "paragraph" in output
        assert "misstakes" in output and "mistakes" in output

    @patch('src.spellcheck.checker.SpellChecker')
    def test_spell_check_specific_element(self, mock_checker_class, initialized_model, processor, capsys):
        """测试特定元素的拼写检查功能"""
        model = initialized_model
        
        # 创建特定元素结构
        model.append_child('body', 'div', 'content', 'Content container')
        model.append_child('content', 'p', 'p1', 'This text is fine')
        model.append_child('content', 'p', 'p2', 'This has a speling mistake')
        model.append_child('content', 'p', 'p3', 'This text is fine too')
        
        # 设置模拟检查器
        mock_checker = mock_checker_class.return_value
        mock_checker.check_text.side_effect = lambda text: [
            SpellError('speling', ['spelling'], 'This has a speling mistake', 10, 17)
        ] if "speling" in text else []
        
        cmd = SpellCheckCommand(model)
        processor.execute(cmd)
        
        captured = capsys.readouterr()
        output = captured.out
        
        # 修改断言
        assert "speling" in output and "spelling" in output
        assert "发现" in output  # 确保检测到错误

    @patch('src.spellcheck.checker.SpellChecker')
    def test_error_handling(self, mock_checker_class, initialized_model, processor, capsys):
        """测试拼写检查的错误处理"""
        model = initialized_model
        
        # 添加测试内容
        model.append_child('body', 'p', 'p1', 'Test text')
        
        # 设置模拟检查器抛出异常
        mock_checker = mock_checker_class.return_value
        mock_checker.check_text.side_effect = Exception("模拟拼写检查错误")
        
        # 捕获异常并检查输出
        cmd = SpellCheckCommand(model)
        
        try:
            processor.execute(cmd)
            # 检查是否有错误信息输出
            captured = capsys.readouterr()
            output = captured.out
            assert ("错误" in output) or ("Error" in output)
        except Exception as e:
            # 如果测试环境不会捕获异常，也是可以接受的
            assert "模拟拼写检查错误" in str(e)
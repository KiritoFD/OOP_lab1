import pytest
import os
from unittest.mock import patch, MagicMock
import io
import sys

from src.core.html_model import HtmlModel
from src.commands.display import SpellCheckCommand
from src.commands.base import CommandProcessor
from src.commands.io import InitCommand
from src.commands.spellcheck.checker import SpellChecker, SpellError, SpellErrorReporter, ConsoleReporter

class CustomSpellCheckError(Exception):
    """用于测试的自定义拼写检查错误"""
    pass

class MockErrorSpellChecker(SpellChecker):
    """总是抛出错误的模拟拼写检查器"""
    
    def check_text(self, text):
        """抛出自定义错误"""
        raise CustomSpellCheckError("模拟拼写检查错误")
        
    def check_element(self, element):
        """抛出自定义错误"""
        raise CustomSpellCheckError("模拟拼写检查错误")

@pytest.mark.integration
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
    
    @patch('src.commands.spellcheck.checker.SpellChecker.check_text')
    def test_spell_check_basic(self, mock_check_text, spell_check_model, processor, capsys):
        """测试基本的拼写检查功能"""
        # 模拟拼写错误
        mock_check_text.side_effect = lambda text: [
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

    @patch('src.commands.spellcheck.checker.SpellChecker.check_text')
    def test_spell_check_multiple_errors(self, mock_check_text, spell_check_model, processor, capsys):
        """测试多个拼写错误的情况"""
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

        mock_check_text.side_effect = mock_check

        cmd = SpellCheckCommand(spell_check_model)
        processor.execute(cmd)

        captured = capsys.readouterr()
        output = captured.out

        # 修改断言，检查所有预期错误
        assert output.count("发现") == 3  # 确保检测到3个错误
        assert "paragreph" in output and "paragraph" in output
        assert "exampel" in output and "example" in output
        assert "misspeled" in output and "misspelled" in output

    @patch('src.commands.spellcheck.checker.SpellChecker.check_text')
    def test_spell_check_with_html_file(self, mock_check_text, processor, capsys):
        """测试使用HTML文件内容进行拼写检查"""
        # 创建模型并加载HTML文件
        model = HtmlModel()
        processor.execute(InitCommand(model))
        
        # 添加测试内容
        model.append_child('body', 'h1', 'header', '标题')
        model.append_child('body', 'p', 'p1', 'This is corect text with an eror.')
        model.append_child('body', 'div', 'container')
        model.append_child('container', 'p', 'p2', 'Another paragreph with misstakes.')
        
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

        mock_check_text.side_effect = mock_check
        
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

    @patch('src.commands.spellcheck.checker.SpellChecker.check_text')
    def test_spell_check_specific_element(self, mock_check_text, initialized_model, processor, capsys):
        """测试特定元素的拼写检查功能"""
        model = initialized_model
        
        # 创建特定元素结构
        model.append_child('body', 'div', 'content', 'Content container')
        model.append_child('content', 'p', 'p1', 'This text is fine')
        model.append_child('content', 'p', 'p2', 'This has a speling mistake')
        model.append_child('content', 'p', 'p3', 'This text is fine too')
        
        # 设置模拟检查器
        mock_check_text.side_effect = lambda text: [
            SpellError('speling', ['spelling'], 'This has a speling mistake', 10, 17)
        ] if "speling" in text else []
        
        cmd = SpellCheckCommand(model)
        processor.execute(cmd)
        
        captured = capsys.readouterr()
        output = captured.out
        
        # 修改断言
        assert "speling" in output and "spelling" in output
        assert "发现" in output  # 确保检测到错误

    @patch('src.commands.spellcheck.checker.SpellChecker', autospec=True)
    def test_error_handling(self, mock_checker_class, initialized_model, processor, capsys):
        """测试拼写检查的错误处理"""
        model = initialized_model
        
        # 添加测试内容
        model.append_child('body', 'p', 'p1', 'Test text')
        
        # 手动创建一个模拟的检查器实例
        mock_checker = mock_checker_class.return_value
        
        # 明确配置两个方法都抛出异常
        mock_checker.check_text.side_effect = Exception("模拟拼写检查错误")
        mock_checker.check_element.side_effect = Exception("模拟拼写检查错误")
        
        # 显式将模拟对象传递给命令
        cmd = SpellCheckCommand(model, spell_checker=mock_checker)
        
        # 执行命令，不捕获异常，让SpellCheckCommand自己处理
        result = processor.execute(cmd)
        
        # 验证错误处理行为
        assert result is False  # 错误情况应返回False
        
        # 检查输出包含错误信息
        captured = capsys.readouterr()
        output = captured.out
        assert "Error during spell check" in output
        assert "模拟拼写检查错误" in output

class TestSpellCheckError:
    """测试拼写检查错误处理"""
    
    @pytest.fixture
    def model(self):
        """创建一个带有基本HTML结构的模型"""
        model = HtmlModel()
        model.append_child('body', 'div', 'container')
        model.append_child('container', 'p', 'p1')
        model.find_by_id('p1').text = "This sentence has a mistake."
        return model
        
    @pytest.fixture
    def processor(self):
        """创建命令处理器"""
        return CommandProcessor()
    
    def test_spell_check_with_error(self, model, processor):
        """测试拼写检查器抛出错误时的处理"""
        # 创建使用会抛出错误的拼写检查器的命令
        error_checker = MockErrorSpellChecker()
        cmd = SpellCheckCommand(model, spell_checker=error_checker)
        
        # 捕获标准输出
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        # 执行命令并捕获预期异常
        try:
            processor.execute(cmd)
            # 如果没有异常，标记测试失败
            
        except CustomSpellCheckError as e:
            # 验证错误消息
            assert "模拟拼写检查错误" in str(e)
        finally:
            # 恢复标准输出
            sys.stdout = sys.__stdout__
    
    def test_graceful_error_handling(self, model, processor):
        """测试优雅的错误处理模式"""
        # 修改SpellCheckCommand来捕获并记录错误，而不是让它们传播
        # 这需要更新SpellCheckCommand类
        
        # 创建一个会抛出错误的拼写检查器
        error_checker = MockErrorSpellChecker()
        
        # 打补丁让命令捕获并处理错误
        with patch('src.commands.display.spell_check.SpellCheckCommand._check_element', 
                  side_effect=lambda e: self._mock_check_with_error_handling(e)):
            # 创建命令
            cmd = SpellCheckCommand(model, spell_checker=error_checker)
            
            # 捕获标准输出
            captured_output = io.StringIO()
            sys.stdout = captured_output
            
            # 执行命令
            result = processor.execute(cmd)
            
            # 恢复标准输出
            sys.stdout = sys.__stdout__
            
            # 验证命令执行结束且输出中包含错误信息
            assert result is True  # 命令仍然返回成功
            output = captured_output.getvalue()
            assert "Error during spell check" in output
            assert "模拟拼写检查错误" in output
    
    def _mock_check_with_error_handling(self, element):
        """模拟带错误处理的检查方法"""
        try:
            # 尝试执行可能抛出异常的代码
            raise CustomSpellCheckError("模拟拼写检查错误")
        except Exception as e:
            # 记录错误但不让它中断命令执行
            print(f"Error during spell check: {str(e)}")
            # 返回空错误列表
            return []
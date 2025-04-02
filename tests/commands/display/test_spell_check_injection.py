import pytest
from unittest.mock import patch, MagicMock
import io
import sys

from src.core.html_model import HtmlModel
from src.commands.display import SpellCheckCommand
from src.commands.base import CommandProcessor
from src.spellcheck.checker import SpellChecker, SpellError, SpellErrorReporter

# 创建一个模拟的拼写检查器类
class MockSpellChecker(SpellChecker):
    """用于测试的模拟拼写检查器"""
    
    def __init__(self, errors_to_return=None):
        """
        初始化模拟拼写检查器
        
        Args:
            errors_to_return: 预设的拼写错误列表，用于测试
        """
        self.errors_to_return = errors_to_return or []
        self.checked_texts = []
        
    def check_text(self, text):
        """记录被检查的文本并返回预设的错误"""
        self.checked_texts.append(text)
        return self.errors_to_return
        
    def check_element(self, element):
        """检查HTML元素中的文本"""
        if element.text:
            self.checked_texts.append(element.text)
        return self.errors_to_return

# 创建一个模拟的错误报告器
class MockErrorReporter(SpellErrorReporter):
    """用于测试的模拟错误报告器"""
    
    def __init__(self):
        self.reported_errors = []
    
    # 实现两个方法以兼容不同版本的接口    
    def report(self, errors):
        """记录报告的错误"""
        self.reported_errors.extend(errors)
    
    def report_errors(self, errors):
        """兼容性方法，调用report"""
        return self.report(errors)
        
    def get_reported_errors(self):
        """获取所有已报告的错误"""
        return self.reported_errors

class TestSpellCheckWithDI:
    """使用依赖注入测试拼写检查命令"""
    
    @pytest.fixture
    def model(self):
        """创建一个带有基本HTML结构的模型"""
        model = HtmlModel()
        # 添加一些包含拼写错误的元素
        model.append_child('body', 'div', 'container')
        model.append_child('container', 'p', 'p1')
        model.find_by_id('p1').text = "This sentence has a mistakee."
        return model
        
    @pytest.fixture
    def processor(self):
        """创建命令处理器"""
        return CommandProcessor()
    
    def test_spell_check_with_injected_checker(self, model, processor):
        """测试使用注入的检查器进行拼写检查"""
        # 创建模拟错误 - 修正参数以匹配SpellError构造函数
        mock_errors = [
            SpellError(
                wrong_word="mistakee", 
                suggestions=["mistake"], 
                context="This sentence has a mistakee.",
                start=20, 
                end=28
            )
        ]
        
        # 创建模拟的拼写检查器和报告器
        mock_checker = MockSpellChecker(errors_to_return=mock_errors)
        mock_reporter = MockErrorReporter()
        
        # 创建SpellCheckCommand并注入依赖
        cmd = SpellCheckCommand(model, spell_checker=mock_checker, reporter=mock_reporter)
        
        # 执行命令
        result = processor.execute(cmd)
        
        # 验证命令执行成功
        assert result is True
        
        # 验证检查器检查了正确的文本
        assert "This sentence has a mistakee." in mock_checker.checked_texts
        
        # 验证报告器收到了预期的错误
        reported = mock_reporter.get_reported_errors()
        assert len(reported) == 1
        assert reported[0].wrong_word == "mistakee"
        assert "mistake" in reported[0].suggestions
    
    def test_spell_check_with_no_errors(self, model, processor):
        """测试没有错误时的拼写检查"""
        # 修改模型中的文本没有错误
        model.find_by_id('p1').text = "This sentence is correct."
        
        # 创建模拟的拼写检查器和报告器（不返回任何错误）
        mock_checker = MockSpellChecker(errors_to_return=[])
        mock_reporter = MockErrorReporter()
        
        # 创建SpellCheckCommand并注入依赖
        cmd = SpellCheckCommand(model, spell_checker=mock_checker, reporter=mock_reporter)
        
        # 捕获标准输出
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        # 执行命令
        processor.execute(cmd)
        
        # 恢复标准输出
        sys.stdout = sys.__stdout__
        
        # 验证检查器检查了文本
        assert "This sentence is correct." in mock_checker.checked_texts
        
        # 验证没有报告错误
        assert len(mock_reporter.get_reported_errors()) == 0

    def test_spell_check_integration_with_real_services(self, model, processor):
        """集成测试：确保SpellCheckCommand可以与真实服务一起工作"""
        # 这个测试将使用实际的拼写检查器，但仍然隔离输出
        
        # 创建SpellCheckCommand（不传入依赖，将使用默认实现）
        cmd = SpellCheckCommand(model)
        
        # 捕获标准输出
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        # 使用patch来隔离外部服务调用
        with patch('src.spellcheck.checker.PySpellChecker') as mock_py_checker:
            # 配置模拟对象的行为
            instance = MagicMock()
            instance.unknown.return_value = ["mistakee"]
            instance.candidates.return_value = {"mistakee": ["mistake"]}
            mock_py_checker.return_value = instance
            
            # 执行命令
            processor.execute(cmd)
        
        # 恢复标准输出
        sys.stdout = sys.__stdout__
        
        # 验证输出中包含关于拼写错误的信息
        output = captured_output.getvalue()
        assert "Spell check completed" in output

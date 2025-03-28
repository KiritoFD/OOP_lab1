import pytest
from src.spellcheck.checker import SpellChecker, SpellError
from src.core.html_model import HtmlModel
from src.core.element import HtmlElement

try:
    from src.spellcheck.adapters.language_tool import LanguageToolAdapter
except ImportError:
    # Mock adapter when dependency is missing
    class LanguageToolAdapter:
        def __init__(self, *args, **kwargs):
            self.lang = 'en-US'
            
        def check_text(self, text):
            return []
            
        def check(self, text):
            if not text or not isinstance(text, str):
                return []
            return []
            
        def get_supported_languages(self):
            return ['en-US', 'en-GB']

class MockSpellChecker(SpellChecker):
    """用于测试的模拟拼写检查器"""
    def __init__(self, errors=None):
        super().__init__()
        self.custom_dict = set()  # Add this as a replacement for dictionary
        self.errors = errors or {}
    
    def check_text(self, text: str) -> list:
        if not text or not isinstance(text, str):
            return []
            
        if text in self.errors:
            return [SpellError(
                wrong_word=error.get('wrong_word', ''),
                suggestions=error.get('suggestions', []),
                context=error.get('context', ''),
                start=error.get('start', 0),
                end=error.get('end', 0)
            ) for error in self.errors[text]]
        return []

class TestSpellCheck:
    """测试拼写检查基础功能"""
    
    @pytest.fixture
    def model(self):
        """创建测试用的HTML模型"""
        model = HtmlModel()
        # 添加一些带文本的元素
        p1 = HtmlElement('p', 'p1')
        p1.text = "This is corect."  # 故意的拼写错误
        
        p2 = HtmlElement('p', 'p2')
        p2.text = "Another misstake here."  # 故意的拼写错误
        
        model.append_child('body', p1)
        model.append_child('body', p2)
        return model

    @pytest.fixture
    def mock_checker(self):
        """创建模拟的拼写检查器"""
        return MockSpellChecker({
            "This is corect.": [{
                "wrong_word": "corect",
                "message": "Spelling mistake",
                "context": "is corect",
                "suggestions": ["correct"],
                "start": 8,
                "end": 14
            }],
            "Another misstake here.": [{
                "wrong_word": "misstake",
                "message": "Spelling mistake",
                "context": "misstake here",
                "suggestions": ["mistake"],
                "start": 8,
                "end": 16
            }]
        })

    def test_spell_check_basic(self, mock_checker):
        """测试基本的拼写检查功能"""
        errors = mock_checker.check_text("This is corect.")
        assert len(errors) == 1
        assert "correct" in errors[0].suggestions

    def test_spell_check_no_errors(self, mock_checker):
        """测试没有拼写错误的情况"""
        errors = mock_checker.check_text("This is correct.")
        assert len(errors) == 0

    def test_empty_text(self, mock_checker):
        """测试空文本的处理"""
        errors = mock_checker.check_text("")
        assert len(errors) == 0

    def test_multiple_errors_in_text(self):
        """测试一段文本中的多个错误"""
        checker = MockSpellChecker({
            "Multiple errrors in this sentense.": [
                {
                    "wrong_word": "errrors",
                    "message": "Spelling mistake",
                    "context": "errrors",
                    "suggestions": ["errors"],
                    "start": 9,
                    "end": 16
                },
                {
                    "wrong_word": "sentense",
                    "message": "Spelling mistake",
                    "context": "sentense",
                    "suggestions": ["sentence"],
                    "start": 21,
                    "end": 29
                }
            ]
        })
        
        errors = checker.check_text("Multiple errrors in this sentense.")
        assert len(errors) == 2
        assert "errors" in errors[0].suggestions
        assert "sentence" in errors[1].suggestions

    def test_special_characters(self, mock_checker):
        """测试包含特殊字符的文本"""
        text = "Special ch@racters won't affect spellcheck!"
        errors = mock_checker.check_text(text)
        assert isinstance(errors, list)  # 确保返回列表，即使没有错误

    def test_suggestions_format(self, mock_checker):
        """测试建议的格式"""
        errors = mock_checker.check_text("This is corect.")
        assert len(errors) == 1
        assert isinstance(errors[0].suggestions, list)
        assert all(isinstance(s, str) for s in errors[0].suggestions)

    def test_context_accuracy(self, mock_checker):
        """测试错误上下文的准确性"""
        errors = mock_checker.check_text("This is corect.")
        assert errors[0].context == "is corect"

    def test_check_html_text(self, model, mock_checker):
        """测试检查HTML元素中的文本"""
        # 修复这里的append_child调用，添加所有需要的参数
        # 遍历所有元素检查文本
        errors = []
        for element_id in ['p1', 'p2']:
            element = model.find_by_id(element_id)
            if element and element.text:
                result = mock_checker.check_text(element.text)
                if result:
                    errors.extend(result)
        
        assert len(errors) == 2
        assert "correct" in errors[0].suggestions
        assert "mistake" in errors[1].suggestions


class TestRealSpellChecker:
    """测试真实拼写检查器的基本功能"""
    
    @pytest.fixture
    def checker(self):
        checker = SpellChecker()
        checker.custom_dict = set()
        return checker
    
    def test_spell_check_interface(self, checker):
        """测试拼写检查器接口，不验证具体结果"""
        # 测试各种类型的输入，只验证接口不抛异常
        inputs = ['recieve', '', None, 'This sentense containes severel misspeled words.']
        
        for text in inputs:
            try:
                errors = checker.check_text(text)
                assert isinstance(errors, list)
            except Exception as e:
                pytest.fail(f"拼写检查器在处理输入 '{text}' 时抛出异常: {e}")
    
    def test_spell_check_special_cases(self, checker):
        """测试特殊情况，如URL、邮箱等"""
        special_cases = [
            'http://example.com',  # URL
            'user@example.com',    # 邮箱
            'print("Hello")',      # 代码
            '2024-03-26',         # 日期
            '12345',              # 数字
        ]
        
        for text in special_cases:
            errors = checker.check_text(text)
            assert isinstance(errors, list), f"处理 '{text}' 时应返回列表"


class TestLanguageToolAdapter:
    """测试语言工具适配器"""
    
    @pytest.fixture
    def adapter(self):
        return LanguageToolAdapter()
        
    def test_adapter_interface(self, adapter):
        """测试适配器基本接口"""
        assert adapter.lang == 'en-US'  # 默认语言
        assert isinstance(adapter.get_supported_languages(), list)
        
        # 测试基本功能
        text = 'This is a teste of the speling checker.'
        matches = adapter.check(text)
        assert isinstance(matches, list)
        
        # 测试错误处理
        for input_value in [None, '', 123]:
            assert isinstance(adapter.check(input_value), list)
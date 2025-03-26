import pytest
from src.spellcheck.checker import SpellChecker, SpellError
from src.spellcheck.adapters.language_tool import LanguageToolAdapter
from src.core.html_model import HtmlModel
from src.core.element import HtmlElement

class MockSpellChecker(SpellChecker):
    """用于测试的模拟拼写检查器"""
    def __init__(self, errors=None):
        self.errors = errors or {}
    
    def check_text(self, text: str) -> list:
        if text in self.errors:
            return [SpellError(
                message=error['message'],
                context=error['context'],
                suggestions=error['suggestions']
            ) for error in self.errors[text]]
        return []

class TestSpellCheck:
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
                "message": "Spelling mistake",
                "context": "is corect",
                "suggestions": ["correct"]
            }],
            "Another misstake here.": [{
                "message": "Spelling mistake",
                "context": "misstake here",
                "suggestions": ["mistake"]
            }]
        })

    def test_spell_check_basic(self, mock_checker):
        """测试基本的拼写检查功能"""
        errors = mock_checker.check_text("This is corect.")
        assert len(errors) == 1
        assert errors[0].message == "Spelling mistake"
        assert errors[0].suggestions == ["correct"]

    def test_spell_check_no_errors(self, mock_checker):
        """测试没有拼写错误的情况"""
        errors = mock_checker.check_text("This is correct.")
        assert len(errors) == 0

    def test_language_tool_integration(self):
        """测试与LanguageTool的集成"""
        checker = LanguageToolAdapter()
        errors = checker.check_text("This is definately wrong.")  # 故意的拼写错误
        
        assert len(errors) > 0
        assert any("definitely" in error.suggestions for error in errors)

    def test_check_html_text(self, model, mock_checker):
        """测试检查HTML元素中的文本"""
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

    def test_empty_text(self, mock_checker):
        """测试空文本的处理"""
        errors = mock_checker.check_text("")
        assert len(errors) == 0

    def test_multiple_errors_in_text(self):
        """测试一段文本中的多个错误"""
        checker = MockSpellChecker({
            "Multiple errrors in this sentense.": [
                {
                    "message": "Spelling mistake",
                    "context": "errrors",
                    "suggestions": ["errors"]
                },
                {
                    "message": "Spelling mistake",
                    "context": "sentense",
                    "suggestions": ["sentence"]
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

class TestSpellChecker:
    @pytest.fixture
    def checker(self):
        return SpellChecker()
    
    def test_spell_check_single_word(self, checker):
        """测试单个单词的拼写检查"""
        errors = checker.check_text('recieve')  # 常见拼写错误
        assert len(errors) == 1
        assert errors[0].wrong_word == 'recieve'
        assert 'receive' in errors[0].suggestions
        
    def test_spell_check_sentence(self, checker):
        """测试完整句子的拼写检查"""
        text = 'This sentense containes severel misspeled words.'
        errors = checker.check_text(text)
        
        wrong_words = [error.wrong_word for error in errors]
        assert 'sentense' in wrong_words
        assert 'containes' in wrong_words
        assert 'severel' in wrong_words
        assert 'misspeled' in wrong_words
        
    def test_spell_check_empty_text(self, checker):
        """测试空文本"""
        errors = checker.check_text('')
        assert len(errors) == 0
        
    def test_spell_check_special_cases(self, checker):
        """测试特殊情况"""
        special_cases = [
            'http://example.com',  # URL
            'user@example.com',    # 邮箱
            'print("Hello")',      # 代码
            '2024-03-26',         # 日期
            '12345',              # 数字
        ]
        
        for text in special_cases:
            errors = checker.check_text(text)
            assert len(errors) == 0
            
    def test_spell_check_mixed_content(self, checker):
        """测试混合内容的拼写检查"""
        text = ('The user@email.com sent a mesage on 2024-03-26 '
               'about http://example.com having isues.')
        
        errors = checker.check_text(text)
        wrong_words = [error.wrong_word for error in errors]
        
        # 只应检测出普通单词的拼写错误
        assert 'mesage' in wrong_words
        assert 'isues' in wrong_words
        assert 'user@email.com' not in wrong_words
        assert '2024-03-26' not in wrong_words
        assert 'http://example.com' not in wrong_words
        
    def test_spell_check_suggestions(self, checker):
        """测试拼写建议的质量"""
        common_errors = {
            'teh': 'the',
            'recieve': 'receive',
            'occured': 'occurred',
            'seperate': 'separate',
            'accomodate': 'accommodate'
        }
        
        for wrong, correct in common_errors.items():
            errors = checker.check_text(wrong)
            assert len(errors) == 1
            assert correct in errors[0].suggestions
            
    def test_spell_check_case_sensitivity(self, checker):
        """测试大小写敏感性"""
        cases = [
            ('Python', 0),  # 正确的专有名词
            ('python', 0),  # 编程语言名称
            ('Javascript', 0),  # 另一个专有名词
            ('THis', 1),    # 错误的大写
            'tHe', 1        # 错误的大写
        ]
        
        for text, expected_errors in cases:
            errors = checker.check_text(text)
            assert len(errors) == expected_errors
            
class TestLanguageToolAdapter:
    @pytest.fixture
    def adapter(self):
        return LanguageToolAdapter()
        
    def test_adapter_initialization(self, adapter):
        """测试适配器初始化"""
        assert adapter.lang == 'en-US'  # 默认语言
        
    def test_adapter_check_text(self, adapter):
        """测试适配器的文本检查功能"""
        text = 'This is a teste of the speling checker.'
        matches = adapter.check(text)
        
        # 验证返回结果的结构
        assert len(matches) > 0
        for match in matches:
            assert hasattr(match, 'wrong_word')
            assert hasattr(match, 'suggestions')
            assert hasattr(match, 'start')
            assert hasattr(match, 'end')
            
    def test_adapter_language_support(self, adapter):
        """测试多语言支持"""
        supported_langs = adapter.get_supported_languages()
        assert 'en-US' in supported_langs
        assert 'en-GB' in supported_langs
        
    def test_adapter_error_handling(self, adapter):
        """测试错误处理"""
        # 测试无效文本
        assert len(adapter.check(None)) == 0
        assert len(adapter.check('')) == 0
        
        # 测试非字符串输入
        assert len(adapter.check(123)) == 0
        
    def test_adapter_result_format(self, adapter):
        """测试适配器结果格式"""
        text = 'teh quick brown fox'
        matches = adapter.check(text)
        
        assert len(matches) > 0
        first_match = matches[0]
        
        # 验证错误对象的格式
        assert isinstance(first_match.wrong_word, str)
        assert isinstance(first_match.suggestions, list)
        assert all(isinstance(s, str) for s in first_match.suggestions)
        assert isinstance(first_match.start, int)
        assert isinstance(first_match.end, int)
        assert first_match.start >= 0
        assert first_match.end <= len(text)
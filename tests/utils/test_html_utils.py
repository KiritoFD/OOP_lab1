import pytest
from src.utils.html_utils import escape_html_attribute, unescape_html, is_valid_html_id

class TestHtmlUtils:
    """测试HTML工具类函数"""
    
    @pytest.mark.parametrize("input_text, expected_output", [
        ("Regular text", "Regular text"),
        ("<div>", "&lt;div&gt;"),
        ("a < b > c", "a &lt; b &gt; c"),
        ("a & b", "a &amp; b"),
        ("\"quoted\"", "&quot;quoted&quot;"),
        ("'single'", "&#39;single&#39;"),
        ("<script>alert('XSS')</script>", "&lt;script&gt;alert(&#39;XSS&#39;)&lt;/script&gt;"),
        ("Multiple < > & ' \" symbols", "Multiple &lt; &gt; &amp; &#39; &quot; symbols"),
        ("", ""),  # Empty string
        (None, ""),  # None value
        (123, "123"),  # Non-string value
    ])
    def test_escape_html(self, input_text, expected_output):
        """测试HTML转义函数"""
        assert escape_html_attribute(input_text) == expected_output
        
    @pytest.mark.parametrize("input_text, expected_output", [
        ("Regular text", "Regular text"),
        ("&lt;div&gt;", "<div>"),
        ("a &lt; b &gt; c", "a < b > c"),
        ("a &amp; b", "a & b"),
        ("&quot;quoted&quot;", "\"quoted\""),
        ("&#39;single&#39;", "'single'"),
        ("&lt;script&gt;alert(&#39;XSS&#39;)&lt;/script&gt;", "<script>alert('XSS')</script>"),
        ("Multiple &lt; &gt; &amp; &#39; &quot; symbols", "Multiple < > & ' \" symbols"),
        ("", ""),  # Empty string
        (None, ""),  # None value
        (123, "123"),  # Non-string value
        # Test numeric entities
        ("&#38;", "&"),
        ("&#x26;", "&"),
        ("Mix of &#38; and &amp;", "Mix of & and &"),
    ])
    def test_unescape_html(self, input_text, expected_output):
        """测试HTML反转义函数"""
        assert unescape_html(input_text) == expected_output
        
    @pytest.mark.parametrize("html_id, expected_valid", [
        ("valid-id", True),
        ("valid_id", True),
        ("valid123", True),
        ("123valid", True),  # HTML5 allows IDs to start with a number
        ("valid-id-123", True),
        ("_valid", True),
        ("a", True),  # Single character ID is valid
        ("", False),  # Empty string is invalid
        ("invalid id", False),  # Space is invalid
        ("<invalid>", False),  # Special characters are invalid
        ("invalid#id", False),
        ("invalid.id", False),
        (None, False),  # None is invalid
        (123, False),  # Non-string is invalid
    ])
    def test_is_valid_html_id(self, html_id, expected_valid):
        """测试HTML ID验证函数"""
        assert is_valid_html_id(html_id) == expected_valid

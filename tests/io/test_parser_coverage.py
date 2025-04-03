import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import tempfile

from src.io.parser import HtmlParser
from src.core.html_model import HtmlModel
from src.core.element import HtmlElement

class TestHtmlParserCoverage:
    """测试HTML解析器的覆盖率"""
    
    @pytest.fixture
    def parser(self):
        """创建测试用的HTML解析器"""
        return HtmlParser()
    
    @pytest.fixture
    def model(self):
        """创建测试用的HTML模型"""
        return HtmlModel()

    def test_parse_basic_html(self, parser, model):
        """测试基本HTML解析"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Page</title>
        </head>
        <body>
            <div id="main">
                <h1>Hello World</h1>
                <p>This is a test page.</p>
            </div>
        </body>
        </html>
        """
        
        parser.parse(html_content, model)
        
        # 验证基本结构
        html = model.find_by_id('html')
        assert html is not None
        
        head = model.find_by_id('head')
        assert head is not None
        
        title = model.find_by_id('title')
        assert title is not None
        assert title.text == 'Test Page'
        
        body = model.find_by_id('body')
        assert body is not None
        
        main = model.find_by_id('main')
        assert main is not None

    def test_parse_with_attributes(self, parser, model):
        """测试解析带属性的HTML"""
        html_content = """
        <html>
        <body>
            <div id="container" class="main-container" data-role="content">
                <p id="para" style="color:red;">Text with attributes</p>
            </div>
        </body>
        </html>
        """
        
        parser.parse(html_content, model)
        
        container = model.find_by_id('container')
        assert container is not None
        assert container.attributes.get('class') == 'main-container'
        assert container.attributes.get('data-role') == 'content'
        
        para = model.find_by_id('para')
        assert para is not None
        assert para.attributes.get('style') == 'color:red;'
        
    def test_parse_nested_elements(self, parser, model):
        """测试深层嵌套的元素"""
        html_content = """
        <html>
        <body>
            <div id="level1">
                <div id="level2">
                    <div id="level3">
                        <p id="deep">Deep nested element</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        parser.parse(html_content, model)
        
        level1 = model.find_by_id('level1')
        level2 = model.find_by_id('level2')
        level3 = model.find_by_id('level3')
        deep = model.find_by_id('deep')
        
        assert level1 is not None
        assert level2 is not None
        assert level3 is not None
        assert deep is not None
        
        assert level2.parent == level1
        assert level3.parent == level2
        assert deep.parent == level3
        assert deep.text == 'Deep nested element'
        
    def test_parse_special_characters(self, parser, model):
        """测试特殊字符处理"""
        html_content = """
        <html>
        <body>
            <div id="special">
                <p id="amp">&amp; ampersand</p>
                <p id="lt">&lt; less than</p>
                <p id="gt">&gt; greater than</p>
                <p id="quot">&quot; quote</p>
                <p id="emoji">Emoji: 😊 🚀</p>
            </div>
        </body>
        </html>
        """
        
        parser.parse(html_content, model)
        
        amp = model.find_by_id('amp')
        assert amp is not None
        assert amp.text == '& ampersand'
        
        lt = model.find_by_id('lt')
        assert lt is not None
        assert lt.text == '< less than'
        
        gt = model.find_by_id('gt')
        assert gt is not None
        assert gt.text == '> greater than'
        
        quot = model.find_by_id('quot')
        assert quot is not None
        assert quot.text == '" quote'
        
        emoji = model.find_by_id('emoji')
        assert emoji is not None
        assert '😊' in emoji.text
        assert '🚀' in emoji.text
        
    def test_parse_with_comments(self, parser, model):
        """测试带注释的HTML"""
        html_content = """
        <html>
        <head>
            <!-- Head comment -->
            <title>Test Page</title>
        </head>
        <body>
            <!-- This is a comment -->
            <div id="main">
                <!-- Nested comment -->
                <p>Content</p>
            </div>
            <!-- Another comment -->
        </body>
        </html>
        """
        
        parser.parse(html_content, model)
        
        # 验证注释被正确忽略
        main = model.find_by_id('main')
        assert main is not None
        assert len(main.children) == 1
        assert main.children[0].tag == 'p'
        
    def test_parse_with_script_and_style(self, parser, model):
        """测试包含脚本和样式的HTML"""
        html_content = """
        <html>
        <head>
            <style id="styles">
                body { font-family: Arial; }
                .container { width: 100%; }
            </style>
            <script id="script">
                function test() {
                    if (x < 10) {
                        return true;
                    }
                }
            </script>
        </head>
        <body>
            <div id="content">Content</div>
        </body>
        </html>
        """
        
        parser.parse(html_content, model)
        
        styles = model.find_by_id('styles')
        assert styles is not None
        assert 'font-family' in styles.text
        
        script = model.find_by_id('script')
        assert script is not None
        assert 'function test()' in script.text
        assert 'if (x < 10)' in script.text
        
    def test_parse_malformed_html(self, parser, model):
        """测试解析格式不正确的HTML"""
        html_content = """
        <html>
        <body>
            <div id="unclosed">
                <p>Paragraph in unclosed div
            <span id="span">Span element</span>
        </body>
        </html>
        """
        
        parser.parse(html_content, model)
        
        # 验证元素尽管HTML不规范，仍被解析
        unclosed = model.find_by_id('unclosed')
        assert unclosed is not None
        
        span = model.find_by_id('span')
        assert span is not None
        
    def test_parse_from_file(self, parser, model):
        """测试从文件解析HTML"""
        # 创建临时HTML文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w', encoding='utf-8') as f:
            f.write("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>File Test</title>
            </head>
            <body>
                <div id="file-content">Content from file</div>
            </body>
            </html>
            """)
            temp_path = f.name
        
        try:
            # 解析文件
            parser.parse_file(temp_path, model)
            
            # 验证内容
            file_content = model.find_by_id('file-content')
            assert file_content is not None
            assert file_content.text == 'Content from file'
        finally:
            # 清理
            os.unlink(temp_path)
            
    def test_parse_nonexistent_file(self, parser, model):
        """测试解析不存在的文件"""
        with pytest.raises(Exception):
            parser.parse_file("nonexistent_file.html", model)
            
    def test_parse_empty_html(self, parser, model):
        """测试解析空HTML"""
        html_content = ""
        parser.parse(html_content, model)
        
        html = model.find_by_id('html')
        assert html is not None
        
    def test_parse_with_doctype(self, parser, model):
        """测试带DOCTYPE的HTML"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>DOCTYPE Test</title>
        </head>
        <body>
            <div id="content">Content</div>
        </body>
        </html>
        """
        
        parser.parse(html_content, model)
        
        content = model.find_by_id('content')
        assert content is not None
        assert content.text == 'Content'
        
    def test_parse_with_different_encodings(self, parser, model):
        """测试不同编码的HTML"""
        # UTF-8编码
        html_content_utf8 = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>UTF-8 Test</title>
        </head>
        <body>
            <div id="utf8">测试中文内容</div>
        </body>
        </html>
        """.encode('utf-8')
        
        parser.parse(html_content_utf8.decode('utf-8'), model)
        
        utf8_div = model.find_by_id('utf8')
        assert utf8_div is not None
        assert utf8_div.text == '测试中文内容'

import pytest
import os
from src.io.parser import HtmlParser
from src.io.writer import HtmlWriter
from src.core.html_model import HtmlModel
from src.core.exceptions import ElementNotFoundError

class TestHtmlIO:
    @pytest.fixture
    def sample_html(self):
        return """
<html>
    <head>
        <title>Test Page</title>
    </head>
    <body>
        <div id="content">
            <p id="text">Hello World</p>
            <ul id="list">
                <li id="item1">First Item</li>
                <li id="item2">Second Item</li>
            </ul>
        </div>
    </body>
</html>
""".strip()

    @pytest.fixture
    def complex_html(self):
        return """
<html>
    <head>
        <title>Complex Test</title>
    </head>
    <body>
        <div id="main">
            Text before elements
            <p id="p1">First paragraph</p>
            <p id="p2">Second paragraph</p>
        </div>
        <div id="footer">
            Footer text
            <p id="copyright">Copyright 2025</p>
        </div>
    </body>
</html>
""".strip()

    def test_parse_basic_structure(self, sample_html):
        """测试基本HTML结构解析"""
        parser = HtmlParser()
        model = parser.parse_string(sample_html)
        
        # 验证基本结构
        assert model.find_by_id('html') is not None
        assert model.find_by_id('head') is not None
        assert model.find_by_id('title') is not None
        assert model.find_by_id('body') is not None
        
        # 验证title内容
        title = model.find_by_id('title')
        assert title.text == 'Test Page'

    def test_parse_nested_elements(self, sample_html):
        """测试嵌套元素解析"""
        parser = HtmlParser()
        model = parser.parse_string(sample_html)
        
        # 验证嵌套结构
        content = model.find_by_id('content')
        text = model.find_by_id('text')
        list_el = model.find_by_id('list')
        item1 = model.find_by_id('item1')
        item2 = model.find_by_id('item2')
        
        assert text in content.children
        assert list_el in content.children
        assert item1 in list_el.children
        assert item2 in list_el.children
        
        # 验证文本内容
        assert text.text == 'Hello World'
        assert item1.text == 'First Item'
        assert item2.text == 'Second Item'

    def test_parse_text_before_elements(self, complex_html):
        """测试元素前的文本内容解析"""
        parser = HtmlParser()
        model = parser.parse_string(complex_html)
        
        main = model.find_by_id('main')
        footer = model.find_by_id('footer')
        
        assert main.text == 'Text before elements'
        assert footer.text == 'Footer text'

    def test_write_basic_structure(self, tmp_path):
        """测试基本HTML结构的写入"""
        model = HtmlModel()  # 创建一个基本模型
        
        # 写入文件
        filepath = os.path.join(tmp_path, 'test.html')
        writer = HtmlWriter()
        assert writer.write_file(model, filepath) is True
        
        # 读取并验证
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            assert '<html>' in content
            assert '<head>' in content
            assert '<title>' in content
            assert '<body>' in content
            assert content.count('<html>') == 1  # 确保标签只出现一次

    def test_write_complex_structure(self, tmp_path, complex_html):
        """测试复杂HTML结构的写入"""
        # 解析样例HTML
        parser = HtmlParser()
        model = parser.parse_string(complex_html)
        
        # 写入文件
        filepath = os.path.join(tmp_path, 'complex.html')
        writer = HtmlWriter()
        assert writer.write_file(model, filepath) is True
        
        # 重新解析写入的文件
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        new_parser = HtmlParser()
        new_model = new_parser.parse_string(content)
        
        # 验证结构和内容保持一致
        elements = ['main', 'p1', 'p2', 'footer', 'copyright']
        for id in elements:
            original = model.find_by_id(id)
            parsed = new_model.find_by_id(id)
            assert parsed is not None
            assert parsed.text == original.text

    def test_write_indentation(self, tmp_path):
        """测试HTML输出的缩进格式"""
        model = HtmlModel()
        div = model.append_child('body', 'div', 'test')
        model.append_child('test', 'p', 'para', 'Hello')
        
        # 写入文件
        filepath = os.path.join(tmp_path, 'indent.html')
        writer = HtmlWriter()
        writer.write_file(model, filepath)
        
        # 读取并检查缩进
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # 验证缩进
        div_line = next(i for i, line in enumerate(lines) if 'div' in line)
        p_line = next(i for i, line in enumerate(lines) if 'p' in line)
        
        assert len(lines[div_line]) - len(lines[div_line].lstrip()) > 0
        assert len(lines[p_line]) - len(lines[p_line].lstrip()) > len(lines[div_line]) - len(lines[div_line].lstrip())

    def test_write_self_closing_tags(self, tmp_path):
        """测试空元素的写入"""
        model = HtmlModel()
        # 添加一些空元素
        model.append_child('body', 'img', 'test-img')
        model.append_child('body', 'br', 'test-br')
        
        # 写入文件
        filepath = os.path.join(tmp_path, 'self-closing.html')
        writer = HtmlWriter()
        writer.write_file(model, filepath)
        
        # 验证输出格式
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            assert '/>' in content  # 应该使用自闭合标签

    def test_parse_invalid_html(self):
        """测试解析无效HTML"""
        invalid_html = "<html><body><p>未闭合的段落"
        parser = HtmlParser()
        with pytest.raises(Exception):  # 使用一般异常替代特定异常
            parser.parse_string(invalid_html)

    def test_parse_file_not_found(self):
        """测试解析不存在的文件"""
        parser = HtmlParser()
        with pytest.raises(FileNotFoundError):
            parser.parse_file('nonexistent.html')

    def test_write_permission_denied(self, tmp_path):
        """测试写入权限被拒绝的情况"""
        model = HtmlModel()
        filepath = os.path.join(tmp_path, 'test.html')
        
        # 创建文件并设置为只读
        with open(filepath, 'w') as f:
            f.write('')
        os.chmod(filepath, 0o444)  # 设置为只读
        
        writer = HtmlWriter()
        with pytest.raises(PermissionError):
            writer.write_file(model, filepath)

    def test_round_trip(self, sample_html, tmp_path):
        """测试HTML的解析-写入-解析循环"""
        # 第一次解析
        parser = HtmlParser()
        model1 = parser.parse_string(sample_html)
        
        # 写入文件
        filepath = os.path.join(tmp_path, 'round-trip.html')
        writer = HtmlWriter()
        writer.write_file(model1, filepath)
        
        # 重新解析
        new_parser = HtmlParser()
        model2 = new_parser.parse_file(filepath)
        
        # 比较两个模型
        def compare_elements(e1, e2):
            assert e1.tag == e2.tag
            assert e1.id == e2.id
            assert e1.text == e2.text
            assert len(e1.children) == len(e2.children)
            for c1, c2 in zip(e1.children, e2.children):
                compare_elements(c1, c2)
        
        compare_elements(model1.find_by_id('html'), model2.find_by_id('html'))
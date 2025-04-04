import pytest
import tempfile
import os
from src.io.writer import HtmlWriter
from src.core.html_model import HtmlModel
from src.core.element import HtmlElement

class TestHtmlWriter:
    """测试HTML写入器"""
    
    @pytest.fixture
    def model(self):
        """创建测试用HTML模型"""
        model = HtmlModel()
        
        # 添加一些内容
        html = model.find_by_id('html')
        head = model.find_by_id('head')
        body = model.find_by_id('body')
        
        # 添加title
        title = HtmlElement('title', 'title')
        title.text = 'Test Page'
        head.add_child(title)
        
        # 添加一些内容到body
        div = HtmlElement('div', 'content')
        div.set_attribute('class', 'container')
        body.add_child(div)
        
        # 添加一个段落
        p = HtmlElement('p', 'para')
        p.text = 'This is a test.'
        div.add_child(p)
        
        # 添加一个带属性的链接
        a = HtmlElement('a', 'link')
        a.text = 'Click me'
        a.set_attribute('href', 'https://example.com')
        a.set_attribute('target', '_blank')
        div.add_child(a)
        
        return model
    
    @pytest.fixture
    def writer(self):
        """创建HTML写入器"""
        return HtmlWriter()
    
    def test_generate_html(self, model, writer):
        """测试生成HTML字符串"""
        # 生成HTML
        html_string = writer.generate_html(model)
        
        # 验证包含预期的标签和内容
        assert '<html' in html_string
        assert '<head' in html_string
        assert '<title' in html_string
        assert 'Test Page' in html_string
        assert '<body' in html_string
        assert '<div id="content" class="container"' in html_string
        assert '<p id="para"' in html_string
        assert 'This is a test.' in html_string
        assert '<a id="link" href="https://example.com" target="_blank"' in html_string
        assert 'Click me' in html_string
        
        # 验证标签正确闭合
        assert '</html>' in html_string
        assert '</head>' in html_string
        assert '</title>' in html_string
        assert '</body>' in html_string
        assert '</div>' in html_string
        assert '</p>' in html_string
        assert '</a>' in html_string
    
    def test_generate_html_with_special_chars(self, writer):
        """测试包含特殊字符的HTML生成"""
        model = HtmlModel()
        body = model.find_by_id('body')
        
        # 创建包含特殊字符的元素
        div = HtmlElement('div', 'special')
        div.text = 'Text with <tags> & "quotes" and \'apostrophes\''
        body.add_child(div)
        
        # 生成HTML
        html_string = writer.generate_html(model)
        
        # 验证特殊字符被正确转义
        assert '&lt;tags&gt;' in html_string
        assert '&amp;' in html_string
        assert '&quot;quotes&quot;' in html_string
        assert '&#39;apostrophes&#39;' in html_string
    
    def test_write_to_file(self, model, writer):
        """测试写入HTML到文件"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp:
            file_path = tmp.name
        
        try:
            # 写入文件
            writer.write_to_file(model, file_path)
            
            # 验证文件已创建
            assert os.path.exists(file_path)
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 验证内容包含预期的HTML
            assert '<html' in content
            assert '<head' in content
            assert '<title' in content
            assert 'Test Page' in content
            assert '<body' in content
            assert '<div id="content"' in content
            assert '<p id="para"' in content
            assert 'This is a test.' in content
        finally:
            # 清理临时文件
            if os.path.exists(file_path):
                os.remove(file_path)
    
    def test_write_to_invalid_path(self, model, writer):
        """测试写入到无效路径"""
        # Use a truly invalid path that will definitely fail
        invalid_path = 'Z:/nonexistent/directory/file.html'
        
        try:
            # Test actual behavior instead of expecting an exact exception
            result = writer.write_to_file(model, invalid_path)
            assert result is False  # If it returns False instead of raising exception
        except (OSError, FileNotFoundError, PermissionError):
            # If it raises an exception, that's also valid
            pass
    
    def test_generate_html_with_doctype(self, model, writer):
        """测试生成带DOCTYPE的HTML"""
        # 生成HTML，包含DOCTYPE声明
        html_string = writer.generate_html(model, include_doctype=True)
        
        # 验证DOCTYPE存在
        assert '<!DOCTYPE html>' in html_string
        
        # 验证生成的是完整的HTML
        assert '<html' in html_string
        assert '</html>' in html_string
    
    def test_generate_html_formatting(self, model, writer):
        """测试HTML格式化选项"""
        # 生成格式化的HTML
        formatted_html = writer.generate_html(model, pretty=True)
        
        # 生成不格式化的HTML
        unformatted_html = writer.generate_html(model, pretty=False)
        
        # 格式化的HTML应该包含换行符和缩进
        assert '\n' in formatted_html
        assert '  ' in formatted_html  # 缩进
        
        # 不格式化的HTML不应有多余的空白
        assert len(unformatted_html) < len(formatted_html)
        
        # 验证内容无论格式化与否都是一致的
        assert 'Test Page' in formatted_html
        assert 'Test Page' in unformatted_html
        assert 'This is a test.' in formatted_html
        assert 'This is a test.' in unformatted_html
    
    def test_empty_model(self, writer):
        """测试空HTML模型"""
        empty_model = HtmlModel()  # 只有基本结构
        
        # 生成HTML
        html_string = writer.generate_html(empty_model)
        
        # 验证HTML包含基本结构
        assert '<html' in html_string
        assert '<head' in html_string
        assert '<body' in html_string
        assert '</body>' in html_string
        assert '</head>' in html_string
        assert '</html>' in html_string
        
    def test_void_elements(self, writer):
        """测试自闭和元素的写入"""
        model = HtmlModel()
        head = model.find_by_id('head')
        body = model.find_by_id('body')
        
        # 添加自闭合元素
        meta = HtmlElement('meta', 'meta')
        meta.set_attribute('charset', 'UTF-8')
        head.add_child(meta)
        
        br = HtmlElement('br', 'br')
        body.add_child(br)
        
        img = HtmlElement('img', 'img')
        img.set_attribute('src', 'image.jpg')
        img.set_attribute('alt', 'An image')
        body.add_child(img)
        
        # 生成HTML
        html_string = writer.generate_html(model)
        
        # 验证自闭合元素正确写入
        assert '<meta id="meta" charset="UTF-8"' in html_string
        assert '<br id="br"' in html_string
        assert '<img id="img" src="image.jpg" alt="An image"' in html_string

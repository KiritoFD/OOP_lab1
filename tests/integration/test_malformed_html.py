import os
import pytest
import tempfile
from unittest.mock import patch, mock_open

from src.core.html_model import HtmlModel
from src.core.element import HtmlElement
from src.commands.base import CommandProcessor
from src.commands.io_commands import ReadCommand
from src.commands.command_exceptions import CommandExecutionError
from src.io.parser import HtmlParser

class TestMalformedHtml:
    """测试对格式错误的HTML的处理"""
    
    @pytest.fixture
    def setup(self):
        """设置测试环境"""
        model = HtmlModel()
        processor = CommandProcessor()
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        
        return {
            'model': model,
            'processor': processor,
            'temp_dir': temp_dir
        }
    
    def test_unclosed_tags(self):
        """测试处理未闭合标签的能力"""
        parser = HtmlParser()

        # 包含未闭合标签的HTML
        html_content = """
        <html id="html">
          <head id="head">
            <title id="title">Unclosed Tags Test
          </head>
          <body id="body">
            <div id="container">
              <p id="p1">Paragraph 1
              <p id="p2">Paragraph 2
            </div>
          </body>
        </html>
        """

        # 解析应该成功完成
        root = parser.parse_string(html_content)  # 使用正确的方法名
        assert root is not None
        assert root.tag == 'html'

        # 尝试访问元素
        model = HtmlModel()
        model.replace_content(root)

        # 验证至少基本结构是存在的 - 确保使用显式提供的ID
        assert model.find_by_id('html') is not None
        assert model.find_by_id('container') is not None
        assert model.find_by_id('p1') is not None
        assert model.find_by_id('p2') is not None
        
    def test_empty_file(self, setup):
        """测试处理空文件"""
        model = setup['model']
        processor = setup['processor']
        temp_dir = setup['temp_dir']

        # 创建空文件
        empty_file = os.path.join(temp_dir, 'empty.html')
        with open(empty_file, 'w') as f:
            f.write('')

        # 尝试读取
        read_cmd = ReadCommand(processor, model, empty_file)

        # 期望抛出CommandExecutionError异常
        with pytest.raises(CommandExecutionError) as excinfo:
            processor.execute(read_cmd)
            
        # 验证错误消息包含"文件内容为空"
        assert "文件内容为空" in str(excinfo.value)
    
    def test_nested_errors(self):
        """测试处理错误嵌套的HTML"""
        parser = HtmlParser()
        
        # 包含嵌套错误的HTML (标签交叉)
        html_content = """
        <html>
          <head>
            <title>Nested Errors Test</title>
          </head>
          <body>
            <div id="container">
              <span id="s1">This <p id="p1">is wrong</span> nesting</p>
            </div>
          </body>
        </html>
        """
        
        # 解析应该成功完成
        root = parser.parse_string(html_content)  # 使用正确的方法名
        assert root is not None
        
        # 尝试访问元素
        model = HtmlModel()
        model.replace_content(root)
        
        s1 = model.find_by_id('s1')
        assert s1 is not None
        
        p1 = model.find_by_id('p1')
        assert p1 is not None
    
    def test_severely_malformed_html(self, setup):
        """测试处理严重畸形的HTML"""
        model = setup['model']
        processor = setup['processor']
        temp_dir = setup['temp_dir']
        
        # 创建一个畸形的HTML文件
        malformed_file = os.path.join(temp_dir, 'malformed.html')
        with open(malformed_file, 'w') as f:
            f.write('<malformed><<>>')
        
        # 直接使用文件而非模拟
        read_cmd = ReadCommand(processor, model, malformed_file)
        
        # 应该优雅地处理
        result = processor.execute(read_cmd)
        
        # 即使是畸形HTML，也应该生成一个合法的模型
        # 可能会失败或成功，但不应崩溃
        if result:  # 如果解析成功
            # 至少应该有基本结构
            html = model.find_by_id('html')
            assert html is not None

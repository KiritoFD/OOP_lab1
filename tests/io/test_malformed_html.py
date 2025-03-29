import pytest
import os
import tempfile
from unittest.mock import patch, mock_open
from src.io.parser import HtmlParser
from src.core.html_model import HtmlModel
from src.commands.io import ReadCommand
from src.commands.base import CommandProcessor
from src.core.exceptions import InvalidOperationError
from src.commands.command_exceptions import CommandExecutionError

class TestMalformedHtml:
    @pytest.fixture
    def setup(self):
        model = HtmlModel()
        processor = CommandProcessor()
        temp_dir = tempfile.mkdtemp()
        return {
            'model': model,
            'processor': processor,
            'temp_dir': temp_dir
        }
    
    def test_unclosed_tags(self):
        """测试处理未闭合标签的能力"""
        parser = HtmlParser()
    
        # 包含未闭合标签的HTML - 添加明确的ID属性
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

        # 使用正确的API - parse_string代替parse_html
        root = parser.parse_string(html_content)
        assert root is not None
        
        # 应该能够找到所有标签，即使有未闭合标签
        model = HtmlModel()
        model.replace_content(root)
        
        assert model.find_by_id('html') is not None
        assert model.find_by_id('container') is not None
        assert model.find_by_id('p1') is not None
        assert model.find_by_id('p2') is not None

    def test_nested_errors(self):
        """测试处理错误嵌套的HTML"""
        parser = HtmlParser()

        # 包含嵌套错误的HTML (标签交叉) - 添加明确的ID属性
        html_content = """
        <html id="html">
          <head id="head">
            <title id="title">Nested Errors Test</title>
          </head>
          <body id="body">
            <div id="container">
              <span id="s1">This <p id="p1">is wrong</span> nesting</p>
            </div>
          </body>
        </html>
        """

        # 使用正确的API - parse_string代替parse_html
        root = parser.parse_string(html_content)
        assert root is not None
        
        # 即使有错误嵌套，仍应解析成功
        model = HtmlModel()
        model.replace_content(root)
        
        # 标准解析器应该能从错误中恢复
        assert model.find_by_id('container') is not None
        assert model.find_by_id('s1') is not None
        assert model.find_by_id('p1') is not None

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

        # 期望抛出特定的异常
        with pytest.raises(CommandExecutionError) as excinfo:
            processor.execute(read_cmd)
            
        # 验证错误消息包含"文件内容为空"
        assert "文件内容为空" in str(excinfo.value)

    def test_severely_malformed_html(self, setup):
        """测试处理严重畸形的HTML"""
        model = setup['model']
        processor = setup['processor']
        
        # 创建文件路径并写入内容
        filepath = os.path.join(setup['temp_dir'], "malformed.html")
        with open(filepath, "w") as f:
            f.write('<malformed><<>>')
            
        read_cmd = ReadCommand(processor, model, filepath)
        
        # BeautifulSoup可以处理畸形HTML，所以应该成功
        result = processor.execute(read_cmd)
        assert result is True

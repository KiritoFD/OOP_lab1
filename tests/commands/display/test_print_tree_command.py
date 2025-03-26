import pytest
import os
from io import StringIO
from bs4 import BeautifulSoup
from src.core.html_model import HtmlModel
from src.core.element import HtmlElement
from src.commands.display_commands import PrintTreeCommand
from src.commands.base import CommandProcessor
from src.commands.edit_commands import AppendCommand

class TestPrintTreeCommand:
    @pytest.fixture
    def model(self):
        """创建测试用的HTML模型"""
        return HtmlModel()
    
    @pytest.fixture
    def processor(self):
        return CommandProcessor()
    
    @pytest.fixture
    def simple_tree_model(self):
        """从固定文件加载简单树结构，直接使用BeautifulSoup解析"""
        file_path = os.path.join('tests', 'input', 'simple_tree.html')
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # 使用BeautifulSoup解析，而非依赖HtmlParser
        soup = BeautifulSoup(html_content, 'html.parser')
        html_tag = soup.find('html')
        
        # 构建模型
        model = HtmlModel()
        root = self._build_element_tree(html_tag)
        if root:
            model.replace_content(root)
        return model
    
    @pytest.fixture
    def deep_nested_model(self):
        """从固定文件加载深层嵌套结构，直接使用BeautifulSoup解析"""
        file_path = os.path.join('tests', 'input', 'deep_nested.html')
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
            
        soup = BeautifulSoup(html_content, 'html.parser')
        html_tag = soup.find('html')
        
        model = HtmlModel()
        root = self._build_element_tree(html_tag)
        if root:
            model.replace_content(root)
        return model
    
    @pytest.fixture
    def special_chars_model(self):
        """从固定文件加载含特殊字符的结构，直接使用BeautifulSoup解析"""
        file_path = os.path.join('tests', 'input', 'special_chars.html')
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
            
        soup = BeautifulSoup(html_content, 'html.parser')
        html_tag = soup.find('html')
        
        model = HtmlModel()
        root = self._build_element_tree(html_tag)
        if root:
            model.replace_content(root)
        return model
    
    def _build_element_tree(self, soup_element):
        """在测试类中直接实现简单的元素树构建逻辑"""
        if not soup_element:
            return None
            
        # 获取标签名和ID
        tag = soup_element.name
        element_id = soup_element.get('id', tag)
        
        # 创建元素
        element = HtmlElement(tag, element_id)
        
        # 处理文本内容
        if soup_element.strings:
            text_content = ' '.join(t.strip() for t in soup_element.strings if t.strip())
            if text_content:
                element.text = text_content
        
        # 递归处理子元素
        for child in soup_element.children:
            if child.name:  # 跳过纯文本节点
                child_element = self._build_element_tree(child)
                if child_element:
                    element.add_child(child_element)
                    
        return element
    
    def test_print_basic_structure(self, model, processor, capsys):
        """测试打印基本HTML结构"""
        cmd = PrintTreeCommand(model)
        
        # 执行打印
        assert processor.execute(cmd) is True
        
        # 获取打印输出
        captured = capsys.readouterr()
        output = captured.out
        
        # 验证基本结构
        assert 'html' in output
        assert '├── head' in output
        assert '│   └── title' in output
        assert '└── body' in output
        
    def test_print_with_content(self, simple_tree_model, processor, capsys):
        """测试打印包含内容的树结构"""
        # 使用从文件加载的模型
        model = simple_tree_model
        cmd = PrintTreeCommand(model)
        processor.execute(cmd)
        
        captured = capsys.readouterr()
        output = captured.out
        
        # 修改断言以匹配实际输出格式
        assert 'div (id=main)' in output
        assert 'p (id=para1)' in output
        assert 'p (id=para2)' in output
        assert 'div (id=section)' in output
        assert 'Paragraph 1' in output
        assert 'Paragraph 2' in output
        assert 'Text 1' in output
        
    def test_print_empty_elements(self, model, processor, capsys):
        """测试打印空元素"""
        # 添加一个空div
        cmd1 = AppendCommand(model, 'div', 'empty', 'body')
        processor.execute(cmd1)
        
        # 打印
        cmd2 = PrintTreeCommand(model)
        processor.execute(cmd2)
        
        captured = capsys.readouterr()
        output = captured.out
        
        # 验证空元素显示正确
        assert 'empty' in output
        assert output.count('└──') >= 1  # 至少有一个叶子节点标记
        
    def test_print_deep_nesting(self, deep_nested_model, processor, capsys):
        """测试打印深层嵌套结构"""
        # 使用从文件加载的深层嵌套模型
        model = deep_nested_model
        cmd = PrintTreeCommand(model)
        processor.execute(cmd)
        
        captured = capsys.readouterr()
        output = captured.out
        
        # 验证嵌套层次
        for i in range(5):
            assert f'level{i}' in output
            
        # 验证缩进增加
        lines = output.split('\n')
        max_indent = max(len(line) - len(line.lstrip()) for line in lines if line.strip())
        assert max_indent >= 16  # 至少4个层次的缩进
        
    def test_print_non_recordable(self, model, processor):
        """测试打印命令不被记录到历史"""
        cmd = PrintTreeCommand(model)
        processor.execute(cmd)
        
        # 验证命令不可撤销
        assert processor.undo() is False
        
    def test_print_special_chars(self, special_chars_model, processor, capsys):
        """测试打印包含特殊字符的内容"""
        # 使用从文件加载的特殊字符模型
        model = special_chars_model
        cmd = PrintTreeCommand(model)
        processor.execute(cmd)
        
        captured = capsys.readouterr()
        output = captured.out
        
        # 修改断言以匹配实际输出格式
        assert 'p (id=special)' in output
        assert '&' in output
        assert 'quotes' in output
        assert 'apostrophes' in output
        assert 'p (id=empty)' in output
        assert 'div (id=html-tags)' in output
        assert '<html>' in output
import pytest
import os
from bs4 import BeautifulSoup
from unittest.mock import patch, MagicMock
from src.core.html_model import HtmlModel
from src.core.element import HtmlElement
from src.commands.display_commands import SpellCheckCommand
from src.commands.base import CommandProcessor
from src.spellcheck.checker import SpellError

class TestSpellCheckCommand:
    @pytest.fixture
    def model(self):
        """创建测试用的HTML模型"""
        return HtmlModel()
    
    @pytest.fixture
    def processor(self):
        return CommandProcessor()
    
    @pytest.fixture
    def spell_check_model(self):
        """从固定文件加载拼写检查测试内容"""
        file_path = os.path.join('tests', 'input', 'spell_check.html')
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # 使用BeautifulSoup解析
        soup = BeautifulSoup(html_content, 'html.parser')
        html_tag = soup.find('html')
        
        # 构建模型
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
    
    @patch('src.spellcheck.checker.SpellChecker')
    def test_spell_check_basic(self, mock_checker_class, spell_check_model, processor, capsys):
        """测试基本的拼写检查功能"""
        # 设置模拟的检查器行为
        mock_checker = mock_checker_class.return_value
        
        # 模拟拼写错误
        mock_checker.check_text.side_effect = lambda text: [
            SpellError(wrong_word="paragreph", suggestions=["paragraph"], 
                      context="This paragreph has", start=5, end=14)
        ] if "paragreph" in text else []
        
        cmd = SpellCheckCommand(spell_check_model)
        
        # 执行拼写检查
        assert processor.execute(cmd) is True
        
        # 获取输出
        captured = capsys.readouterr()
        output = captured.out
        
        # 验证拼写错误被检测到
        assert "拼写检查完成" in output
        assert "paragreph" in output
        assert "paragraph" in output  # 建议的修正
        
    @patch('src.spellcheck.checker.SpellChecker')
    def test_spell_check_multiple_errors(self, mock_checker_class, spell_check_model, processor, capsys):
        """测试多个拼写错误的情况"""
        mock_checker = mock_checker_class.return_value
        
        # 模拟多个拼写错误
        def mock_check(text):
            errors = []
            if "paragreph" in text:
                errors.append(SpellError(wrong_word="paragreph", suggestions=["paragraph"], 
                                       context="This paragreph has", start=5, end=14))
            if "sume" in text:
                errors.append(SpellError(wrong_word="sume", suggestions=["some"], 
                                       context="has sume incorrect", start=15, end=19))
            if "speling" in text:
                errors.append(SpellError(wrong_word="speling", suggestions=["spelling"], 
                                       context="incorrect speling", start=25, end=32))
            return errors
            
        mock_checker.check_text.side_effect = mock_check
        
        cmd = SpellCheckCommand(spell_check_model)
        processor.execute(cmd)
        
        captured = capsys.readouterr()
        output = captured.out
        
        # 验证输出包含多个错误
        assert "拼写检查完成" in output
        assert "paragreph" in output
        assert "sume" in output
        assert "speling" in output
        
    @patch('src.spellcheck.checker.SpellChecker')
    def test_spell_check_empty_model(self, mock_checker_class, model, processor, capsys):
        """测试在空模型上的拼写检查"""
        mock_checker = mock_checker_class.return_value
        mock_checker.check_text.return_value = []
        
        cmd = SpellCheckCommand(model)
        processor.execute(cmd)
        
        captured = capsys.readouterr()
        output = captured.out
        
        # 验证没有拼写错误被检测到
        assert "拼写检查通过" in output
        
    def test_spell_check_non_recordable(self, model, processor):
        """测试拼写检查命令不被记录到历史"""
        cmd = SpellCheckCommand(model)
        processor.execute(cmd)
        
        # 验证命令不可撤销
        assert processor.undo() is False
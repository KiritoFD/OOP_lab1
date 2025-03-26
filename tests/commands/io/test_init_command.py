import pytest
from src.core.html_model import HtmlModel
from src.commands.io_commands import InitCommand
from src.commands.base import CommandProcessor
from src.commands.edit_commands import AppendCommand

class TestInitCommand:
    @pytest.fixture
    def model(self):
        return HtmlModel()
    
    @pytest.fixture
    def processor(self):
        return CommandProcessor()
        
    def test_init_success(self, model, processor):
        """测试成功初始化"""
        cmd = InitCommand(processor, model)
        
        # 添加一些内容，以验证初始化会清空
        setup_cmd = AppendCommand(model, 'div', 'test-div', 'body', 'Test Content')
        processor.execute(setup_cmd)
        
        # 执行初始化
        assert processor.execute(cmd) is True
        
        # 验证基本结构
        html = model.find_by_id('html')
        head = model.find_by_id('head')
        title = model.find_by_id('title')
        body = model.find_by_id('body')
        
        assert html is not None
        assert head is not None and head in html.children
        assert title is not None and title in head.children
        assert body is not None and body in html.children
        
        # 验证之前的内容被清空
        assert model.find_by_id('test-div') is None
        
    def test_init_clears_history(self, model, processor):
        """测试初始化后清空命令历史"""
        # 执行一些编辑命令
        cmd1 = AppendCommand(model, 'div', 'test-div', 'body')
        processor.execute(cmd1)
        
        # 执行初始化
        cmd2 = InitCommand(processor, model)
        processor.execute(cmd2)
        
        # 验证无法撤销之前的编辑
        assert processor.undo() is False
        
    def test_init_preserves_structure(self, model, processor):
        """测试初始化保持正确的HTML结构"""
        cmd = InitCommand(processor, model)
        processor.execute(cmd)
        
        # 验证元素及其关系
        html = model.find_by_id('html')
        head = model.find_by_id('head')
        title = model.find_by_id('title')
        body = model.find_by_id('body')
        
        # 检查元素存在性
        assert all(elem is not None for elem in [html, head, title, body])
        
        # 检查父子关系
        assert head.parent == html
        assert body.parent == html
        assert title.parent == head
        
        # 检查顺序
        assert html.children.index(head) < html.children.index(body)
        
    def test_init_empty_content(self, model, processor):
        """测试初始化后元素内容为空"""
        cmd = InitCommand(processor, model)
        processor.execute(cmd)
        
        # 验证title和body为空
        title = model.find_by_id('title')
        body = model.find_by_id('body')
        
        assert title.text == ''
        assert len(body.children) == 0
        
    def test_init_multiple_times(self, model, processor):
        """测试多次初始化"""
        # 第一次初始化
        cmd1 = InitCommand(processor, model)
        processor.execute(cmd1)
        
        # 添加一些内容
        append_cmd = AppendCommand(model, 'div', 'test-div', 'body')
        processor.execute(append_cmd)
        
        # 第二次初始化
        cmd2 = InitCommand(processor, model)
        processor.execute(cmd2)
        
        # 验证内容被清空
        assert model.find_by_id('test-div') is None
        
        # 验证基本结构保持完整
        html = model.find_by_id('html')
        head = model.find_by_id('head')
        title = model.find_by_id('title')
        body = model.find_by_id('body')
        
        assert all(elem is not None for elem in [html, head, title, body])
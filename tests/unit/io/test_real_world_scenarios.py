import pytest
import os
import tempfile
from unittest.mock import patch

from src.core.html_model import HtmlModel
from src.commands.base import CommandProcessor
from src.commands.io import InitCommand, SaveCommand, ReadCommand
from src.commands.edit.append_command import AppendCommand
from src.commands.edit.insert_command import InsertCommand
from src.commands.edit.delete_command import DeleteCommand
from src.commands.edit.edit_text_command import EditTextCommand
from src.commands.edit.edit_id_command import EditIdCommand
from src.commands.display import PrintTreeCommand
from src.core.exceptions import ElementNotFoundError, DuplicateIdError
from src.commands.command_exceptions import CommandExecutionError

@pytest.mark.unit
class TestRealWorldScenarios:
    """测试真实场景用例"""
    
    @pytest.fixture
    def setup(self):
        """设置测试环境"""
        model = HtmlModel()
        processor = CommandProcessor()
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            yield {
                'model': model,
                'processor': processor,
                'temp_dir': temp_dir
            }
    
    def test_create_blog_post(self, setup):
        """测试创建完整博客文章页面"""
        model = setup['model']
        processor = setup['processor']
        
        # 初始化
        processor.execute(InitCommand(model))
        
        # 首先要创建title元素
        processor.execute(AppendCommand(model, 'title', 'title', 'head', ''))
        
        # 设置标题
        processor.execute(EditTextCommand(model, 'title', 'My Tech Blog - Python Design Patterns'))
        
        # 添加页眉
        processor.execute(AppendCommand(model, 'header', 'page-header', 'body'))
        processor.execute(AppendCommand(model, 'h1', 'blog-title', 'page-header', 'Python Design Patterns'))
        processor.execute(AppendCommand(model, 'div', 'meta', 'page-header'))
        processor.execute(AppendCommand(model, 'span', 'author', 'meta', 'Posted by: John Doe'))
        processor.execute(AppendCommand(model, 'span', 'date', 'meta', 'Date: 2023-05-15'))
        
        # 添加主内容
        processor.execute(AppendCommand(model, 'main', 'content', 'body'))
        processor.execute(AppendCommand(model, 'article', 'article1', 'content'))
        processor.execute(AppendCommand(model, 'h2', 'intro-heading', 'article1', 'Introduction to Design Patterns'))
        processor.execute(AppendCommand(model, 'p', 'intro-text', 'article1', 'Design patterns are reusable solutions to common problems in software design.'))
        
        # 添加模式列表
        processor.execute(AppendCommand(model, 'h2', 'patterns-heading', 'article1', 'Common Design Patterns'))
        processor.execute(AppendCommand(model, 'ul', 'pattern-list', 'article1'))
        
        patterns = [
            ('Singleton', 'Ensures a class has only one instance.'),
            ('Observer', 'Defines a dependency between objects.'),
            ('Factory', 'Creates objects without specifying exact class.'),
            ('Strategy', 'Defines family of algorithms.')
        ]
        
        # 添加每个模式作为列表项
        for i, (name, desc) in enumerate(patterns):
            processor.execute(AppendCommand(model, 'li', f'pattern{i}', 'pattern-list'))
            processor.execute(AppendCommand(model, 'h3', f'name{i}', f'pattern{i}', name))
            processor.execute(AppendCommand(model, 'p', f'desc{i}', f'pattern{i}', desc))
        
        # 添加结论
        processor.execute(AppendCommand(model, 'h2', 'conclusion-heading', 'article1', 'Conclusion'))
        processor.execute(AppendCommand(model, 'p', 'conclusion-text', 'article1', 
                                     'Understanding design patterns helps create better software architecture.'))
        
        # 添加页脚
        processor.execute(AppendCommand(model, 'footer', 'page-footer', 'body'))
        processor.execute(AppendCommand(model, 'p', 'copyright', 'page-footer', '© 2023 My Tech Blog'))
        processor.execute(AppendCommand(model, 'p', 'contact', 'page-footer', 'Contact: contact@example.com'))
        
        # 验证博客结构
        assert model.find_by_id('blog-title').text == 'Python Design Patterns'
        assert model.find_by_id('author').text == 'Posted by: John Doe'
        assert len(model.find_by_id('pattern-list').children) == 4
        assert model.find_by_id('copyright').text == '© 2023 My Tech Blog'
        
        # 保存博客HTML
        temp_dir = setup['temp_dir']
        file_path = os.path.join(temp_dir, 'blog_post.html')
        processor.execute(SaveCommand(model, file_path))
        
        # 验证文件已保存
        assert os.path.exists(file_path)
        file_size = os.path.getsize(file_path)
        assert file_size > 1000  # 确保文件大小合理
        
        # 从文件重新加载
        new_model = HtmlModel()
        new_processor = CommandProcessor()
        read_cmd = ReadCommand(new_processor, new_model, file_path)
        assert new_processor.execute(read_cmd) is True
        
        # 验证加载后的结构保持完整
        assert new_model.find_by_id('blog-title') is not None
        assert new_model.find_by_id('author') is not None
        assert new_model.find_by_id('pattern0') is not None
        assert new_model.find_by_id('conclusion-text') is not None
    
    def test_interactive_editing_session(self, setup):
        """测试模拟交互式编辑会话，包括错误修复"""
        model = setup['model']
        processor = setup['processor']
        
        # 初始化一个新的HTML文档
        processor.execute(InitCommand(model))
        
        # 1. 添加基本结构
        processor.execute(AppendCommand(model, 'div', 'container', 'body'))
        processor.execute(AppendCommand(model, 'h1', 'page-title', 'container', 'My Webpage'))
        
        # 2. 错误地添加重复ID (模拟用户错误)
        with pytest.raises(DuplicateIdError) as excinfo:
            processor.execute(AppendCommand(model, 'div', 'container', 'body'))
        
        # 验证错误信息包含"已存在"
        assert "已存在" in str(excinfo.value)
        
        # 3. 用户改为使用不同ID
        processor.execute(AppendCommand(model, 'div', 'content', 'body'))
        
        # 4. 添加段落
        processor.execute(AppendCommand(model, 'p', 'intro', 'content', 'Welcome to my webpage!'))
        processor.execute(AppendCommand(model, 'ul', 'links', 'content'))
        processor.execute(AppendCommand(model, 'li', 'link1', 'links', 'Home'))
        processor.execute(AppendCommand(model, 'li', 'link2', 'links', 'About'))
        
        # 5. 修改内容
        processor.execute(EditTextCommand(model, 'intro', 'Welcome to my awesome webpage!'))
        
        # 验证最终结构
        assert model.find_by_id('container') is not None
        assert model.find_by_id('content') is not None
        assert model.find_by_id('intro') is not None
        assert model.find_by_id('links') is not None
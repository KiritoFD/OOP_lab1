import pytest
import os
import tempfile
from unittest.mock import patch

from src.core.html_model import HtmlModel
from src.commands.base import CommandProcessor
from src.commands.io_commands import InitCommand, SaveCommand, ReadCommand
from src.commands.edit.append_command import AppendCommand
from src.commands.edit.insert_command import InsertCommand
from src.commands.edit.delete_command import DeleteCommand
from src.commands.edit.edit_text_command import EditTextCommand
from src.commands.edit.edit_id_command import EditIdCommand
from src.commands.display_commands import PrintTreeCommand
from src.core.exceptions import ElementNotFoundError, DuplicateIdError

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
        with pytest.raises(DuplicateIdError):
            processor.execute(AppendCommand(model, 'div', 'container', 'body'))
        
        # 3. 用户改为使用不同ID
        processor.execute(AppendCommand(model, 'div', 'content', 'container'))
        
        # 4. 添加段落
        processor.execute(AppendCommand(model, 'p', 'para1', 'content', 'First paragraph'))
        processor.execute(AppendCommand(model, 'p', 'para2', 'content', 'Second paragraph'))
        
        # 5. 发现错误并编辑文本
        processor.execute(EditTextCommand(model, 'para1', 'This is the first paragraph'))
        
        # 6. 删除段落并撤销
        processor.execute(DeleteCommand(model, 'para2'))
        processor.undo()  # 用户改变主意，撤销删除
        assert model.find_by_id('para2') is not None
        
        # 7. 重命名元素ID以提高可读性
        processor.execute(EditIdCommand(model, 'para1', 'introduction'))
        processor.execute(EditIdCommand(model, 'para2', 'details'))
        
        # 验证ID已更改
        assert model.find_by_id('introduction') is not None
        assert model.find_by_id('details') is not None
        
        # 8. 添加新段落，发现位置不对，移动(通过删除并在正确位置重新创建)
        processor.execute(AppendCommand(model, 'p', 'conclusion', 'content', 'In conclusion...'))
        processor.execute(DeleteCommand(model, 'conclusion'))
        processor.execute(InsertCommand(model, 'p', 'conclusion', 'details', 'In conclusion...'))
        
        # 验证结构正确性
        content = model.find_by_id('content')
        children_ids = [c.id for c in content.children]
        assert 'introduction' in children_ids
        assert 'details' in children_ids
        assert 'conclusion' in children_ids
        
        details_idx = children_ids.index('details')
        conclusion_idx = children_ids.index('conclusion')
        
        # 确认conclusion现在位于details之前
        assert conclusion_idx < details_idx
        
        # 9. 最后保存文档
        temp_dir = setup['temp_dir']
        file_path = os.path.join(temp_dir, 'edited_document.html')
        processor.execute(SaveCommand(model, file_path))
        
        assert os.path.exists(file_path)

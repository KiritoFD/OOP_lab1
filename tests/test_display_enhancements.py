import pytest
from unittest.mock import patch, MagicMock
import tempfile
import os
import shutil

from src.session_manager import SessionManager
from src.commands.edit.append_command import AppendCommand
from src.commands.display_commands import PrintTreeCommand
from src.spellcheck.checker import SpellChecker, SpellError
from src.commands.io_commands import InitCommand

class TestDisplayEnhancements:
    """测试HTML树形结构的显示增强功能"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def setup_session(self, temp_dir):
        """设置测试环境"""
        session = SessionManager()
        
        # 创建临时文件
        temp_path = os.path.join(temp_dir, "test_display.html")
        
        # 确保文件内容写入
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write("""<!DOCTYPE html>
<html id="html">
    <head id="head"><title id="title">Test</title></head>
    <body id="body"></body>
</html>""")
            f.flush()
        
        # 确保文件存在
        assert os.path.exists(temp_path), f"文件未创建: {temp_path}"
        assert os.path.getsize(temp_path) > 0, f"文件为空: {temp_path}"
        
        with open(temp_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"文件内容: {content[:50]}...")
        
        # 加载临时文件
        success = session.load(temp_path)
        assert success, f"加载文件失败: {temp_path}"
        
        # 确保文件已经正确加载
        assert session.active_editor is not None, "活动编辑器为空"
        
        # 添加一些元素用于测试
        session.execute_command(AppendCommand(session.get_active_model(), "div", "container", "body"))
        session.execute_command(AppendCommand(session.get_active_model(), "h1", "title", "container", "Page Title"))
        session.execute_command(AppendCommand(session.get_active_model(), "p", "paragraph", "container", "This is a paragraph with misspellng."))
        
        # 保存更改
        session.save()
        
        return session

    def test_showid_setting(self, setup_session):
        """测试showid设置"""
        session = setup_session
        
        # 确保有活动编辑器
        assert session.active_editor is not None
        
        # 初始应该为True
        assert session.get_show_id() is True
        
        # 设置为False
        session.set_show_id(False)
        assert session.get_show_id() is False
        
        # 再次设置为True
        session.set_show_id(True)
        assert session.get_show_id() is True
    
    @patch('builtins.print')
    def test_tree_display_with_id(self, mock_print, setup_session):
        """测试显示ID的树形结构"""
        session = setup_session
        
        # 确保显示ID
        session.set_show_id(True)
        
        # 执行树形显示命令
        command = PrintTreeCommand(session.get_active_model())
        session.execute_command(command)
        
        # 检查print调用
        mock_calls = [call[0][0] for call in mock_print.call_args_list]
        
        # 检查ID是否显示
        id_found = False
        for call in mock_calls:
            if "#html" in call or "#body" in call or "#container" in call or "#title" in call or "#paragraph" in call:
                id_found = True
                break
                
        assert id_found, "没有找到任何ID显示在输出中"
    
    @patch('builtins.print')
    def test_tree_display_without_id(self, mock_print, setup_session):
        """测试不显示ID的树形结构"""
        session = setup_session
        
        # 设置不显示ID
        session.set_show_id(False)
        
        # 执行树形显示命令
        command = PrintTreeCommand(session.get_active_model())
        session.execute_command(command)
        
        # 检查print调用
        mock_calls = [call[0][0] for call in mock_print.call_args_list]
        output = '\n'.join(mock_calls)
        
        # 检查ID是否不显示
        assert "#html" not in output
        assert "#body" not in output
        assert "#container" not in output
        assert "#title" not in output
        assert "#paragraph" not in output
    
    @patch('src.spellcheck.checker.SpellChecker.check_text')
    @patch('builtins.print')
    def test_tree_display_with_spelling_errors(self, mock_print, mock_check_text, setup_session):
        """测试带有拼写错误标记的树形结构"""
        session = setup_session
        
        # 模拟拼写检查结果
        mock_check_text.side_effect = lambda text: (
            [SpellError('misspellng', ['misspelling'], text, 0, 10)] 
            if 'misspellng' in text else []
        )
        
        # 执行树形显示命令
        command = PrintTreeCommand(session.get_active_model())
        session.execute_command(command)
        
        # 检查print调用
        mock_calls = [call[0][0] for call in mock_print.call_args_list]
        output = '\n'.join(mock_calls)
        
        # 检查是否有带[X]标记的<p>
        p_with_error = False
        for call in mock_calls:
            if "[X] <p>" in call.replace(" ", ""):
                p_with_error = True
                break
                
        assert p_with_error, "没有找到带有[X]标记的<p>元素"
        
        # 确认其他元素没有错误标记
        for call in mock_calls:
            if "<html>" in call:
                assert "[X]" not in call, "html元素不应有错误标记"
            if "<div>" in call and "container" in call:
                assert "[X]" not in call, "div元素不应有错误标记"
            if "<h1>" in call:
                assert "[X]" not in call, "h1元素不应有错误标记"
    
    @patch('src.spellcheck.checker.SpellChecker.check_text')
    @patch('builtins.print')
    def test_tree_display_with_errors_no_ids(self, mock_print, mock_check_text, setup_session):
        """测试同时有拼写错误标记但不显示ID的树形结构"""
        session = setup_session
        
        # 设置不显示ID
        session.set_show_id(False)
        
        # 模拟拼写检查结果
        mock_check_text.side_effect = lambda text: (
            [SpellError('misspellng', ['misspelling'], text, 0, 10)] 
            if 'misspellng' in text else []
        )
        
        # 执行树形显示命令
        command = PrintTreeCommand(session.get_active_model())
        session.execute_command(command)
        
        # 检查print调用
        mock_calls = [call[0][0] for call in mock_print.call_args_list]
        output = '\n'.join(mock_calls)
        
        # 检查是否有带[X]标记的<p>
        p_with_error = False
        for call in mock_calls:
            if "[X] <p>" in call.replace(" ", ""):
                p_with_error = True
                break
                
        assert p_with_error, "没有找到带有[X]标记的<p>元素"
        
        # 检查ID不存在
        assert "#paragraph" not in output
        assert "#title" not in output

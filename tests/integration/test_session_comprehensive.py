import os
import pytest
import tempfile
import shutil
from unittest.mock import patch, MagicMock

from src.session.session_manager import SessionManager, Editor
from src.commands.edit.append_command import AppendCommand
from src.commands.edit.edit_text_command import EditTextCommand
from src.commands.edit.delete_command import DeleteCommand
from src.commands.edit.edit_id_command import EditIdCommand
from src.commands.io import InitCommand, SaveCommand, ReadCommand
from src.core.exceptions import ElementNotFoundError, DuplicateIdError, InvalidOperationError
from src.commands.command_exceptions import CommandExecutionError, CommandParameterError

@pytest.mark.integration
class TestSessionComprehensive:
    """全面测试会话管理功能"""
    
    @pytest.fixture
    def temp_dir(self):
        """创建临时目录用于测试文件操作"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def session(self):
        """创建会话管理器实例"""
        return SessionManager()
    
    def test_editor_init(self):
        """测试编辑器初始化"""
        editor = Editor("test.html")
        assert editor.filename == "test.html"
        assert editor.modified is False
        assert editor.model is not None
        assert editor.processor is not None
    
    def test_load_new_file(self, session, temp_dir):
        """测试加载不存在的文件(创建新文件)"""
        new_file = os.path.join(temp_dir, "new.html")
        session.load(new_file)
        
        assert session.active_editor is not None
        assert session.active_editor.filename == os.path.normpath(new_file)
        assert not session.active_editor.modified
        
        # 验证新文件已使用默认结构初始化
        html_element = session.get_active_model().find_by_id('html')
        assert html_element is not None
        assert html_element.tag == 'html'
    
    def test_load_existing_file(self, session, temp_dir):
        """测试加载已存在的HTML文件"""
        # 创建一个包含HTML内容的文件
        file_path = os.path.join(temp_dir, "existing.html")
        html_content = """<!DOCTYPE html>
<html id="html">
  <head id="head">
    <title id="title">Test Page</title>
  </head>
  <body id="body">
    <div id="content">Existing content</div>
  </body>
</html>
"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # 加载现有文件
        session.load(file_path)
        
        # 验证文件内容已正确加载
        assert session.get_active_model().find_by_id('content') is not None
        assert session.get_active_model().find_by_id('title') is not None
        assert session.get_active_model().find_by_id('content').text == 'Existing content'
    
    def test_save_file(self, session, temp_dir):
        """测试保存文件"""
        # 创建测试文件
        file_path = os.path.join(temp_dir, "test.html")
        session.load(file_path)
        
        # 先添加一些内容
        cmd = AppendCommand(session.get_active_model(), "div", "test-div", "body", "Test content")
        session.execute_command(cmd)
        assert session.active_editor.modified is True
        
        # 保存文件
        session.save()
        assert not session.active_editor.modified
        
        # 验证文件已保存
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "test-div" in content
            assert "Test content" in content
    
    def test_editor_save_as(self, session, temp_dir):
        """测试文件另存为"""
        # 创建原始文件
        orig_path = os.path.join(temp_dir, "original.html")
        new_path = os.path.join(temp_dir, "new_location.html")
        
        # 加载并修改原始文件
        session.load(orig_path)
        session.execute_command(AppendCommand(session.get_active_model(), "div", "testdiv", "body", "Test content"))
        
        # 另存为新文件
        session.save(new_path)
        
        # 验证两个文件都存在于编辑器列表中
        assert len(session.editors) == 2
        assert os.path.normpath(orig_path) in session.editors
        assert os.path.normpath(new_path) in session.editors
        
        # 验证活动编辑器已切换为新文件
        assert session.active_editor.filename == os.path.normpath(new_path)
        
        # 验证新文件内容正确
        assert os.path.exists(new_path)
        with open(new_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "testdiv" in content
            assert "Test content" in content
    
    @patch('builtins.input', return_value='n')
    def test_close_file_no_save(self, mock_input, session, temp_dir):
        """测试关闭文件(不保存)"""
        # 创建两个测试文件
        file1_path = os.path.join(temp_dir, "file1.html")
        file2_path = os.path.join(temp_dir, "file2.html")
        session.load(file1_path)
        session.load(file2_path)
        
        # 修改第二个文件
        cmd = AppendCommand(session.get_active_model(), "div", "modified", "body")
        session.execute_command(cmd)
        
        # 关闭当前文件(第二个文件)
        session.close()
        
        # 验证第二个文件已关闭，活动编辑器切换为第一个文件
        assert len(session.editors) == 1
        assert os.path.normpath(file1_path) in session.editors
        assert session.active_editor.filename == os.path.normpath(file1_path)
        
        # 验证文件2未保存
        assert not os.path.exists(file2_path)
    
    @patch('builtins.input', return_value='y')
    def test_close_file_with_save(self, mock_input, session, temp_dir):
        """测试关闭文件(保存)"""
        # 创建测试文件
        file_path = os.path.join(temp_dir, "test.html")
        session.load(file_path)
        
        # 加载文件并修改
        cmd = AppendCommand(session.get_active_model(), "div", "save-before-close", "body")
        session.execute_command(cmd)
        
        # 关闭文件(应该提示保存)
        session.close()
        
        # 验证文件已保存
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "save-before-close" in content
    
    def test_close_all_files(self, session, temp_dir):
        """测试关闭所有文件"""
        # 创建测试文件
        file_path = os.path.join(temp_dir, "test.html")
        session.load(file_path)
        
        # 加载一个文件
        session.load(file_path)
        
        # 关闭这个文件
        session.close()
        
        # 验证没有活动编辑器
        assert len(session.editors) == 0
        assert session.active_editor is None
    
    def test_editor_list(self, session, temp_dir, capsys):
        """测试编辑器列表显示"""
        # 创建两个测试文件
        file1_path = os.path.join(temp_dir, "file1.html")
        file2_path = os.path.join(temp_dir, "file2.html")
        session.load(file1_path)
        session.load(file2_path)
        
        # 修改第二个文件
        cmd = AppendCommand(session.get_active_model(), "div", "modified", "body")
        session.execute_command(cmd)
        
        # 显示编辑器列表
        session.editor_list()
        
        # 验证输出
        captured = capsys.readouterr()
        output = captured.out
        
        # 过滤输出，只保留编辑器列表相关的行
        editor_list_lines = [line for line in output.split('\n') if "file1.html" in line or "file2.html" in line or ">" in line]
        editor_list_output = "\n".join(editor_list_lines)
        
        # 检查格式: 活动文件前有 >，修改过的文件后有 *
        assert "当前打开的文件:" not in editor_list_output
        assert "file1.html" in editor_list_output
        assert "file2.html" in editor_list_output
        assert ">file2.html*" in editor_list_output.replace(" ", "")  # 活动且已修改
        assert "file1.html" in editor_list_output  # 非活动未修改
    
    def test_switch_active_file(self, session, temp_dir):
        """测试切换活动文件"""
        # 创建两个测试文件
        file1_path = os.path.join(temp_dir, "file1.html")
        file2_path = os.path.join(temp_dir, "file2.html")
        session.load(file1_path)
        session.load(file2_path)
        
        # 切换到第一个文件
        session.edit(file1_path)
        assert session.active_editor.filename == os.path.normpath(file1_path)
    
    def test_execute_command(self, session, temp_dir):
        """测试在活动编辑器上执行命令"""
        # 创建测试文件
        file_path = os.path.join(temp_dir, "test.html")
        session.load(file_path)
        
        # 加载文件
        session.load(file_path)
        
        # 执行命令
        cmd = AppendCommand(session.get_active_model(), "div", "test-div", "body", "Command executed")
        session.execute_command(cmd)
        
        assert session.active_editor.modified is True
        
        # 验证命令执行结果
        element = session.get_active_model().find_by_id('test-div')
        assert element is not None
        assert element.text == "Command executed"
    
    def test_undo_redo_commands(self, session, temp_dir):
        """测试在活动编辑器上执行撤销和重做操作"""
        # 创建测试文件
        file_path = os.path.join(temp_dir, "test.html")
        session.load(file_path)
        
        # 加载文件
        session.load(file_path)
        
        # 执行命令
        cmd = AppendCommand(session.get_active_model(), "div", "undo-test", "body")
        session.execute_command(cmd)
        
        # 撤销命令
        session.undo()
        
        # 验证元素已删除
        with pytest.raises(ElementNotFoundError):
            session.get_active_model().find_by_id('undo-test')
        
        # 重做命令
        session.redo()
        
        # 验证元素已恢复
        element = session.get_active_model().find_by_id('undo-test')
        assert element is not None
    
    def test_per_editor_command_history(self, session, temp_dir):
        """测试每个编辑器有独立的命令历史"""
        # 创建两个测试文件
        file1_path = os.path.join(temp_dir, "file1.html")
        file2_path = os.path.join(temp_dir, "file2.html")
        session.load(file1_path)
        session.load(file2_path)
        
        # 加载两个文件
        session.load(file1_path)
        
        # 在第一个文件添加元素
        cmd1 = AppendCommand(session.get_active_model(), "div", "file1-div", "body")
        session.execute_command(cmd1)
        
        # 加载第二个文件
        session.load(file2_path)
        
        # 在第二个文件添加元素
        cmd2 = AppendCommand(session.get_active_model(), "div", "file2-div", "body")
        session.execute_command(cmd2)
        
        # 验证第二个文件的命令历史
        assert session.active_editor.model.find_by_id('file2-div') is not None
        session.undo()  # 撤销第二个文件的操作
        with pytest.raises(ElementNotFoundError):
            session.active_editor.model.find_by_id('file2-div')
        
        # 切换到第一个文件
        session.edit(file1_path)
        
        # 验证第一个文件的命令历史
        assert session.active_editor.model.find_by_id('file1-div') is not None
        session.undo()  # 撤销第一个文件的操作
        with pytest.raises(ElementNotFoundError):
            session.active_editor.model.find_by_id('file1-div')
    
    def test_no_active_editor(self, session, capsys):
        """测试没有活动编辑器时的处理"""
        # 尝试在没有活动编辑器时执行命令
        cmd = AppendCommand(None, "div", "test-div", "body")
        result = session.execute_command(cmd)
        assert result is False
        
        # 尝试撤销/重做
        assert session.undo() is False
        assert session.redo() is False
        
        # 检查错误消息
        captured = capsys.readouterr()
        assert "没有活动编辑器" in captured.out
    
    def test_complete_workflow(self, session, temp_dir):
        """测试完整的工作流程: 加载-编辑-保存-关闭"""
        # 创建测试文件路径
        file_path = os.path.join(temp_dir, "workflow.html")
        
        # 1. 加载新文件(不存在，会创建)
        session.load(file_path)
        assert session.active_editor is not None
        assert not session.active_editor.modified
        
        # 2. 添加一些内容
        cmd1 = AppendCommand(session.get_active_model(), "div", "container", "body")
        cmd2 = AppendCommand(session.get_active_model(), "h1", "title", "container", "Welcome")
        cmd3 = AppendCommand(session.get_active_model(), "p", "para", "container", "Test paragraph")
        
        session.execute_command(cmd1)
        session.execute_command(cmd2)
        session.execute_command(cmd3)
        
        # 验证内容已添加
        assert session.active_editor.modified is True
        assert session.get_active_model().find_by_id('container') is not None
        assert session.get_active_model().find_by_id('title') is not None
        assert session.get_active_model().find_by_id('para') is not None
        
        # 3. 保存文件
        session.save()
        assert os.path.exists(file_path)
        assert not session.active_editor.modified
        
        # 4. 进一步编辑并测试撤销/重做
        cmd4 = EditTextCommand(session.get_active_model(), "title", "New Title")
        session.execute_command(cmd4)
        assert session.get_active_model().find_by_id('title').text == "New Title"
        assert session.active_editor.modified is True
        
        # 撤销编辑
        session.undo()
        assert session.get_active_model().find_by_id('title').text == "Welcome"
        
        # 重做编辑
        session.redo()
        assert session.get_active_model().find_by_id('title').text == "New Title"
        
        # 5. 保存并关闭
        session.save()
        with patch('builtins.input', return_value='n'):  # 如有需要，回答"不保存"
            session.close()
        
        assert len(session.editors) == 0
        assert session.active_editor is None
    
    @patch('builtins.input', return_value='y')
    def test_multiple_files_workflow(self, mock_input, session, temp_dir):
        """测试多文件工作流程"""
        # 创建两个测试文件路径
        file1_path = os.path.join(temp_dir, "file1.html")
        file2_path = os.path.join(temp_dir, "file2.html")
        
        # 1. 加载第一个文件
        session.load(file1_path)
        
        # 添加内容
        session.execute_command(AppendCommand(session.get_active_model(), "div", "file1-div", "body", "File 1 content"))
        
        # 2. 加载第二个文件
        session.load(file2_path)
        
        # 添加不同的内容
        session.execute_command(AppendCommand(session.get_active_model(), "div", "file2-div", "body", "File 2 content"))
        
        # 验证当前活动编辑器是第二个文件
        assert session.active_editor.filename == os.path.normpath(file2_path)
        assert session.get_active_model().find_by_id('file2-div') is not None
        
        # 3. 切换回第一个文件
        session.edit(file1_path)
        
        # 验证活动编辑器已切换
        assert session.active_editor.filename == os.path.normpath(file1_path)
        assert session.get_active_model().find_by_id('file1-div') is not None
        
        # 4. 保存所有文件
        session.save()
        session.edit(file2_path)
        session.save()
        
        # 验证两个文件都已保存
        assert os.path.exists(file1_path)
        assert os.path.exists(file2_path)
        
        # 5. 关闭第一个文件
        session.edit(file1_path)
        session.close()
        
        # 验证第一个文件已关闭，第二个成为活动编辑器
        assert len(session.editors) == 1
        assert session.active_editor.filename == os.path.normpath(file2_path)
        
        # 6. 关闭第二个文件
        session.close()
        assert len(session.editors) == 0
    
    def test_file_modification_tracking(self, session, temp_dir):
        """测试文件修改状态跟踪"""
        file_path = os.path.join(temp_dir, "modified.html")
        
        # 1. 加载文件
        session.load(file_path)
        assert not session.active_editor.modified
        
        # 2. 进行编辑
        session.execute_command(AppendCommand(session.get_active_model(), "div", "content", "body"))
        assert session.active_editor.modified is True
        
        # 3. 保存文件
        session.save()
        assert not session.active_editor.modified
        
        # 4. 编辑、撤销、重做的修改状态跟踪
        session.execute_command(AppendCommand(session.get_active_model(), "p", "para", "content"))
        assert session.active_editor.modified is True
        
        session.save()
        assert not session.active_editor.modified
        
        # 撤销应将文件标记为已修改
        session.undo()
        assert session.active_editor.modified is True
        
        # 重做应将文件标记为已修改(虽然内容与保存时相同)
        session.redo()
        assert session.active_editor.modified is True
    
    def test_error_handling(self, session, temp_dir, capsys):
        """测试错误处理"""
        file_path = os.path.join(temp_dir, "errors.html")
        
        # 1. 加载文件
        session.load(file_path)
        
        # 2. 尝试执行会失败的命令
        session.execute_command(DeleteCommand(session.get_active_model(), "nonexistent"))
        
        # 捕获输出验证错误处理
        captured = capsys.readouterr()
        assert "执行命令失败" in captured.out
        
        # 3. 尝试编辑不存在的文件
        # 创建测试文件
        file_path = os.path.join(temp_dir, "test.html")
        session.load(file_path)
        
        result = session.edit("nonexistent.html")
        assert result is False
        
        captured = capsys.readouterr()
        assert "未加载" in captured.out
    
    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_save_error_handling(self, mock_open, session, temp_dir):
        """测试保存错误处理"""
        # 创建测试文件
        file_path = os.path.join(temp_dir, "test.html")
        session.load(file_path)
        
        # 加载文件
        session.load(file_path)
        
        # 使用模拟对象模拟权限错误
        result = session.save()
        assert result is False
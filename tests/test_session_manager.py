import pytest
import os
import shutil
from unittest.mock import patch, MagicMock
from src.session.session_manager import SessionManager, Editor
from src.commands.display import PrintTreeCommand
from src.utils.spell_checker import SpellChecker

class TestEditor:
    """测试Editor类的功能"""
    
    @pytest.fixture
    def setup_test_files(self):
        """设置测试环境和文件"""
        # 创建测试目录
        test_dir = os.path.join(os.getcwd(), "test_files")
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)
            
        # 创建测试文件
        test_file = os.path.join(test_dir, "test.html")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("<html><body><p>Test content</p></body></html>")
            
        # 返回测试文件和目录
        yield test_file, test_dir
        
        # 测试后清理
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
    
    def test_load_existing_file(self, setup_test_files):
        """测试加载现有文件"""
        test_file, _ = setup_test_files
        editor = Editor(test_file)
        
        result = editor.load()
        
        assert result == True
        assert editor.modified == False
    
    def test_load_new_file(self, setup_test_files):
        """测试加载不存在的文件（创建新文件）"""
        _, test_dir = setup_test_files
        new_file = os.path.join(test_dir, "new.html")
        editor = Editor(new_file)
        
        result = editor.load()
        
        assert result == True
        assert editor.modified == False
    
    def test_save_file(self, setup_test_files):
        """测试保存文件"""
        test_file, _ = setup_test_files
        editor = Editor(test_file)
        editor.load()
        
        # 标记文件为已修改
        editor.modified = True
        
        result = editor.save()
        
        assert result == True
        assert editor.modified == False
    
    def test_undo_redo(self):
        """测试撤销和重做操作"""
        # 创建模拟对象
        editor = Editor("test.html")
        editor.processor = MagicMock()
        
        # 设置模拟的undo方法返回值
        editor.processor.undo.return_value = True
        
        # 测试撤销
        result = editor.undo()
        assert result == True
        assert editor.modified == True
        editor.processor.undo.assert_called_once()
        
        # 设置模拟的redo方法返回值
        editor.processor.redo.return_value = True
        
        # 测试重做
        result = editor.redo()
        assert result == True
        assert editor.modified == True
        editor.processor.redo.assert_called_once()
    
    @pytest.mark.parametrize("mock_result,expected_modified", [(True, True), (False, False)])
    def test_execute_command(self, mock_result, expected_modified):
        """测试执行命令"""
        # 创建模拟对象
        editor = Editor("test.html")
        editor.processor = MagicMock()
        mock_command = MagicMock()
        mock_command.recordable = True
        
        # 设置模拟的execute方法返回值
        editor.processor.execute.return_value = mock_result
        
        # 执行测试
        result = editor.execute_command(mock_command)
        
        assert result == mock_result
        assert editor.modified == expected_modified


class TestSessionManager:
    """测试SessionManager类的功能"""
    
    @pytest.fixture
    def setup_test_environment(self):
        """设置测试环境和文件"""
        # 创建测试目录
        test_dir = os.path.join(os.getcwd(), "test_files")
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)
            
        # 创建测试文件
        test_file1 = os.path.join(test_dir, "file1.html")
        test_file2 = os.path.join(test_dir, "file2.html")
        
        with open(test_file1, 'w', encoding='utf-8') as f:
            f.write("<html><body><p>File 1</p></body></html>")
            
        with open(test_file2, 'w', encoding='utf-8') as f:
            f.write("<html><body><p>File 2</p></body></html>")
            
        # 初始化会话管理器
        mock_state_manager = MagicMock()
        session_manager = SessionManager(mock_state_manager)
        
        # 返回测试对象
        yield session_manager, test_file1, test_file2, test_dir
        
        # 测试后清理
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
    
    def test_load_file(self, setup_test_environment):
        """测试加载文件"""
        session_manager, test_file1, test_file2, _ = setup_test_environment
        
        # 加载第一个文件
        result1 = session_manager.load(test_file1)
        assert result1 == True
        assert session_manager.active_editor.filename == os.path.abspath(test_file1)
        
        # 加载第二个文件
        result2 = session_manager.load(test_file2)
        assert result2 == True
        assert session_manager.active_editor.filename == os.path.abspath(test_file2)
        
        # 确认有两个编辑器
        assert len(session_manager.editors) == 2
    
    def test_save_file(self, setup_test_environment):
        """测试保存文件"""
        session_manager, test_file1, _, _ = setup_test_environment
        
        # 加载文件
        session_manager.load(test_file1)
        
        # 修改文件
        session_manager.active_editor.modified = True
        
        # 保存文件
        result = session_manager.save()
        assert result == True
        assert session_manager.active_editor.modified == False
    
    def test_close_file(self, setup_test_environment):
        """测试关闭文件"""
        session_manager, test_file1, test_file2, _ = setup_test_environment
        
        # 加载两个文件
        session_manager.load(test_file1)
        session_manager.load(test_file2)
        
        # 断言当前活动文件
        assert session_manager.active_editor.filename == os.path.abspath(test_file2)
        
        # 关闭当前文件 (模拟用户不保存)
        with patch('builtins.input', return_value='n'):
            session_manager.close()
        
        # 断言新的活动文件
        assert session_manager.active_editor.filename == os.path.abspath(test_file1)
        
        # 断言只有一个编辑器
        assert len(session_manager.editors) == 1
        
        # 关闭最后一个文件
        with patch('builtins.input', return_value='n'):
            session_manager.close()
        
        # 断言没有编辑器
        assert len(session_manager.editors) == 0
        assert session_manager.active_editor is None
    
    def test_close_modified_file(self, setup_test_environment):
        """测试关闭已修改的文件"""
        session_manager, test_file1, _, _ = setup_test_environment
        
        # 加载文件
        session_manager.load(test_file1)
        
        # 修改文件
        session_manager.active_editor.modified = True
        
        # 关闭文件 (模拟用户保存)
        with patch('builtins.input', return_value='y'):
            # 模拟save方法
            with patch.object(session_manager.active_editor, 'save', return_value=True) as mock_save:
                session_manager.close()
                mock_save.assert_called_once()
        
        # 断言没有编辑器
        assert len(session_manager.editors) == 0
    
    def test_editor_list(self, setup_test_environment):
        """测试编辑器列表功能"""
        session_manager, test_file1, test_file2, _ = setup_test_environment
        
        # 加载两个文件
        session_manager.load(test_file1)
        session_manager.load(test_file2)
        
        # 修改第二个文件
        session_manager.active_editor.modified = True
        
        # 捕获print输出
        with patch('builtins.print') as mock_print:
            session_manager.editor_list()
            
            # 验证输出包含预期的内容
            mock_print.assert_any_call("当前打开的文件:")
            mock_print.assert_any_call(f"> {os.path.basename(test_file2)}*")
            mock_print.assert_any_call(f"  {os.path.basename(test_file1)}")
    
    def test_edit_file(self, setup_test_environment):
        """测试切换活动编辑器"""
        session_manager, test_file1, test_file2, _ = setup_test_environment
        
        # 加载两个文件
        session_manager.load(test_file1)
        session_manager.load(test_file2)
        
        # 断言当前活动文件
        assert session_manager.active_editor.filename == os.path.abspath(test_file2)
        
        # 切换到第一个文件
        result = session_manager.edit(test_file1)
        assert result == True
        
        # 断言新的活动文件
        assert session_manager.active_editor.filename == os.path.abspath(test_file1)
    
    def test_edit_nonexistent_file(self, setup_test_environment):
        """测试切换到不存在的文件"""
        session_manager, test_file1, _, _ = setup_test_environment
        
        # 加载一个文件
        session_manager.load(test_file1)
        
        # 尝试切换到不存在的文件
        result = session_manager.edit("nonexistent.html")
        assert result == False
        
        # 确认活动文件没有变化
        assert session_manager.active_editor.filename == os.path.abspath(test_file1)
    
    def test_set_show_id(self, setup_test_environment):
        """测试设置显示ID选项"""
        session_manager, test_file1, _, _ = setup_test_environment
        
        # 加载文件
        session_manager.load(test_file1)
        
        # 默认应该显示ID
        assert session_manager.get_show_id() == True
        
        # 设置为不显示ID
        result = session_manager.set_show_id(False)
        assert result == True
        assert session_manager.get_show_id() == False
        
        # 设置为显示ID
        result = session_manager.set_show_id(True)
        assert result == True
        assert session_manager.get_show_id() == True
    
    def test_execute_command_with_print_tree(self, setup_test_environment):
        """测试执行PrintTreeCommand命令时的特殊处理"""
        session_manager, test_file1, _, _ = setup_test_environment
        
        # 加载文件
        session_manager.load(test_file1)
        
        # 设置不显示ID
        session_manager.set_show_id(False)
        
        # 创建模拟的PrintTreeCommand
        mock_command = MagicMock(spec=PrintTreeCommand)
        mock_command.show_id = None
        mock_command.formatter = MagicMock()
        
        # 执行命令
        with patch.object(session_manager.active_editor, 'execute_command', return_value=True) as mock_execute:
            result = session_manager.execute_command(mock_command)
            assert result == True
            mock_execute.assert_called_once_with(mock_command)
        
        # 验证show_id被设置为编辑器的值
        assert mock_command.show_id == False


class TestMultiFileIntegration:
    """多文件编辑功能集成测试"""
    
    @pytest.fixture
    def setup_integration(self):
        """设置集成测试环境"""
        # 创建测试目录
        test_dir = os.path.join(os.getcwd(), "test_integration")
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)
            
        # 创建测试文件
        test_file1 = os.path.join(test_dir, "file1.html")
        test_file2 = os.path.join(test_dir, "file2.html")
        test_file3 = os.path.join(test_dir, "file3.html")
        
        with open(test_file1, 'w', encoding='utf-8') as f:
            f.write("<html><body><p>File 1</p></body></html>")
            
        with open(test_file2, 'w', encoding='utf-8') as f:
            f.write("<html><body><p>File 2</p></body></html>")
            
        with open(test_file3, 'w', encoding='utf-8') as f:
            f.write("<html><body><p>File 3</p></body></html>")
        
        # 初始化会话管理器
        session_manager = SessionManager()
        
        # 返回测试对象
        yield session_manager, test_file1, test_file2, test_file3, test_dir
        
        # 测试后清理
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
    
    def test_complete_workflow(self, setup_integration):
        """测试完整的工作流程"""
        session_manager, test_file1, test_file2, test_file3, _ = setup_integration
        
        # 1. 加载文件1
        session_manager.load(test_file1)
        assert len(session_manager.editors) == 1
        assert session_manager.active_editor.filename == os.path.abspath(test_file1)
        
        # 2. 加载文件2
        session_manager.load(test_file2)
        assert len(session_manager.editors) == 2
        assert session_manager.active_editor.filename == os.path.abspath(test_file2)
        
        # 3. 切换回文件1
        session_manager.edit(test_file1)
        assert session_manager.active_editor.filename == os.path.abspath(test_file1)
        
        # 4. 修改文件1（模拟）
        session_manager.active_editor.modified = True
        
        # 5. 加载文件3
        session_manager.load(test_file3)
        assert len(session_manager.editors) == 3
        assert session_manager.active_editor.filename == os.path.abspath(test_file3)
        
        # 6. 关闭文件3
        session_manager.close()
        assert len(session_manager.editors) == 2
        # 此时活动编辑器应该是列表中的第一个
        assert session_manager.active_editor is not None
        assert session_manager.active_editor.filename in [os.path.abspath(test_file1), os.path.abspath(test_file2)]
        
        # 7. 检查文件1仍然标记为已修改
        file1_editor = None
        for filename, editor in session_manager.editors.items():
            if os.path.abspath(filename) == os.path.abspath(test_file1):
                file1_editor = editor
                break
                
        assert file1_editor is not None
        assert file1_editor.modified == True
        
        # 8. 切换到文件1并保存
        session_manager.edit(test_file1)
        assert session_manager.active_editor.filename == os.path.abspath(test_file1)
        session_manager.save()
        assert session_manager.active_editor.modified == False
        
        # 9. 关闭所有文件
        while session_manager.editors:
            session_manager.close()
            
        # 10. 确认没有活动编辑器
        assert len(session_manager.editors) == 0
        assert session_manager.active_editor is None


class TestHtmlTreeDisplay:
    """测试HTML树形结构的显示增强功能"""
    
    @pytest.fixture
    def setup_html_display_test(self):
        """设置HTML显示测试环境"""
        test_dir = os.path.join(os.getcwd(), "test_html_display")
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)
            
        # 创建测试文件
        test_file = os.path.join(test_dir, "test_display.html")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write('<html><body><p id="para1">Test content</p><div class="misspelled">错误的单词</div></body></html>')
            
        # 初始化会话管理器和编辑器
        session_manager = SessionManager()
        
        # 返回测试对象
        yield session_manager, test_file, test_dir
        
        # 测试后清理
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
    
    def test_show_id_option(self, setup_html_display_test):
        """测试显示/隐藏ID选项"""
        session_manager, test_file, _ = setup_html_display_test
        
        # 加载测试文件
        session_manager.load(test_file)
        
        # 创建用于捕获输出的模拟PrintTreeCommand
        mock_print_cmd_show_id = MagicMock(spec=PrintTreeCommand)
        mock_print_cmd_show_id.show_id = None
        mock_print_cmd_show_id.formatter = MagicMock()
        
        # 测试默认应该显示ID
        with patch.object(session_manager.active_editor, 'execute_command') as mock_execute:
            session_manager.execute_command(mock_print_cmd_show_id)
            assert mock_print_cmd_show_id.show_id == True
        
        # 设置为不显示ID
        session_manager.set_show_id(False)
        
        # 创建新的模拟命令
        mock_print_cmd_hide_id = MagicMock(spec=PrintTreeCommand)
        mock_print_cmd_hide_id.show_id = None
        mock_print_cmd_hide_id.formatter = MagicMock()
        
        # 测试此时不应该显示ID
        with patch.object(session_manager.active_editor, 'execute_command') as mock_execute:
            session_manager.execute_command(mock_print_cmd_hide_id)
            assert mock_print_cmd_hide_id.show_id == False
    
    def test_spelling_error_marking(self, setup_html_display_test):
        """测试拼写错误标记功能"""
        session_manager, test_file, _ = setup_html_display_test
        
        # 加载测试文件
        session_manager.load(test_file)
        
        # 模拟HTML节点
        mock_node_with_error = MagicMock()
        mock_node_with_error.text = "错误的单词"
        mock_node_without_error = MagicMock()
        mock_node_without_error.text = "正确单词"
        mock_node_without_error.attributes = {}
        mock_node_without_error.children = []
        
        # 模拟SpellChecker
        with patch('src.utils.spell_checker.SpellChecker.get_instance') as mock_get_instance:
            mock_checker = MagicMock()
            mock_checker.has_errors.side_effect = lambda text: text == "错误的单词"
            mock_get_instance.return_value = mock_checker
            
            # 测试有拼写错误的节点
            assert session_manager.active_editor.has_spelling_errors(mock_node_with_error) == True
            
            # 测试无拼写错误的节点
            assert session_manager.active_editor.has_spelling_errors(mock_node_without_error) == False
            
            # 测试格式化器
            mock_formatter = MagicMock()
            session_manager.active_editor.mark_spelling_errors(mock_node_with_error, mock_formatter)
            assert mock_formatter.tag_prefix == "[X] "
            
            session_manager.active_editor.mark_spelling_errors(mock_node_without_error, mock_formatter)
            assert mock_formatter.tag_prefix == ""


class TestDirectoryDisplay:
    """测试文件目录显示功能"""
    
    @pytest.fixture
    def setup_directory_test(self):
        """设置目录树测试环境"""
        # 创建测试目录结构
        base_dir = os.path.join(os.getcwd(), "test_dir_tree")
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
            
        # 创建子目录
        sub_dir1 = os.path.join(base_dir, "subdir1")
        sub_dir2 = os.path.join(base_dir, "subdir2")
        os.makedirs(sub_dir1, exist_ok=True)
        os.makedirs(sub_dir2, exist_ok=True)
        
        # 创建测试文件
        test_file1 = os.path.join(base_dir, "file1.html")
        test_file2 = os.path.join(sub_dir1, "file2.html")
        test_file3 = os.path.join(sub_dir2, "file3.html")
        
        with open(test_file1, 'w') as f:
            f.write("<html><body>File 1</body></html>")
        with open(test_file2, 'w') as f:
            f.write("<html><body>File 2</body></html>")
        with open(test_file3, 'w') as f:
            f.write("<html><body>File 3</body></html>")
            
        # 创建会话管理器
        session_manager = SessionManager()
        
        # 保存当前目录
        old_dir = os.getcwd()
        # 切换到测试目录
        os.chdir(base_dir)
        
        # 返回测试对象
        yield session_manager, base_dir, test_file1, test_file2, test_file3, old_dir
        
        # 测试后清理
        os.chdir(old_dir)
        if os.path.exists(base_dir):
            shutil.rmtree(base_dir)
    
    def test_dir_tree_display(self, setup_directory_test):
        """测试目录树显示功能"""
        session_manager, base_dir, test_file1, test_file2, test_file3, _ = setup_directory_test
        
        # 加载一个文件
        session_manager.load(test_file1)
        
        # 捕获print输出
        with patch('builtins.print') as mock_print:
            session_manager.dir_tree()
            
            # 验证输出包含目录结构
            mock_print.assert_any_call(f"目录树: {os.getcwd()}")
            
            # 检查文件1是否标记为正在编辑
            expected_file1_output = f"├── file1.html *"
            found_file1 = any(call[0][0] == expected_file1_output for call in mock_print.call_args_list)
            assert found_file1, f"未找到预期输出: {expected_file1_output}"
            
            # 检查子目录是否显示
            expected_subdir1_output = f"├── subdir1/"
            found_subdir1 = any(call[0][0] == expected_subdir1_output for call in mock_print.call_args_list)
            assert found_subdir1, f"未找到预期输出: {expected_subdir1_output}"
    
    def test_dir_tree_with_multiple_open_files(self, setup_directory_test):
        """测试多个打开文件时的目录树显示"""
        session_manager, base_dir, test_file1, test_file2, test_file3, _ = setup_directory_test
        
        # 加载多个文件
        session_manager.load(test_file1)
        session_manager.load(test_file2)
        
        # 捕获print输出
        with patch('builtins.print') as mock_print:
            session_manager.dir_tree()
            
            # 验证输出包含目录结构
            mock_print.assert_any_call(f"目录树: {os.getcwd()}")
            
            # 检查文件1是否标记为正在编辑
            expected_file1_output = "file1.html *"
            found_file1 = False
            for call in mock_print.call_args_list:
                if isinstance(call[0][0], str) and expected_file1_output in call[0][0]:
                    found_file1 = True
                    break
            assert found_file1, f"未找到包含 {expected_file1_output} 的输出"
            
            # 检查子目录中的文件2是否标记为正在编辑
            expected_file2_output = "file2.html *"
            found_file2 = False
            for call in mock_print.call_args_list:
                if isinstance(call[0][0], str) and expected_file2_output in call[0][0]:
                    found_file2 = True
                    break
            assert found_file2, f"未找到包含 {expected_file2_output} 的输出"
            
            # 检查文件3是否未标记（不应该有星号）
            # 首先检查文件3存在于输出中
            expected_file3_name = "file3.html"
            found_file3_name = False
            found_file3_with_star = False
            
            for call in mock_print.call_args_list:
                if isinstance(call[0][0], str):
                    if expected_file3_name in call[0][0]:
                        found_file3_name = True
                        if expected_file3_name + " *" in call[0][0]:
                            found_file3_with_star = True
                            
            assert found_file3_name, f"未找到包含 {expected_file3_name} 的输出"
            assert not found_file3_with_star, f"文件3不应该被标记为打开状态，但找到了带星号的输出"

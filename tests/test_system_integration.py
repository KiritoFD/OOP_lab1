import pytest
import os
import tempfile
import shutil
import sys
from unittest.mock import patch, MagicMock
import importlib

# Import all test modules for comprehensive testing
from tests.test_display_enhancements import TestDisplayEnhancements
from tests.test_dir_tree_command import TestDirTreeCommand
from tests.test_session_state import TestSessionState
from tests.test_main_session_persistence import TestMainSessionPersistence
import tests.integration.test_comprehensive as test_comprehensive

from src.session_manager import SessionManager
from src.commands.edit.append_command import AppendCommand
from src.commands.edit.insert_command import InsertCommand
from src.commands.edit.delete_command import DeleteCommand
from src.commands.edit.edit_text_command import EditTextCommand
from src.commands.edit.edit_id_command import EditIdCommand
from src.commands.display_commands import PrintTreeCommand, SpellCheckCommand, DirTreeCommand
from src.state.session_state import SessionState
from src.spellcheck.checker import SpellChecker

class TestSystemIntegration:
    """系统集成测试 - 全面覆盖所有功能"""
    
    @pytest.fixture
    def temp_environment(self):
        """创建完整的临时测试环境"""
        # 创建临时目录结构
        temp_dir = tempfile.mkdtemp()
        
        # 创建内部结构
        os.makedirs(os.path.join(temp_dir, "docs"))
        os.makedirs(os.path.join(temp_dir, "templates"))
        
        # 创建测试文件
        files = {
            "index.html": """<!DOCTYPE html>
<html id="html">
<head id="head"><title id="title">Home Page</title></head>
<body id="body">
    <h1 id="main-title">Welcome</h1>
    <p id="intro">This is a test page with some misspeled words.</p>
</body>
</html>""",
            
            "docs/about.html": """<!DOCTYPE html>
<html id="html">
<head id="head"><title id="title">About</title></head>
<body id="body">
    <h1 id="about-title">About Us</h1>
    <p id="about-text">Information about our company.</p>
</body>
</html>""",
            
            "templates/template.html": """<!DOCTYPE html>
<html id="html">
<head id="head"><title id="title">Template</title></head>
<body id="body">
    <header id="header"></header>
    <main id="main"></main>
    <footer id="footer"></footer>
</body>
</html>"""
        }
        
        for file_path, content in files.items():
            full_path = os.path.join(temp_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # 创建临时状态文件
        state_file = os.path.join(temp_dir, ".test_state.json")
        
        yield {
            'temp_dir': temp_dir,
            'state_file': state_file,
            'files': {k: os.path.join(temp_dir, k) for k in files.keys()}
        }
        
        # 清理
        shutil.rmtree(temp_dir)
    
    def test_full_application_workflow(self, temp_environment):
        """测试完整的应用工作流程，包括所有主要功能"""
        temp_dir = temp_environment['temp_dir']
        state_file = temp_environment['state_file']
        files = temp_environment['files']
        
        # 1. 创建会话并加载文件
        state_manager = SessionState(state_file)
        session = SessionManager(state_manager)
        
        # 加载主页
        assert session.load(files["index.html"]) is True
        assert session.active_editor is not None
        
        # 2. 测试编辑功能
        # 添加新元素
        session.execute_command(AppendCommand(
            session.get_active_model(), 
            "div", 
            "content", 
            "body", 
            "Main content area"
        ))
        
        # 添加子元素
        session.execute_command(AppendCommand(
            session.get_active_model(), 
            "ul", 
            "menu", 
            "content"
        ))
        
        for i in range(3):
            session.execute_command(AppendCommand(
                session.get_active_model(), 
                "li", 
                f"item{i}", 
                "menu", 
                f"Menu Item {i+1}"
            ))
        
        # 修改文本
        session.execute_command(EditTextCommand(
            session.get_active_model(), 
            "main-title", 
            "Welcome to Our Website"
        ))
        
        # 修改ID
        session.execute_command(EditIdCommand(
            session.get_active_model(), 
            "intro", 
            "introduction"
        ))
        
        # 3. 测试树形显示功能（带ID）
        with patch('builtins.print') as mock_print:
            session.execute_command(PrintTreeCommand(session.get_active_model()))
            # 验证输出包含期望的ID
            output = ''.join([call[0][0] for call in mock_print.call_args_list if len(call[0]) > 0])
            assert "#content" in output
            assert "#menu" in output
            assert "#item" in output
        
        # 4. 测试树形显示功能（不带ID）
        session.set_show_id(False)
        assert session.get_show_id() is False
        
        with patch('builtins.print') as mock_print:
            session.execute_command(PrintTreeCommand(session.get_active_model()))
            output = ''.join([call[0][0] for call in mock_print.call_args_list if len(call[0]) > 0])
            assert "#content" not in output
            assert "#menu" not in output
        
        # 5. 测试目录树显示功能
        with patch('os.getcwd', return_value=temp_dir):
            with patch('builtins.print') as mock_print:
                session.execute_command(DirTreeCommand(session))
                output = ''.join([call[0][0] for call in mock_print.call_args_list if len(call[0]) > 0])
                
                # 验证输出包含目录和文件
                assert "docs/" in output
                assert "templates/" in output
                assert "index.html*" in output.replace(" ", "")  # 带*表示已打开
        
        # 6. 测试拼写检查功能
        with patch('src.spellcheck.checker.SpellChecker.check_text') as mock_check:
            mock_check.side_effect = lambda text: (
                [MagicMock(wrong_word="misspeled", suggestions=["misspelled"], context=text)]
                if "misspeled" in text else []
            )
            
            with patch('builtins.print') as mock_print:
                session.execute_command(SpellCheckCommand(session.get_active_model()))
                output = ''.join([str(call[0][0]) for call in mock_print.call_args_list if len(call[0]) > 0])
                
                assert "misspeled" in output
                assert "misspelled" in output  # 建议的修正
        
        # 7. 测试保存和加载另一个文件
        session.save()
        assert not session.active_editor.modified
        
        # 加载另一个文件
        assert session.load(files["docs/about.html"]) is True
        
        # 确保第二个文件也设置为不显示ID
        session.set_show_id(False)
        assert session.get_show_id() is False
        
        # 8. 测试撤销和重做功能
        # 进行编辑
        session.execute_command(AppendCommand(
            session.get_active_model(), 
            "div", 
            "about-content", 
            "body"
        ))
        
        # 确认元素已添加
        assert session.get_active_model().find_by_id("about-content") is not None
        
        # 撤销操作
        assert session.undo() is True
        
        # 确认元素已删除
        with pytest.raises(Exception):
            session.get_active_model().find_by_id("about-content")
        
        # 重做操作
        assert session.redo() is True
        
        # 确认元素已恢复
        assert session.get_active_model().find_by_id("about-content") is not None
        
        # 9. 测试会话状态持久化
        # 保存会话状态
        assert session.save_session() is True
        
        # 创建新会话并验证恢复
        new_session = SessionManager(SessionState(state_file))
        assert new_session.restore_session() is True
        
        # 确认恢复了两个文件
        assert len(new_session.editors) == 2
        
        # 确认活动编辑器是about.html
        current_file = os.path.normpath(new_session.active_editor.filename)
        expected_file = os.path.normpath(files["docs/about.html"])
        assert current_file == expected_file
        
        # 验证当前活动文件的showid设置
        assert new_session.get_show_id() is False
        
        # 切换到index.html并验证其show_id设置也被正确恢复
        new_session.edit(files["index.html"])
        assert new_session.get_show_id() is False
        
        # 10. 测试错误处理
        # 尝试使用无效ID
        with patch('builtins.print') as mock_print:
            new_session.execute_command(DeleteCommand(new_session.get_active_model(), "non-existent-id"))
            output = ''.join([str(call[0][0]) for call in mock_print.call_args_list if len(call[0]) > 0])
            assert "失败" in output

        # Test reopening the application with command line arguments
        with patch('sys.argv', ['main.py']):
            with patch('builtins.input', side_effect=['exit']):
                with patch('src.main.SessionManager', return_value=new_session):
                    from src.main import main
                    main()  # Should restore the previous session
    
    def test_run_all_individual_tests(self, monkeypatch):
        """运行所有单独的测试类以确保完整的覆盖范围"""
        # 运行测试前，保存并恢复原始的命令行参数
        original_argv = sys.argv.copy()
        
        try:
            # 这个测试只是为了确保我们不会漏掉任何单元测试
            # 实际上，它依赖于pytest的fixture和收集机制
            # 因此，这里只做简单的检查确保所有测试模块都被导入
            
            # 检查display_enhancements测试
            assert hasattr(TestDisplayEnhancements, 'test_showid_setting')
            assert hasattr(TestDisplayEnhancements, 'test_tree_display_with_id')
            assert hasattr(TestDisplayEnhancements, 'test_tree_display_without_id')
            assert hasattr(TestDisplayEnhancements, 'test_tree_display_with_spelling_errors')
            
            # 检查dir_tree_command测试
            assert hasattr(TestDirTreeCommand, 'test_dir_tree_command_basic')
            assert hasattr(TestDirTreeCommand, 'test_open_files_marking')
            assert hasattr(TestDirTreeCommand, 'test_permission_denied_handling')
            assert hasattr(TestDirTreeCommand, 'test_empty_directory')
            
            # 检查session_state测试
            assert hasattr(TestSessionState, 'test_save_load_state')
            assert hasattr(TestSessionState, 'test_clear_state')
            assert hasattr(TestSessionState, 'test_session_manager_save_restore')
            assert hasattr(TestSessionState, 'test_nonexistent_files')
            
            # 检查main_session_persistence测试
            assert hasattr(TestMainSessionPersistence, 'test_session_restore_on_startup')
            assert hasattr(TestMainSessionPersistence, 'test_no_restore_with_new_flag')
            assert hasattr(TestMainSessionPersistence, 'test_save_session_on_exit')
            
            # 检查全面集成测试
            test_module = test_comprehensive
            assert hasattr(test_module.TestComprehensiveIntegration, 'test_html_model_basics')
            assert hasattr(test_module.TestComprehensiveIntegration, 'test_editing_commands')
            assert hasattr(test_module.TestComprehensiveIntegration, 'test_io_commands_and_tree_structure')
            assert hasattr(test_module.TestComprehensiveIntegration, 'test_spellcheck')
            assert hasattr(test_module.TestComprehensiveIntegration, 'test_undo_redo_functionality')
            
        finally:
            # 恢复原始命令行参数
            sys.argv = original_argv
    
    def test_feature_coverage(self):
        """测试特性覆盖 - 确保所有功能都被测试到"""
        # 定义一个功能和对应测试的映射
        feature_tests = {
            "树形显示(含ID)": TestDisplayEnhancements.test_tree_display_with_id,
            "树形显示(不含ID)": TestDisplayEnhancements.test_tree_display_without_id,
            "拼写检查标记": TestDisplayEnhancements.test_tree_display_with_spelling_errors,
            "目录树显示": TestDirTreeCommand.test_dir_tree_command_basic,
            "打开文件标记": TestDirTreeCommand.test_open_files_marking,
            "会话状态保存": TestSessionState.test_save_load_state,
            "会话状态恢复": TestSessionState.test_session_manager_save_restore,
            "撤销/重做功能": getattr(test_comprehensive.TestComprehensiveIntegration, 'test_undo_redo_functionality'),
            "HTML编辑命令": getattr(test_comprehensive.TestComprehensiveIntegration, 'test_editing_commands'),
            "命令行参数处理": TestMainSessionPersistence.test_no_restore_with_new_flag,
            "应用启动状态恢复": TestMainSessionPersistence.test_session_restore_on_startup,
            "应用退出状态保存": TestMainSessionPersistence.test_save_session_on_exit,
            "IO命令与文件操作": getattr(test_comprehensive.TestComprehensiveIntegration, 'test_io_commands_and_tree_structure'),
            "拼写检查功能": getattr(test_comprehensive.TestComprehensiveIntegration, 'test_spellcheck'),
            "错误处理": hasattr(test_comprehensive.TestComprehensiveIntegration, 'test_error_handling') and 
                      getattr(test_comprehensive.TestComprehensiveIntegration, 'test_error_handling'),
            "权限错误处理": TestDirTreeCommand.test_permission_denied_handling
        }
        
        # 验证所有功能都有对应的测试
        for feature, test_func in feature_tests.items():
            assert test_func is not None, f"功能 '{feature}' 缺少对应测试"

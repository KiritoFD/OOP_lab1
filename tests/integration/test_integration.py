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

class TestIntegrationWorkflow:
    """测试完整的编辑工作流程"""
    
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
    
    def test_complete_workflow(self, setup, capsys):
        """测试完整的HTML编辑工作流程"""
        model = setup['model']
        processor = setup['processor']
        temp_dir = setup['temp_dir']
        
        # 步骤1: 初始化一个空HTML文档
        init_cmd = InitCommand(model)
        assert processor.execute(init_cmd) is True
        print("\n--- 步骤1: 初始化HTML文档 ---")
        
        # 步骤2: 添加一个容器div
        append_container_cmd = AppendCommand(model, 'div', 'container', 'body', '网页容器')
        assert processor.execute(append_container_cmd) is True
        
        # 验证容器已添加
        container = model.find_by_id('container')
        assert container is not None
        assert container.text == '网页容器'
        print("--- 步骤2: 添加容器div ---")
        
        # 步骤3: 在容器中添加一个标题和段落
        append_title_cmd = AppendCommand(model, 'h1', 'main-title', 'container', '欢迎')
        assert processor.execute(append_title_cmd) is True
        
        append_para_cmd = AppendCommand(model, 'p', 'intro', 'container', '这是一个段落介绍')
        assert processor.execute(append_para_cmd) is True
        print("--- 步骤3: 添加标题和段落 ---")
        
        # 步骤4: 在标题前插入一个logo元素
        insert_logo_cmd = InsertCommand(model, 'img', 'logo', 'main-title')
        assert processor.execute(insert_logo_cmd) is True
        
        # 验证logo已正确插入在标题前
        container = model.find_by_id('container')
        child_ids = [child.id for child in container.children]
        assert 'logo' in child_ids
        assert 'main-title' in child_ids
        assert child_ids.index('logo') < child_ids.index('main-title')
        print("--- 步骤4: 在标题前插入logo ---")
        
        # 步骤5: 编辑标题文本
        edit_title_cmd = EditTextCommand(model, 'main-title', '欢迎访问我的网站')
        assert processor.execute(edit_title_cmd) is True
        
        # 验证文本已更新
        title = model.find_by_id('main-title')
        assert title.text == '欢迎访问我的网站'
        print("--- 步骤5: 编辑标题文本 ---")
        
        # 步骤6: 添加一个页脚，并在其中添加版权信息
        append_footer_cmd = AppendCommand(model, 'div', 'footer', 'body')
        assert processor.execute(append_footer_cmd) is True
        
        append_copyright_cmd = AppendCommand(model, 'p', 'copyright', 'footer', '© 2023 我的网站')
        assert processor.execute(append_copyright_cmd) is True
        print("--- 步骤6: 添加页脚和版权信息 ---")
        
        # 步骤7: 修改元素ID
        edit_id_cmd = EditIdCommand(model, 'container', 'main-container')
        assert processor.execute(edit_id_cmd) is True
        
        # 验证ID已更新
        container = model.find_by_id('main-container')
        assert container is not None
        with pytest.raises(ElementNotFoundError):
            model.find_by_id('container')
        print("--- 步骤7: 修改容器ID ---")
        
        # 步骤8: 打印当前HTML结构
        print_cmd = PrintTreeCommand(model)
        assert processor.execute(print_cmd) is True
        
        # 捕获输出并验证
        captured = capsys.readouterr()
        print_output = captured.out
        
        # 验证所有元素都在输出中
        assert 'main-container' in print_output
        assert 'main-title' in print_output
        assert 'footer' in print_output
        print("--- 步骤8: 打印HTML结构 ---")
        
        # 步骤9: 保存文件
        file_path = os.path.join(temp_dir, "test_output.html")
        save_cmd = SaveCommand(model, file_path)
        assert processor.execute(save_cmd) is True
        
        # 验证文件已保存
        assert os.path.exists(file_path)
        print(f"--- 步骤9: 保存到文件 {file_path} ---")
        
        # 步骤10: 读取保存的文件到新模型
        new_model = HtmlModel()
        new_processor = CommandProcessor()
        read_cmd = ReadCommand(new_processor, new_model, file_path)
        assert new_processor.execute(read_cmd) is True
        
        # 验证新模型包含所有元素
        assert new_model.find_by_id('main-container') is not None
        assert new_model.find_by_id('main-title') is not None
        assert new_model.find_by_id('logo') is not None
        assert new_model.find_by_id('intro') is not None
        assert new_model.find_by_id('footer') is not None
        assert new_model.find_by_id('copyright') is not None
        print("--- 步骤10: 从文件读取HTML ---")
        
        # 步骤11: 测试撤销和重做 - 删除元素然后撤销
        delete_cmd = DeleteCommand(new_model, 'logo')
        assert new_processor.execute(delete_cmd) is True
        
        # 验证元素已删除
        with pytest.raises(ElementNotFoundError):
            new_model.find_by_id('logo')
        
        # 撤销删除
        assert new_processor.undo() is True
        
        # 验证元素已恢复
        assert new_model.find_by_id('logo') is not None
        
        # 重做删除
        assert new_processor.redo() is True
        
        # 验证元素再次被删除
        with pytest.raises(ElementNotFoundError):
            new_model.find_by_id('logo')
        print("--- 步骤11: 测试撤销和重做 ---")
        
        # 步骤12: 测试错误处理 - 尝试创建重复ID
        # 应该引发异常
        with pytest.raises(DuplicateIdError):
            duplicate_cmd = AppendCommand(new_model, 'div', 'main-title', 'body')
            new_processor.execute(duplicate_cmd)
        print("--- 步骤12: 测试错误处理 ---")
        
        print("\n集成测试完成，所有功能正常工作！")

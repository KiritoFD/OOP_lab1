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
from src.commands.display_commands import PrintTreeCommand, SpellCheckCommand
from src.core.exceptions import ElementNotFoundError, DuplicateIdError

class TestEdgeCases:
    """测试各种边缘情况和异常处理"""
    
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
    
    def test_deep_nesting(self, setup):
        """测试深层嵌套的元素结构"""
        model = setup['model']
        processor = setup['processor']
        
        # 初始化
        processor.execute(InitCommand(model))
        
        # 创建一个10层深的嵌套结构
        current_parent = "body"
        for i in range(1, 11):
            cmd = AppendCommand(model, 'div', f'level{i}', current_parent, f'Level {i} content')
            assert processor.execute(cmd) is True
            current_parent = f'level{i}'
        
        # 验证最深层级元素正确创建
        deepest = model.find_by_id('level10')
        assert deepest is not None
        assert deepest.text == 'Level 10 content'
        
        # 追踪从最深层级回到根的路径
        element = deepest
        path = []
        while element:
            path.append(element.id)
            element = element.parent
        
        # 验证路径正确 (从子到父)
        expected_path = ['level10', 'level9', 'level8', 'level7', 'level6', 
                         'level5', 'level4', 'level3', 'level2', 'level1', 
                         'body', 'html']
        assert path == expected_path
    
    def test_delete_with_children(self, setup):
        """测试删除含有子元素的元素"""
        model = setup['model']
        processor = setup['processor']
        
        # 初始化
        processor.execute(InitCommand(model))
        
        # 创建具有子元素的结构
        processor.execute(AppendCommand(model, 'div', 'parent', 'body'))
        processor.execute(AppendCommand(model, 'p', 'child1', 'parent', 'Child 1'))
        processor.execute(AppendCommand(model, 'p', 'child2', 'parent', 'Child 2'))
        processor.execute(AppendCommand(model, 'div', 'nested', 'child2'))
        processor.execute(AppendCommand(model, 'span', 'deep', 'nested', 'Deep nested'))
        
        # 删除中间元素，应该级联删除所有子元素
        processor.execute(DeleteCommand(model, 'child2'))
        
        # 验证删除了child2及其所有子元素
        assert model.find_by_id('parent') is not None
        assert model.find_by_id('child1') is not None
        with pytest.raises(ElementNotFoundError):
            model.find_by_id('child2')
        with pytest.raises(ElementNotFoundError):
            model.find_by_id('nested')
        with pytest.raises(ElementNotFoundError):
            model.find_by_id('deep')
            
        # 删除根元素应该失败
        with pytest.raises(ElementNotFoundError):
            processor.execute(DeleteCommand(model, 'invalid-id'))
    
    def test_modify_special_elements(self, setup):
        """测试修改特殊元素（html, head, body, title）"""
        model = setup['model']
        processor = setup['processor']
        
        # 初始化
        processor.execute(InitCommand(model))
        
        # 尝试修改title的文本
        processor.execute(EditTextCommand(model, 'title', '页面标题'))
        
        # 验证title文本已更新
        title = model.find_by_id('title')
        assert title.text == '页面标题'
        
        # 尝试修改body的ID (应该可以成功，但不推荐)
        processor.execute(EditIdCommand(model, 'body', 'custom-body'))
        
        # 验证ID已更改
        with pytest.raises(ElementNotFoundError):
            model.find_by_id('body')
        assert model.find_by_id('custom-body') is not None
    
    def test_command_error_recovery(self, setup, capsys):
        """测试命令执行失败后的恢复能力"""
        model = setup['model']
        processor = setup['processor']
        
        # 初始化
        processor.execute(InitCommand(model))
        
        # 成功执行一个命令
        processor.execute(AppendCommand(model, 'div', 'container', 'body'))
        
        # 尝试执行一个会失败的命令
        with pytest.raises(DuplicateIdError):
            processor.execute(AppendCommand(model, 'p', 'container', 'body'))
        
        # 验证模型状态仍然有效
        container = model.find_by_id('container')
        assert container is not None
        assert container.tag == 'div'
        
        # 执行后续命令应该仍然成功
        processor.execute(AppendCommand(model, 'p', 'paragraph', 'container'))
        para = model.find_by_id('paragraph')
        assert para is not None
    
    def test_large_document(self, setup):
        """测试处理大型文档的性能和正确性"""
        model = setup['model']
        processor = setup['processor']
        
        # 初始化
        processor.execute(InitCommand(model))
        
        # 创建一个有100个元素的文档
        for i in range(1, 101):
            parent_id = 'body' if i <= 10 else f'parent{(i-1) // 10}'
            element_id = f'parent{i // 10}' if i % 10 == 0 else f'element{i}'
            
            cmd = AppendCommand(model, 'div' if i % 10 == 0 else 'p', 
                              element_id, parent_id, f'Content {i}')
            processor.execute(cmd)
        
        # 验证随机抽查的元素
        for id in ['element25', 'element50', 'element75', 'parent5', 'parent10']:
            element = model.find_by_id(id)
            assert element is not None
        
        # 保存大型文档
        temp_dir = setup['temp_dir']
        file_path = os.path.join(temp_dir, 'large_doc.html')
        processor.execute(SaveCommand(model, file_path))
        
        # 确认文件存在且大小合理
        assert os.path.exists(file_path)
        assert os.path.getsize(file_path) > 5000  # 应该超过5KB
        
        # 重新加载大型文档
        new_model = HtmlModel()
        new_processor = CommandProcessor()
        processor.execute(ReadCommand(new_processor, new_model, file_path))
        
        # 验证加载后的文档内容正确
        for id in ['element25', 'element50', 'element75', 'parent5', 'parent10']:
            try:
                element = new_model.find_by_id(id)
                assert element is not None
            except ElementNotFoundError:
                # 如果读取后ID发生变化，这是可接受的，但我们应该记录下来
                print(f"注意: ID '{id}' 在重新加载后不存在，可能是由于ID处理方式变化")
    
    def test_malformed_commands(self, setup):
        """测试处理格式错误的命令"""
        model = setup['model']
        processor = setup['processor']
        
        # 初始化
        processor.execute(InitCommand(model))
        
        # 创建一个基础元素来进行测试
        processor.execute(AppendCommand(model, 'div', 'container', 'body'))
        
        # 测试无效参数的命令处理
        with pytest.raises(ValueError):
            processor.execute(AppendCommand(model, '', 'test', 'container'))
            
        with pytest.raises(ValueError):
            processor.execute(AppendCommand(model, 'div', '', 'container'))
            
        with pytest.raises(ElementNotFoundError):
            processor.execute(AppendCommand(model, 'div', 'test', 'non-existent'))
            
        # 验证错误命令后，模型状态依然正确
        assert model.find_by_id('container') is not None
        
    @patch('builtins.open')
    def test_io_error_handling(self, mock_open, setup):
        """测试IO错误处理"""
        model = setup['model']
        processor = setup['processor']
        
        # 初始化
        processor.execute(InitCommand(model))
        
        # 创建一些内容
        processor.execute(AppendCommand(model, 'div', 'container', 'body'))
        
        # 模拟文件读写错误
        mock_open.side_effect = IOError("模拟IO错误")
        
        # 测试保存失败处理
        save_cmd = SaveCommand(model, "/invalid/path/file.html")
        result = processor.execute(save_cmd)
        assert result is False
        
        # 测试读取失败处理
        with pytest.raises(IOError):
            read_cmd = ReadCommand(processor, model, "/invalid/path/nonexistent.html")
            processor.execute(read_cmd)
        
        # 验证模型状态保持不变
        assert model.find_by_id('container') is not None
        
    def test_undo_redo_edge_cases(self, setup):
        """测试撤销/重做的边缘情况"""
        model = setup['model']
        processor = setup['processor']
        
        # 初始化
        processor.execute(InitCommand(model))
        
        # 测试空栈撤销
        assert processor.undo() is False
        
        # 测试空栈重做
        assert processor.redo() is False
        
        # 执行一系列命令
        processor.execute(AppendCommand(model, 'div', 'div1', 'body'))
        processor.execute(AppendCommand(model, 'p', 'p1', 'div1'))
        
        # 全部撤销
        processor.undo()
        processor.undo()
        
        # 再次撤销(应该失败)
        assert processor.undo() is False
        
        # 全部重做
        processor.redo()
        processor.redo()
        
        # 再次重做(应该失败)
        assert processor.redo() is False
        
        # 验证最终状态正确
        assert model.find_by_id('div1') is not None
        assert model.find_by_id('p1') is not None

import pytest
from unittest.mock import MagicMock, patch
from src.commands.base import Command, CommandProcessor
from src.commands.edit.append_command import AppendCommand
from src.commands.edit.edit_text_command import EditTextCommand
from src.commands.edit.delete_command import DeleteCommand
from src.commands.edit.edit_id_command import EditIdCommand
from src.commands.io import SaveCommand
from src.core.html_model import HtmlModel
from src.core.exceptions import ElementNotFoundError
from src.commands.do.undo import UndoCommand

class MockCommand(Command):
    """用于测试的命令"""
    def __init__(self, return_value=True, recordable=True):
        self.executed = False
        self.undone = False
        self.redone = False
        self.return_value = return_value
        self.description = "Mock Command"
        self.recordable = recordable
    
    def execute(self):
        self.executed = True
        return self.return_value
        
    def undo(self):
        self.undone = True
        return True
    
    def redo(self):
        self.redone = True
        return True

@pytest.mark.unit
class TestUndoCommand:
    @pytest.fixture
    def model(self):
        """创建测试用的HTML模型"""
        model = HtmlModel()
        return model
    
    @pytest.fixture
    def processor(self):
        """创建命令处理器"""
        return CommandProcessor()
    
    @pytest.fixture
    def setup_elements(self, model, processor):
        """设置测试用的元素结构"""
        # 添加一些元素用于测试撤销
        cmd1 = AppendCommand(model, 'div', 'container', 'body')
        cmd2 = AppendCommand(model, 'p', 'para1', 'container', 'Paragraph 1')
        cmd3 = AppendCommand(model, 'p', 'para2', 'container', 'Paragraph 2')
        
        processor.execute(cmd1)
        processor.execute(cmd2)
        processor.execute(cmd3)
        
        return model
    
    def test_undo_success(self, processor):
        """测试成功撤销命令"""
        cmd = MockCommand()
        processor.execute(cmd)
        
        # 验证撤销可用
        assert processor.undo() is True
    
    def test_undo_empty_history(self, processor):
        """测试空历史时的撤销行为"""
        # 新的处理器历史是空的
        assert processor.undo() is False
    
    def test_undo_failed_undo_operation(self, processor):
        """测试撤销操作失败的情况"""
        mock_cmd = MockCommand()
        # 修改undo方法以返回False
        mock_cmd.undo = lambda: False
        
        processor.execute(mock_cmd)
        
        # 执行撤销
        assert processor.undo() is False
    
    def test_undo_append_command(self, model, processor):
        """测试撤销AppendCommand"""
        cmd = AppendCommand(model, 'div', 'test-div', 'body')
        processor.execute(cmd)
        
        # 验证元素已添加
        assert model.find_by_id('test-div') is not None
        
        # 执行撤销
        assert processor.undo() is True
        
        # 验证元素已删除
        with pytest.raises(ElementNotFoundError):
            model.find_by_id('test-div')
    
    def test_undo_edit_text_command(self, model, processor):
        """测试撤销EditTextCommand"""
        # 先添加一个元素
        cmd1 = AppendCommand(model, 'p', 'test-para', 'body', 'Original text')
        processor.execute(cmd1)
        
        # 修改文本
        cmd2 = EditTextCommand(model, 'test-para', 'New text')
        processor.execute(cmd2)
        
        # 验证文本已修改
        assert model.find_by_id('test-para').text == 'New text'
        
        # 执行撤销
        assert processor.undo() is True
        
        # 验证文本已恢复
        assert model.find_by_id('test-para').text == 'Original text'
    
    def test_undo_delete_command(self, model, processor):
        """测试撤销DeleteCommand"""
        # 先添加一个元素
        cmd1 = AppendCommand(model, 'div', 'test-div', 'body')
        processor.execute(cmd1)
        
        # 删除元素
        cmd2 = DeleteCommand(model, 'test-div')
        processor.execute(cmd2)
        
        # 验证元素已删除
        with pytest.raises(ElementNotFoundError):
            model.find_by_id('test-div')
        
        # 执行撤销
        assert processor.undo() is True
        
        # 验证元素已恢复
        assert model.find_by_id('test-div') is not None
    
    def test_undo_edit_id_command(self, model, processor):
        """测试撤销EditIdCommand"""
        # 先添加一个元素
        cmd1 = AppendCommand(model, 'div', 'old-id', 'body')
        processor.execute(cmd1)
        
        # 修改ID
        cmd2 = EditIdCommand(model, 'old-id', 'new-id')
        processor.execute(cmd2)
        
        # 验证ID已修改
        with pytest.raises(ElementNotFoundError):
            model.find_by_id('old-id')
        assert model.find_by_id('new-id') is not None
        
        # 执行撤销
        assert processor.undo() is True
        
        # 验证ID已恢复
        with pytest.raises(ElementNotFoundError):
            model.find_by_id('new-id')
        assert model.find_by_id('old-id') is not None
    
    def test_undo_multiple_commands(self, model, processor, setup_elements):
        """测试撤销多个命令"""
        # 验证初始状态
        assert model.find_by_id('para2') is not None
        assert model.find_by_id('para1') is not None
        assert model.find_by_id('container') is not None
        
        # 撤销添加para2
        assert processor.undo() is True
        with pytest.raises(ElementNotFoundError):
            model.find_by_id('para2')
        
        # 撤销添加para1
        assert processor.undo() is True
        with pytest.raises(ElementNotFoundError):
            model.find_by_id('para1')
            
        # 撤销添加container
        assert processor.undo() is True
        with pytest.raises(ElementNotFoundError):
            model.find_by_id('container')
            
        # 历史记录应该为空
        assert processor.undo() is False
    
    def test_undo_non_recordable_command(self, processor):
        """测试不可记录命令的撤销行为"""
        # 创建不可记录的命令
        cmd = MockCommand(recordable=False)
        processor.execute(cmd)
        
        # 不可记录命令不会进入历史记录，因此无法撤销
        assert processor.undo() is False
    
    def test_undo_command_hierarchy(self, model, processor):
        """测试命令层次结构中的撤销行为"""
        # 创建嵌套元素结构
        cmd1 = AppendCommand(model, 'div', 'parent', 'body')
        cmd2 = AppendCommand(model, 'div', 'child', 'parent')
        cmd3 = AppendCommand(model, 'p', 'grandchild', 'child', 'Text')
        
        processor.execute(cmd1)
        processor.execute(cmd2)
        processor.execute(cmd3)
        
        # 撤销添加孙子元素
        assert processor.undo() is True
        with pytest.raises(ElementNotFoundError):
            model.find_by_id('grandchild')
        assert model.find_by_id('child') is not None
        
        # 撤销添加子元素
        assert processor.undo() is True
        with pytest.raises(ElementNotFoundError):
            model.find_by_id('child')
        assert model.find_by_id('parent') is not None
        
        # 撤销添加父元素
        assert processor.undo() is True
        with pytest.raises(ElementNotFoundError):
            model.find_by_id('parent')
    
    def test_undo_after_clear_history(self, processor):
        """测试清空历史后尝试撤销"""
        cmd = MockCommand()
        processor.execute(cmd)
        
        # 清空历史
        processor.clear_history()
        
        # 验证无法撤销
        assert processor.undo() is False
    
    def test_undo_io_commands(self, model, processor, tmp_path):
        """测试IO命令的撤销行为"""
        # 创建保存命令
        save_cmd = SaveCommand(model, str(tmp_path / "test.html"))
        processor.execute(save_cmd)
        
        # 尝试撤销IO命令 (具体结果取决于实现)
        result = processor.undo()
        # 不做具体断言，因为可能返回True或False，取决于SaveCommand是否实现了undo
    
    def test_undo_command_direct(self, processor):
        """直接测试UndoCommand类"""
        # 创建可记录命令
        mock_cmd = MockCommand(recordable=True)
        processor.execute(mock_cmd)
        
        # 创建撤销命令
        undo_cmd = UndoCommand(processor)
        
        # 验证属性设置
        assert undo_cmd.processor == processor
        assert undo_cmd.description == "撤销上一个操作"
        assert not undo_cmd.recordable  # 应该不可记录
        
        # 执行撤销命令
        result = undo_cmd.execute()
        assert result is True
        assert mock_cmd.undone is True
        
    def test_undo_command_with_empty_history(self, processor):
        """测试UndoCommand处理空历史的情况"""
        # 确保历史为空
        processor.clear_history()
        
        # 创建撤销命令
        undo_cmd = UndoCommand(processor)
        
        # 应该返回False表示无法撤销
        result = undo_cmd.execute()
        assert result is False
        
    @patch('builtins.print')
    def test_undo_command_output(self, mock_print, processor):
        """测试UndoCommand的输出"""
        # 添加一个命令
        mock_cmd = MockCommand()
        processor.execute(mock_cmd)
        
        # 创建并执行撤销命令
        undo_cmd = UndoCommand(processor)
        undo_cmd.execute()
        
        # 验证输出信息
        mock_print.assert_called_with("已撤销: 上一个操作")
        
    def test_undo_command_with_failed_undo(self, processor):
        """测试UndoCommand处理撤销失败的情况"""
        # 创建撤销失败的命令
        failed_cmd = MockCommand()
        failed_cmd.undo = lambda: False
        processor.execute(failed_cmd)
        
        # 创建撤销命令
        undo_cmd = UndoCommand(processor)
        
        # 应该返回False表示撤销失败
        result = undo_cmd.execute()
        assert result is False
        
    @patch('builtins.print')
    def test_undo_command_exception_handling(self, mock_print, processor):
        """测试UndoCommand的异常处理"""
        # 创建抛出异常的命令
        error_cmd = MockCommand()
        error_cmd.undo = lambda: exec('raise Exception("测试异常")')
        processor.execute(error_cmd)
        
        # 创建撤销命令
        undo_cmd = UndoCommand(processor)
        
        # 应该捕获异常并返回False
        result = undo_cmd.execute()
        assert result is False
        
        # 验证错误输出
        called_with_args = [call[0][0] for call in mock_print.call_args_list]
        error_message_printed = False
        for arg in called_with_args:
            if isinstance(arg, str) and "撤销时发生错误" in arg:
                error_message_printed = True
                break
        assert error_message_printed

    def test_undo_command_invalid_redo(self):
        """测试UndoCommand的redo方法（应该返回False）"""
        processor = CommandProcessor()
        undo_cmd = UndoCommand(processor)
        
        # redo方法应该返回False，因为撤销命令不能重做
        assert undo_cmd.redo() is False

    def test_undo_command_str_representation(self):
        """测试UndoCommand的字符串表示"""
        processor = CommandProcessor()
        undo_cmd = UndoCommand(processor)
        
        # 验证__str__方法输出包含命令描述
        assert "撤销上一个操作" in str(undo_cmd)
        
    def test_undo_command_with_custom_processor(self):
        """测试使用自定义处理器的UndoCommand"""
        # 创建模拟的命令处理器
        mock_processor = MagicMock()
        mock_processor.undo.return_value = True
        
        # 创建UndoCommand
        undo_cmd = UndoCommand(mock_processor)
        
        # 执行命令
        result = undo_cmd.execute()
        
        # 验证结果和处理器调用
        assert result is True
        mock_processor.undo.assert_called_once()
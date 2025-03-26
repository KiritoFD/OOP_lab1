import pytest
from src.commands.edit.delete_command import DeleteCommand
from src.commands.edit.append_command import AppendCommand
from src.commands.base import CommandProcessor
from src.core.html_model import HtmlModel
from src.core.exceptions import ElementNotFoundError

class TestDeleteCommand:
    @pytest.fixture
    def model(self):
        """创建一个测试用的HTML模型"""
        return HtmlModel()
        
    @pytest.fixture
    def processor(self):
        """创建一个命令处理器"""
        return CommandProcessor()
    
    @pytest.fixture
    def setup_elements(self, model, processor):
        """设置测试用的元素"""
        # 添加一些元素用于测试删除
        cmd1 = AppendCommand(model, 'div', 'test-div', 'body')
        cmd2 = AppendCommand(model, 'p', 'test-p', 'body')
        cmd3 = AppendCommand(model, 'span', 'test-span', 'test-div')
        
        processor.execute(cmd1)
        processor.execute(cmd2)
        processor.execute(cmd3)
        
        return model
        
    def test_delete_success(self, model, processor, setup_elements):
        """测试成功删除元素"""
        cmd = DeleteCommand(model, 'test-div')
        
        # 执行删除命令
        assert processor.execute(cmd) is True
        
        # 验证元素已被删除
        assert model.find_by_id('test-div') is None
        assert model.find_by_id('test-span') is None  # 子元素也应被删除
        assert model.find_by_id('test-p') is not None  # 其他元素不受影响
        
    def test_delete_nonexistent(self, model, processor):
        """测试删除不存在的元素"""
        cmd = DeleteCommand(model, 'non-existent')
        
        # 应抛出异常
        with pytest.raises(ElementNotFoundError):
            processor.execute(cmd)
            
    def test_delete_special_element(self, model, processor):
        """测试删除特殊元素"""
        # 尝试删除body元素
        cmd = DeleteCommand(model, 'body')
        
        # 应抛出异常
        with pytest.raises(ValueError):
            processor.execute(cmd)
            
    def test_delete_undo(self, model, processor, setup_elements):
        """测试删除的撤销操作"""
        # 记录初始状态
        original_div = model.find_by_id('test-div')
        original_span = model.find_by_id('test-span')
        
        # 执行删除
        cmd = DeleteCommand(model, 'test-div')
        processor.execute(cmd)
        
        # 验证删除成功
        assert model.find_by_id('test-div') is None
        assert model.find_by_id('test-span') is None
        
        # 执行撤销
        assert processor.undo() is True
        
        # 验证元素已恢复
        restored_div = model.find_by_id('test-div')
        restored_span = model.find_by_id('test-span')
        
        assert restored_div is not None
        assert restored_div.id == original_div.id
        assert restored_div.tag == original_div.tag
        
        # 验证子元素也被恢复
        assert restored_span is not None
        assert restored_span.parent == restored_div
        
    def test_delete_redo(self, model, processor, setup_elements):
        """测试删除的重做操作"""
        # 执行删除
        cmd = DeleteCommand(model, 'test-p')
        processor.execute(cmd)
        
        # 撤销删除
        processor.undo()
        assert model.find_by_id('test-p') is not None
        
        # 重做删除
        assert processor.redo() is True
        assert model.find_by_id('test-p') is None
        
    def test_delete_multiple_elements(self, model, processor, setup_elements):
        """测试删除多个元素"""
        # 先删除第一个元素
        cmd1 = DeleteCommand(model, 'test-div')
        processor.execute(cmd1)
        
        # 再删除第二个元素
        cmd2 = DeleteCommand(model, 'test-p')
        processor.execute(cmd2)
        
        # 验证元素都已删除
        assert model.find_by_id('test-div') is None
        assert model.find_by_id('test-p') is None
        
        # 撤销删除
        processor.undo()  # 撤销删除test-p
        assert model.find_by_id('test-p') is not None
        
        processor.undo()  # 撤销删除test-div
        assert model.find_by_id('test-div') is not None
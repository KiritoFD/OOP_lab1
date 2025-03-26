import pytest
from src.core.html_model import HtmlModel
from src.commands.edit_commands import EditIdCommand, AppendCommand
from src.commands.base import CommandProcessor
from src.core.exceptions import DuplicateIdError, ElementNotFoundError

class TestEditIdCommand:
    @pytest.fixture
    def model(self):
        return HtmlModel()
    
    @pytest.fixture
    def processor(self):
        return CommandProcessor()
    
    @pytest.fixture
    def setup_element(self, model, processor):
        """创建测试用的元素"""
        cmd = AppendCommand(model, 'div', 'old-id', 'body')
        processor.execute(cmd)
        processor.clear_history()
        
    def test_edit_id_success(self, model, processor, setup_element):
        """测试成功编辑ID"""
        cmd = EditIdCommand(model, 'old-id', 'new-id')
        
        # 执行命令
        assert processor.execute(cmd) is True
        
        # 验证ID更新
        assert model.find_by_id('old-id') is None
        element = model.find_by_id('new-id')
        assert element is not None
        assert element.id == 'new-id'
        
    def test_edit_id_duplicate(self, model, processor, setup_element):
        """测试编辑为重复的ID"""
        # 创建另一个元素
        cmd1 = AppendCommand(model, 'p', 'existing-id', 'body')
        processor.execute(cmd1)
        processor.clear_history()
        
        # 尝试将第一个元素的ID改为已存在的ID
        cmd2 = EditIdCommand(model, 'old-id', 'existing-id')
        with pytest.raises(DuplicateIdError):
            processor.execute(cmd2)
            
    def test_edit_nonexistent_element(self, model, processor):
        """测试编辑不存在的元素的ID"""
        cmd = EditIdCommand(model, 'nonexistent', 'new-id')
        with pytest.raises(ElementNotFoundError):
            processor.execute(cmd)
            
    def test_edit_id_undo(self, model, processor, setup_element):
        """测试编辑ID的撤销"""
        cmd = EditIdCommand(model, 'old-id', 'new-id')
        processor.execute(cmd)
        
        # 执行撤销
        assert processor.undo() is True
        
        # 验证ID恢复
        assert model.find_by_id('new-id') is None
        element = model.find_by_id('old-id')
        assert element is not None
        assert element.id == 'old-id'
        
    def test_edit_id_redo(self, model, processor, setup_element):
        """测试编辑ID的重做"""
        cmd = EditIdCommand(model, 'old-id', 'new-id')
        
        # 执行-撤销-重做
        processor.execute(cmd)
        processor.undo()
        assert processor.redo() is True
        
        # 验证ID再次更新
        assert model.find_by_id('old-id') is None
        element = model.find_by_id('new-id')
        assert element is not None
        assert element.id == 'new-id'
        
    def test_edit_id_sequence(self, model, processor, setup_element):
        """测试多次编辑ID"""
        cmd1 = EditIdCommand(model, 'old-id', 'mid-id')
        cmd2 = EditIdCommand(model, 'mid-id', 'final-id')
        
        # 执行第一次编辑
        processor.execute(cmd1)
        assert model.find_by_id('old-id') is None
        assert model.find_by_id('mid-id') is not None
        
        # 执行第二次编辑
        processor.execute(cmd2)
        assert model.find_by_id('mid-id') is None
        assert model.find_by_id('final-id') is not None
        
        # 撤销到初始状态
        processor.undo()
        assert model.find_by_id('mid-id') is not None
        assert model.find_by_id('final-id') is None
        
        processor.undo()
        assert model.find_by_id('old-id') is not None
        assert model.find_by_id('mid-id') is None
        
    def test_edit_id_reference_integrity(self, model, processor):
        """测试编辑ID后引用完整性"""
        # 创建父子结构
        cmd1 = AppendCommand(model, 'div', 'parent', 'body')
        cmd2 = AppendCommand(model, 'p', 'child', 'parent')
        processor.execute(cmd1)
        processor.execute(cmd2)
        processor.clear_history()
        
        # 编辑父元素ID
        cmd3 = EditIdCommand(model, 'parent', 'new-parent')
        processor.execute(cmd3)
        
        # 验证子元素的父引用正确更新
        child = model.find_by_id('child')
        parent = model.find_by_id('new-parent')
        assert child.parent == parent
        assert child in parent.children
        
        # 撤销编辑
        processor.undo()
        
        # 验证引用恢复正确
        child = model.find_by_id('child')
        old_parent = model.find_by_id('parent')
        assert child.parent == old_parent
        assert child in old_parent.children
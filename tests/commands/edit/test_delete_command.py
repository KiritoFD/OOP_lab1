import pytest
from src.core.html_model import HtmlModel
from src.commands.edit_commands import DeleteCommand, AppendCommand
from src.commands.base import CommandProcessor
from src.core.exceptions import ElementNotFoundError, InvalidOperationError

class TestDeleteCommand:
    @pytest.fixture
    def model(self):
        return HtmlModel()
    
    @pytest.fixture
    def processor(self):
        return CommandProcessor()
    
    @pytest.fixture
    def setup_elements(self, model, processor):
        """创建测试用的元素结构"""
        # 创建一个父元素和子元素
        cmd1 = AppendCommand(model, 'div', 'parent', 'body')
        cmd2 = AppendCommand(model, 'p', 'child1', 'parent')
        cmd3 = AppendCommand(model, 'p', 'child2', 'parent')
        processor.execute(cmd1)
        processor.execute(cmd2)
        processor.execute(cmd3)
        processor.clear_history()  # 清空历史，确保不影响测试
        
    def test_delete_success(self, model, processor, setup_elements):
        """测试成功删除元素"""
        cmd = DeleteCommand(model, 'child1')
        
        # 执行删除
        assert processor.execute(cmd) is True
        
        # 验证删除结果
        assert model.find_by_id('child1') is None
        assert 'child1' not in [child.id for child in model.find_by_id('parent').children]
        
    def test_delete_with_children(self, model, processor, setup_elements):
        """测试删除带有子元素的元素"""
        cmd = DeleteCommand(model, 'parent')
        
        # 执行删除
        assert processor.execute(cmd) is True
        
        # 验证父元素和所有子元素都被删除
        assert model.find_by_id('parent') is None
        assert model.find_by_id('child1') is None
        assert model.find_by_id('child2') is None
        
    def test_delete_nonexistent(self, model, processor):
        """测试删除不存在的元素"""
        cmd = DeleteCommand(model, 'nonexistent')
        with pytest.raises(ElementNotFoundError):
            processor.execute(cmd)
            
    def test_delete_protected(self, model, processor):
        """测试删除受保护的元素"""
        protected_ids = ['html', 'head', 'title', 'body']
        for id in protected_ids:
            cmd = DeleteCommand(model, id)
            with pytest.raises(InvalidOperationError):
                processor.execute(cmd)
                
    def test_delete_undo(self, model, processor, setup_elements):
        """测试删除命令的撤销"""
        # 保存初始状态下的父元素子节点数量
        parent = model.find_by_id('parent')
        initial_children_count = len(parent.children)
        
        # 执行删除
        cmd = DeleteCommand(model, 'child1')
        processor.execute(cmd)
        
        # 执行撤销
        assert processor.undo() is True
        
        # 验证元素被恢复
        restored = model.find_by_id('child1')
        assert restored is not None
        assert restored.tag == 'p'
        assert restored.parent == parent
        assert len(parent.children) == initial_children_count
        
    def test_delete_redo(self, model, processor, setup_elements):
        """测试删除命令的重做"""
        cmd = DeleteCommand(model, 'child1')
        processor.execute(cmd)
        processor.undo()
        
        # 执行重做
        assert processor.redo() is True
        
        # 验证元素再次被删除
        assert model.find_by_id('child1') is None
        assert 'child1' not in [child.id for child in model.find_by_id('parent').children]
        
    def test_delete_sequence(self, model, processor, setup_elements):
        """测试多个删除命令的序列"""
        cmd1 = DeleteCommand(model, 'child1')
        cmd2 = DeleteCommand(model, 'child2')
        
        # 执行命令序列
        processor.execute(cmd1)
        processor.execute(cmd2)
        
        # 验证两个元素都被删除
        assert model.find_by_id('child1') is None
        assert model.find_by_id('child2') is None
        
        # 依次撤销删除
        processor.undo()  # 恢复child2
        assert model.find_by_id('child2') is not None
        assert model.find_by_id('child1') is None
        
        processor.undo()  # 恢复child1
        assert model.find_by_id('child1') is not None
        assert model.find_by_id('child2') is not None
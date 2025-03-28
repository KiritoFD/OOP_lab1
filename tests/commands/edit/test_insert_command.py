import pytest
from src.commands.edit.insert_command import InsertCommand
from src.commands.edit.append_command import AppendCommand
from src.commands.io_commands import InitCommand
from src.commands.base import CommandProcessor
from src.core.html_model import HtmlModel
from src.core.exceptions import ElementNotFoundError, DuplicateIdError
from src.commands.command_exceptions import CommandExecutionError

class TestInsertCommand:
    @pytest.fixture
    def model(self):
        """创建一个测试用的HTML模型"""
        model = HtmlModel()
        return model
        
    @pytest.fixture
    def initialized_model(self, model, processor):
        """创建一个已初始化的模型"""
        processor.execute(InitCommand(model))
        return model
        
    @pytest.fixture
    def processor(self):
        """创建一个命令处理器"""
        return CommandProcessor()
    
    @pytest.fixture
    def setup_elements(self, initialized_model, processor):
        """设置测试用的元素结构"""
        model = initialized_model
        
        # 添加一些元素用于测试插入
        cmd1 = AppendCommand(model, 'div', 'container', 'body')
        cmd2 = AppendCommand(model, 'p', 'first', 'container', 'First paragraph')
        cmd3 = AppendCommand(model, 'p', 'last', 'container', 'Last paragraph')
        
        processor.execute(cmd1)
        processor.execute(cmd2)
        processor.execute(cmd3)
        
        return model
        
    def test_insert_success(self, setup_elements, processor):
        """测试成功插入元素"""
        model = setup_elements
        
        # 应该在last元素之前插入，而不是body
        cmd = InsertCommand(model, 'h2', 'middle', 'last')
        
        # 执行插入命令
        assert processor.execute(cmd) is True
        
        # 验证元素已插入
        middle = model.find_by_id('middle')
        assert middle is not None
        assert middle.tag == 'h2'
        
        # 验证元素顺序：first -> middle -> last
        container = model.find_by_id('container')
        assert container.children[0].id == 'first'
        assert container.children[1].id == 'middle'
        assert container.children[2].id == 'last'
    
    def test_multiple_undo_redo(self, setup_elements, processor):
        """测试多次撤销和重做"""
        model = setup_elements
        
        # 修改这里，不使用body作为目标位置
        cmd1 = InsertCommand(model, 'div', 'div1', 'first')
        cmd2 = InsertCommand(model, 'p', 'p1', 'last')
        cmd3 = InsertCommand(model, 'span', 'span1', 'first')
        
        # 执行所有命令
        processor.execute(cmd1)
        processor.execute(cmd2)
        processor.execute(cmd3)
        
        # 验证元素顺序
        container = model.find_by_id('container')
        child_ids = [child.id for child in container.children]
        assert 'div1' in child_ids
        assert 'p1' in child_ids
        assert 'span1' in child_ids
        
        # 撤销操作
        processor.undo()  # 撤销cmd3
        assert model.find_by_id('span1') is None
        
        processor.undo()  # 撤销cmd2
        assert model.find_by_id('p1') is None
        
        processor.undo()  # 撤销cmd1
        assert model.find_by_id('div1') is None
        
        # 重做操作
        processor.redo()  # 重做cmd1
        assert model.find_by_id('div1') is not None
        
        processor.redo()  # 重做cmd2
        assert model.find_by_id('p1') is not None
        
        processor.redo()  # 重做cmd3
        assert model.find_by_id('span1') is not None
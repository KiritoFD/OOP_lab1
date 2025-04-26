import pytest
from unittest.mock import patch, MagicMock
from src.commands.display.base import DisplayCommand
from src.core.html_model import HtmlModel

class ConcreteDisplayCommand(DisplayCommand):
    """用于测试的具体显示命令实现"""
    def __init__(self, model):
        super().__init__(model)
        self.description = "Test Display Command"
        
    def execute(self):
        print("Display Command Executed")
        return True

@pytest.mark.unit
class TestDisplayCommand:
    """测试显示命令基类"""
    
    @pytest.fixture
    def model(self):
        return HtmlModel()
        
    def test_init(self, model):
        """测试初始化"""
        cmd = ConcreteDisplayCommand(model)
        assert cmd.model == model
        assert cmd.description == "Test Display Command"
        assert cmd.recordable == False  # 显示命令不应被记录
    
    @patch('builtins.print')
    def test_execute(self, mock_print, model):
        """测试执行方法"""
        cmd = ConcreteDisplayCommand(model)
        result = cmd.execute()
        
        # 验证执行结果
        assert result is True
        mock_print.assert_called_once_with("Display Command Executed")
    
    def test_undo(self, model):
        """测试撤销方法"""
        cmd = ConcreteDisplayCommand(model)
        result = cmd.undo()
        
        # 显示命令不应支持撤销
        assert result is False
    
    def test_abstract_class(self):
        """测试抽象类行为"""
        # DisplayCommand是抽象基类，不应该直接实例化
        model = HtmlModel()
        
        # 创建一个方法执行被省略的类（模拟抽象类的行为）
        class IncompleteDisplayCommand(DisplayCommand):
            def __init__(self, model):
                super().__init__(model)
        
        # 尝试执行，应该引发NotImplementedError
        cmd = IncompleteDisplayCommand(model)
        with pytest.raises(NotImplementedError):
            cmd.execute()
    
    def test_string_representation(self, model):
        """测试字符串表示"""
        cmd = ConcreteDisplayCommand(model)
        
        # 确保字符串表示包含命令描述
        assert str(cmd) == "Test Display Command"
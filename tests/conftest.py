"""全局测试配置和通用fixture"""
import pytest
import tempfile
import os
import sys
from unittest.mock import MagicMock, patch

# 确保src目录和tests目录在Python路径中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from src.core.html_model import HtmlModel
from src.commands.base import CommandProcessor
from src.commands.io import InitCommand
from src.session.session_manager import SessionManager
from src.session.state import session_state

@pytest.fixture
def temp_dir():
    """创建临时目录，测试结束后自动删除"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def model():
    """创建基本HTML模型"""
    return HtmlModel()

@pytest.fixture
def processor():
    """创建命令处理器"""
    return CommandProcessor()

@pytest.fixture
def initialized_model(model, processor):
    """创建并初始化模型"""
    processor.execute(InitCommand(model))
    return model

@pytest.fixture
def temp_environment():
    """创建临时测试环境，包含文件结构"""
    # 创建临时目录结构
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建内部结构
        os.makedirs(os.path.join(temp_dir, "docs"), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, "templates"), exist_ok=True)
        
        # 创建临时状态文件
        state_file = os.path.join(temp_dir, ".test_state.json")
        
        # 返回环境信息
        yield {
            'temp_dir': temp_dir,
            'state_file': state_file
        }

@pytest.fixture
def session(temp_dir):
    """创建会话管理器"""
    state_file = os.path.join(temp_dir, ".session_state.json")
    state_manager = session_state(state_file)
    return SessionManager(state_manager)

# 添加测试分层标记
def pytest_configure(config):
    """配置pytest标记"""
    config.addinivalue_line("markers", "unit: 标记单元测试")
    config.addinivalue_line("markers", "integration: 标记集成测试")
    config.addinivalue_line("markers", "system: 标记系统测试")
    config.addinivalue_line("markers", "slow: 标记慢速测试")

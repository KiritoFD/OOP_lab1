import pytest
import os
import sys

# 确保src目录在Python路径中
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def pytest_configure(config):
    """添加自定义标记"""
    config.addinivalue_line("markers", "slow: 标记较慢的测试")
    config.addinivalue_line("markers", "integration: 标记集成测试")
    config.addinivalue_line("markers", "unit: 标记单元测试")

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """设置测试环境变量，为所有测试提供通用配置"""
    # 设置环境变量
    os.environ["TESTING"] = "True"
    
    # 如有需要，在这里进行全局测试设置
    
    yield
    
    # 清理环境
    os.environ.pop("TESTING", None)

"""测试配置"""
import pytest
import os
import sys

# 添加源码目录到 Python 路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

@pytest.fixture(autouse=True)
def setup_test_env():
    """设置测试环境"""
    pass
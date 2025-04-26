"""单元测试基类"""
import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from tests.base_test import BaseTest

class BaseUnitTest(BaseTest):
    """单元测试基类，用于测试单个组件"""
    
    def setup_method(self):
        """为每个测试方法设置环境"""
        pass
        
    def teardown_method(self):
        """测试方法完成后清理"""
        pass

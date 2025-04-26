"""集成测试基类"""
import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.core.html_model import HtmlModel
from src.commands.base import CommandProcessor
from src.commands.io import InitCommand
from tests.base_test import BaseTest

class BaseIntegrationTest(BaseTest):
    """集成测试基类，用于测试多个组件的交互"""
    
    @pytest.fixture
    def setup(self):
        """设置基本测试环境"""
        model = HtmlModel()
        processor = CommandProcessor()
        
        # 初始化模型
        processor.execute(InitCommand(model))
        
        # 创建临时目录
        with pytest.MonkeyPatch().context() as mp:
            import tempfile
            with tempfile.TemporaryDirectory() as temp_dir:
                yield {
                    'model': model,
                    'processor': processor,
                    'temp_dir': temp_dir
                }

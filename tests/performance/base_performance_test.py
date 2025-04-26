"""性能测试基类"""
import sys
import os
import time
import pytest
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.core.html_model import HtmlModel
from src.commands.base import CommandProcessor
from src.commands.io import InitCommand
from tests.base_test import BaseTest

class BasePerformanceTest(BaseTest):
    """性能测试基类，用于测试性能指标"""
    
    @pytest.fixture
    def perf_setup(self):
        """设置性能测试环境"""
        model = HtmlModel()
        processor = CommandProcessor()
        
        # 初始化模型
        processor.execute(InitCommand(model))
        
        # 创建临时目录
        with pytest.MonkeyPatch().context() as mp:
            import tempfile
            with tempfile.TemporaryDirectory() as temp_dir:
                start_time = time.time()
                
                yield {
                    'model': model,
                    'processor': processor,
                    'temp_dir': temp_dir,
                    'start_time': start_time
                }
                
                # 输出测试执行时间
                print(f"\n测试执行时间: {time.time() - start_time:.4f}秒")
                
    def assert_performance(self, actual_time, expected_max, operation_desc="操作"):
        """断言性能满足要求"""
        assert actual_time < expected_max, f"{operation_desc}耗时 {actual_time:.4f}秒，超过了预期的 {expected_max}秒"
        print(f"{operation_desc}耗时: {actual_time:.4f}秒")

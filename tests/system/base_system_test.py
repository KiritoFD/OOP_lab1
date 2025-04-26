"""系统测试基类"""
import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.session.session_manager import SessionManager
from src.session.state import SessionState
from tests.base_test import BaseTest

class BaseSystemTest(BaseTest):
    """系统测试基类，用于测试整个应用系统"""
    
    @pytest.fixture
    def system_setup(self, temp_environment):
        """设置系统测试环境"""
        temp_dir = temp_environment['temp_dir']
        state_file = temp_environment['state_file']
        
        # 创建示例HTML文件
        sample_html = """<!DOCTYPE html>
<html id="html">
<head id="head"><title id="title">Test Page</title></head>
<body id="body">
    <h1 id="main-title">Welcome</h1>
    <p id="intro">This is a test page.</p>
</body>
</html>"""
        
        test_file = os.path.join(temp_dir, "index.html")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(sample_html)
            
        # 创建会话管理器
        state_manager = SessionState(state_file)
        session = SessionManager(state_manager)
        
        yield {
            'temp_dir': temp_dir,
            'state_file': state_file,
            'test_file': test_file,
            'session': session
        }

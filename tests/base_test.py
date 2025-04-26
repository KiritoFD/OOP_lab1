"""测试基类，提供共享功能和工具方法"""
import os
import pytest
from unittest.mock import patch

class BaseTest:
    """所有测试类的基类，提供通用功能"""
    
    @staticmethod
    def assert_element_exists(model, element_id, expected_tag=None, expected_text=None):
        """断言元素存在，并可选检查标签和文本"""
        element = model.find_by_id(element_id)
        assert element is not None, f"元素 '{element_id}' 应该存在"
        
        if expected_tag is not None:
            assert element.tag == expected_tag, f"元素 '{element_id}' 标签应为 '{expected_tag}'"
            
        if expected_text is not None:
            assert element.text == expected_text, f"元素 '{element_id}' 文本应为 '{expected_text}'"
    
    @staticmethod
    def assert_element_not_exists(model, element_id):
        """断言元素不存在"""
        with pytest.raises(Exception):  # 使用通用异常捕获适配不同实现
            model.find_by_id(element_id)
    
    @staticmethod
    def assert_is_child_of(model, child_id, parent_id):
        """断言一个元素是另一个元素的子元素"""
        child = model.find_by_id(child_id)
        parent = model.find_by_id(parent_id)
        assert child.parent == parent, f"元素 '{child_id}' 应是 '{parent_id}' 的子元素"
    
    @staticmethod
    def assert_command_executed(result):
        """断言命令执行成功"""
        assert result is True, "命令应该执行成功"
    
    @staticmethod
    def assert_in_output(output, *expected_strings):
        """断言输出中包含期望的字符串"""
        for expected in expected_strings:
            assert expected in output, f"输出应包含 '{expected}'"
    
    @staticmethod
    def create_test_file(temp_dir, filename, content):
        """在临时目录中创建测试文件"""
        file_path = os.path.join(temp_dir, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
    
    @staticmethod
    def capture_output(func, *args, **kwargs):
        """捕获函数输出"""
        import sys
        from io import StringIO
        
        old_stdout = sys.stdout
        try:
            sys.stdout = mystdout = StringIO()
            func(*args, **kwargs)
            sys.stdout = old_stdout
            return mystdout.getvalue()
        finally:
            sys.stdout = old_stdout

"""撤销/重做功能测试"""
import pytest
import os
import sys
from unittest.mock import patch

# 导入基础测试类
from tests.functional.base_functional_test import BaseFunctionalTest

from src.commands.edit.append_command import AppendCommand
from src.commands.edit.delete_command import DeleteCommand
from src.core.exceptions import ElementNotFoundError

@pytest.mark.unit
class TestUndoRedoFunctionality(BaseFunctionalTest):
    """撤销/重做功能测试"""
    
    def test_basic_undo_redo(self, setup):
        """测试基本撤销重做功能"""
        model = setup['model']
        processor = setup['processor']
        
        # 执行命令
        cmd = AppendCommand(model, 'div', 'test-div', 'body', 'Test Content')
        self.assert_command_executed(processor.execute(cmd))
        
        # 验证元素存在
        self.assert_element_exists(model, 'test-div', 'div', 'Test Content')
        self.assert_is_child_of(model, 'test-div', 'body')
        
        # 撤销并验证元素已移除
        self.assert_command_executed(processor.undo())
        self.assert_element_not_exists(model, 'test-div')
        
        # 重做并验证元素已恢复
        self.assert_command_executed(processor.redo())
        self.assert_element_exists(model, 'test-div', 'div', 'Test Content')
    
    def test_multiple_operations_undo_redo(self, setup):
        """测试多个操作的撤销重做"""
        model = setup['model']
        processor = setup['processor']
        
        # 执行多个命令
        cmd1 = AppendCommand(model, 'div', 'container', 'body')
        cmd2 = AppendCommand(model, 'p', 'para1', 'container', '段落1')
        cmd3 = AppendCommand(model, 'p', 'para2', 'container', '段落2')
        
        self.assert_command_executed(processor.execute(cmd1))
        self.assert_command_executed(processor.execute(cmd2))
        self.assert_command_executed(processor.execute(cmd3))
        
        # 验证所有元素存在
        self.assert_element_exists(model, 'container')
        self.assert_element_exists(model, 'para1', 'p', '段落1')
        self.assert_element_exists(model, 'para2', 'p', '段落2')
        
        # 连续撤销
        self.assert_command_executed(processor.undo())  # 撤销添加para2
        self.assert_element_not_exists(model, 'para2')
        self.assert_element_exists(model, 'para1')
        
        self.assert_command_executed(processor.undo())  # 撤销添加para1
        self.assert_element_not_exists(model, 'para1')
        self.assert_element_exists(model, 'container')
        
        # 重做一个操作
        self.assert_command_executed(processor.redo())  # 重做添加para1
        self.assert_element_exists(model, 'para1', 'p', '段落1')
        self.assert_element_not_exists(model, 'para2')
    
    def test_undo_redo_edge_cases(self, setup):
        """测试撤销/重做边缘情况"""
        model = setup['model']
        processor = setup['processor']
        
        # 测试空栈撤销
        result = processor.undo()
        # 不做具体值的断言，取决于实现
        
        # 测试空栈重做
        result = processor.redo()
        # 不做具体值的断言，取决于实现
        
        # 执行、撤销、重做后删除
        cmd1 = AppendCommand(model, 'div', 'div1', 'body')
        self.assert_command_executed(processor.execute(cmd1))
        self.assert_element_exists(model, 'div1')
        
        self.assert_command_executed(processor.undo())
        self.assert_element_not_exists(model, 'div1')
        
        self.assert_command_executed(processor.redo())
        self.assert_element_exists(model, 'div1')
        
        cmd2 = DeleteCommand(model, 'div1')
        self.assert_command_executed(processor.execute(cmd2))
        self.assert_element_not_exists(model, 'div1')
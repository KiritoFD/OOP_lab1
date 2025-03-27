import pytest
import time
import os
import tempfile

from src.core.html_model import HtmlModel
from src.commands.base import CommandProcessor
from src.commands.io_commands import InitCommand, SaveCommand, ReadCommand
from src.commands.edit.append_command import AppendCommand
from src.commands.edit.insert_command import InsertCommand
from src.commands.edit.delete_command import DeleteCommand
from src.commands.edit.edit_text_command import EditTextCommand
from src.commands.display_commands import PrintTreeCommand

class TestPerformance:
    """性能测试"""
    
    @pytest.fixture
    def setup(self):
        """设置测试环境"""
        model = HtmlModel()
        processor = CommandProcessor()
        
        # 初始化
        init_cmd = InitCommand(model)
        processor.execute(init_cmd)
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            yield {
                'model': model,
                'processor': processor,
                'temp_dir': temp_dir
            }
    
    # 使用pytest.mark.slow标记以便可以选择性跳过耗时测试
    @pytest.mark.slow
    def test_large_document_performance(self, setup, capsys):
        """测试处理大量元素时的性能"""
        model = setup['model']
        processor = setup['processor']
        temp_dir = setup['temp_dir']
        
        # 记录开始时间
        start_time = time.time()
        
        # 创建大型文档结构 - 1000个元素
        for i in range(10):  # 10个主区块
            main_id = f'section{i}'
            processor.execute(AppendCommand(model, 'div', main_id, 'body', f'Section {i}'))
            
            # 每个主区块包含10个子区块
            for j in range(10):
                sub_id = f'{main_id}-sub{j}'
                processor.execute(AppendCommand(model, 'div', sub_id, main_id, f'Subsection {i}.{j}'))
                
                # 每个子区块包含10个段落
                for k in range(10):
                    para_id = f'{sub_id}-p{k}'
                    processor.execute(AppendCommand(model, 'p', para_id, sub_id, 
                                                 f'This is paragraph {k} in subsection {i}.{j}'))
        
        # 记录创建时间
        creation_time = time.time() - start_time
        print(f"\n创建1000个元素耗时: {creation_time:.2f}秒")
        
        # 测试保存大型文档的性能
        save_start = time.time()
        file_path = os.path.join(temp_dir, 'large_doc_perf.html')
        processor.execute(SaveCommand(model, file_path))
        save_time = time.time() - save_start
        print(f"保存1000个元素的文档耗时: {save_time:.2f}秒")
        
        # 测试加载大型文档的性能
        new_model = HtmlModel()
        new_processor = CommandProcessor()
        load_start = time.time()
        processor.execute(ReadCommand(new_processor, new_model, file_path))
        load_time = time.time() - load_start
        print(f"加载1000个元素的文档耗时: {load_time:.2f}秒")
        
        # 测试显示大型文档的性能
        display_start = time.time()
        processor.execute(PrintTreeCommand(model))
        captured = capsys.readouterr()  # 捕获输出
        display_time = time.time() - display_start
        print(f"显示1000个元素的文档耗时: {display_time:.2f}秒")
        
        # 确保性能在合理范围内 (这些阈值可根据实际硬件调整)
        assert creation_time < 5.0, "创建1000个元素不应超过5秒"
        assert save_time < 2.0, "保存文档不应超过2秒"
        assert load_time < 2.0, "加载文档不应超过2秒"
        assert display_time < 3.0, "显示文档不应超过3秒"
    
    def test_undo_redo_performance(self, setup):
        """测试撤销/重做操作的性能"""
        model = setup['model']
        processor = setup['processor']
        
        # 执行100个可撤销的命令
        start_time = time.time()
        for i in range(100):
            cmd = AppendCommand(model, 'p', f'p{i}', 'body', f'Text {i}')
            processor.execute(cmd)
        
        append_time = time.time() - start_time
        print(f"\n执行100个追加命令耗时: {append_time:.2f}秒")
        
        # 测试连续撤销100次的性能
        start_time = time.time()
        for i in range(100):
            processor.undo()
        
        undo_time = time.time() - start_time
        print(f"连续撤销100次耗时: {undo_time:.2f}秒")
        
        # 测试连续重做100次的性能
        start_time = time.time()
        for i in range(100):
            processor.redo()
        
        redo_time = time.time() - start_time
        print(f"连续重做100次耗时: {redo_time:.2f}秒")
        
        # 性能验证
        assert append_time < 2.0, "100次命令执行不应超过2秒"
        assert undo_time < 1.0, "100次撤销不应超过1秒"
        assert redo_time < 1.0, "100次重做不应超过1秒"
    
    def test_multiple_operations_performance(self, setup):
        """测试混合操作场景下的性能"""
        model = setup['model']
        processor = setup['processor']
        
        # 记录开始时间
        start_time = time.time()
        
        # 模拟实际的编辑会话 - 混合多种操作
        # 1. 创建基本结构
        for i in range(10):
            processor.execute(AppendCommand(model, 'div', f'section{i}', 'body'))
            
        # 2. 添加元素到结构
        for i in range(10):
            for j in range(5):
                processor.execute(AppendCommand(model, 'p', f'p-{i}-{j}', f'section{i}', f'Para {i}.{j}'))
                
        # 3. 执行一些编辑操作
        for i in range(5):
            processor.execute(EditTextCommand(model, f'p-{i}-0', f'Modified paragraph {i}.0'))
            
        # 4. 删除一些元素
        for i in range(5, 10):
            processor.execute(DeleteCommand(model, f'p-{i}-0'))
            
        # 5. 撤销几次操作
        for _ in range(10):
            processor.undo()
            
        # 6. 重做几次操作
        for _ in range(5):
            processor.redo()
        
        # 记录总时间
        total_time = time.time() - start_time
        print(f"\n混合操作场景耗时: {total_time:.2f}秒")
        
        # 验证性能
        assert total_time < 3.0, "混合操作场景不应超过3秒"
        
        # 验证最终状态的正确性
        # 因为有撤销和重做，状态取决于具体的逻辑，但至少结构应该保持完整
        for i in range(10):
            section = model.find_by_id(f'section{i}')
            assert section is not None
            assert section.tag == 'div'

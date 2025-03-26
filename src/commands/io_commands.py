from .base import Command
from ..io_.parser import HtmlParser
from ..io_.writer import HtmlWriter
from ..core.html_model import HtmlModel

class IoCommand(Command):
    """IO命令的基类，执行后会清空命令历史"""
    def __init__(self, processor):
        super().__init__()
        self.processor = processor

    def _do_execute(self) -> bool:
        """子类实现具体的IO操作"""
        raise NotImplementedError

    def execute(self) -> bool:
        """执行IO操作并清空历史"""
        result = self._do_execute()
        if result:
            self.processor.clear_history()
        return result

    def undo(self) -> bool:
        """IO命令不支持撤销"""
        return False

class ReadCommand(IoCommand):
    """读取HTML文件命令"""
    def __init__(self, processor, model: HtmlModel, filepath: str):
        super().__init__(processor)
        self.model = model
        self.filepath = filepath

    def _do_execute(self) -> bool:
        try:
            new_model = HtmlParser.parse_file(self.filepath)
            return self.model.replace_content(new_model.root)
        except Exception as e:
            return False

class SaveCommand(IoCommand):
    """保存HTML文件命令"""
    def __init__(self, processor, model: HtmlModel, filepath: str):
        super().__init__(processor)
        self.model = model
        self.filepath = filepath

    def _do_execute(self) -> bool:
        try:
            return HtmlWriter.write_file(self.model, self.filepath)
        except Exception as e:
            return False

class InitCommand(IoCommand):
    """初始化编辑器命令"""
    def __init__(self, processor, model: HtmlModel):
        super().__init__(processor)
        self.model = model

    def _do_execute(self) -> bool:
        try:
            # 创建一个空的HTML文档结构
            html_content = """
<html>
    <head>
        <title></title>
    </head>
    <body></body>
</html>
"""
            new_model = HtmlParser.parse_string(html_content)
            return self.model.replace_content(new_model.root)
        except Exception as e:
            return False
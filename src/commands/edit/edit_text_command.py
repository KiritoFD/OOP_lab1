from ..base import Command
from ...core.html_model import HtmlModel
from ...core.exceptions import ElementNotFoundError

class EditTextCommand(Command):
    """编辑元素文本内容"""
    def __init__(self, model: HtmlModel, element_id: str, new_text: str):
        super().__init__()
        self.model = model
        self.element_id = element_id
        self.new_text = new_text
        self.old_text = None
        self.element = None

    def _validate_params(self) -> None:
        """验证参数有效性"""
        if not self.element_id or not isinstance(self.element_id, str):
            raise ValueError("元素ID不能为空且必须是字符串")
            
        if not isinstance(self.new_text, str):
            raise ValueError("新文本内容必须是字符串")
            
        # 查找要编辑的元素
        self.element = self.model.find_by_id(self.element_id)
        if not self.element:
            raise ElementNotFoundError(f"未找到ID为 '{self.element_id}' 的元素")

    def execute(self) -> bool:
        """执行文本编辑命令"""
        try:
            # 验证参数
            self._validate_params()
            
            # 保存原文本
            self.old_text = self.element.text
            
            # 设置新文本
            self.element.text = self.new_text
            return True
            
        except Exception as e:
            # 重置状态
            self.old_text = None
            self.element = None
            raise
            
    def undo(self) -> bool:
        """撤销文本编辑命令"""
        try:
            # 确保有需要撤销的状态
            if not self.element or self.old_text is None:
                return False
                
            # 恢复原文本
            self.element.text = self.old_text
            return True
            
        except Exception as e:
            print(f"撤销文本编辑命令时发生错误: {str(e)}")
            return False
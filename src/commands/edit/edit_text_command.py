from ..base import Command
from ...core.html_model import HtmlModel
from ...core.exceptions import ElementNotFoundError

class EditTextCommand(Command):
    """编辑HTML元素的文本内容"""
    def __init__(self, model: HtmlModel, element_id: str, new_text: str):
        super().__init__()
        self.model = model
        self.element_id = element_id
        self.new_text = new_text
        self.old_text = None
        self._executed = False
        
    def _validate_params(self) -> None:
        """验证参数有效性"""
        if not self.element_id or not isinstance(self.element_id, str):
            raise ValueError("元素ID不能为空且必须是字符串")
        
        # 验证元素是否存在
        element = self.model.find_by_id(self.element_id)
        if not element:
            raise ElementNotFoundError(f"未找到ID为 '{self.element_id}' 的元素")
            
        # 记录原始文本
        self.old_text = element.text
    
    def execute(self) -> bool:
        """执行编辑文本命令"""
        try:
            # 如果命令已执行，直接返回
            if self._executed:
                return True
                
            # 验证参数
            self._validate_params()
            
            # 找到要编辑的元素
            element = self.model.find_by_id(self.element_id)
            
            # 更新文本内容
            element.text = self.new_text
            
            print(f"Successfully updated text of element '{self.element_id}': '{self.old_text}' -> '{self.new_text}'")
            self._executed = True
            return True
            
        except (ValueError, ElementNotFoundError) as e:
            # 向上传播异常
            raise
        except Exception as e:
            print(f"编辑文本时发生错误: {str(e)}")
            self._executed = False
            return False
    
    def undo(self) -> bool:
        """撤销编辑文本命令"""
        try:
            # 确保有需要撤销的状态
            if self.old_text is None or not self._executed:
                return False
                
            # 找到要恢复的元素
            element = self.model.find_by_id(self.element_id)
            if not element:
                print(f"Failed to undo: element '{self.element_id}' not found")
                return False
                
            # 恢复原始文本
            element.text = self.old_text
            
            print(f"Successfully restored text of element '{self.element_id}': '{self.new_text}' -> '{self.old_text}'")
            self._executed = False
            return True
            
        except Exception as e:
            print(f"撤销编辑文本命令时发生错误: {str(e)}")
            return False
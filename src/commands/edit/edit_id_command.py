from ..base import Command
from ...core.html_model import HtmlModel
from ...core.exceptions import ElementNotFoundError, DuplicateIdError

class EditIdCommand(Command):
    """编辑元素ID"""
    def __init__(self, model: HtmlModel, old_id: str, new_id: str):
        super().__init__()
        self.model = model
        self.old_id = old_id
        self.new_id = new_id
        self.element = None

    def _validate_params(self) -> None:
        """验证参数有效性"""
        if not self.old_id or not isinstance(self.old_id, str):
            raise ValueError("原ID不能为空且必须是字符串")
            
        if not self.new_id or not isinstance(self.new_id, str):
            raise ValueError("新ID不能为空且必须是字符串")
            
        # 查找要编辑的元素
        self.element = self.model.find_by_id(self.old_id)
        if not self.element:
            raise ElementNotFoundError(f"未找到ID为 '{self.old_id}' 的元素")
            
        # 检查新ID是否已存在
        if self.model.find_by_id(self.new_id):
            raise DuplicateIdError(f"ID '{self.new_id}' 已存在")

    def execute(self) -> bool:
        """执行ID编辑命令"""
        try:
            # 验证参数
            self._validate_params()
            
            # 从ID映射中移除旧ID
            del self.model._id_map[self.old_id]
            
            # 更新元素ID
            self.element.id = self.new_id
            
            # 注册新ID
            self.model._id_map[self.new_id] = self.element
            
            return True
            
        except Exception as e:
            # 发生错误时恢复原状态
            if self.element:
                if self.new_id in self.model._id_map:
                    del self.model._id_map[self.new_id]
                self.element.id = self.old_id
                self.model._id_map[self.old_id] = self.element
            raise
            
    def undo(self) -> bool:
        """撤销ID编辑命令"""
        try:
            # 确保有需要撤销的状态
            if not self.element:
                return False
                
            # 从ID映射中移除新ID
            del self.model._id_map[self.new_id]
            
            # 恢复原ID
            self.element.id = self.old_id
            
            # 重新注册原ID
            self.model._id_map[self.old_id] = self.element
            
            return True
            
        except Exception as e:
            print(f"撤销ID编辑命令时发生错误: {str(e)}")
            return False
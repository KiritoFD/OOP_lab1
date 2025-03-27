from src.commands.base import Command
from src.core.exceptions import ElementNotFoundError, IdCollisionError, InvalidOperationError, DuplicateIdError

class EditIdCommand(Command):
    """编辑HTML元素ID的命令"""
    
    def __init__(self, model, element_id, new_id):
        super().__init__()  # Don't pass model to the base class constructor
        self.model = model  # Store model as an instance variable instead
        self.element_id = element_id
        self.new_id = new_id
        self.old_id = element_id
        self.description = f"编辑ID: '{element_id}' -> '{new_id}'"
        
    def execute(self):
        """执行编辑ID命令"""
        # 检查是否为空ID
        if not self.new_id:
            raise InvalidOperationError("新ID不能为空")
            
        # 如果新旧ID相同，无需操作
        if self.element_id == self.new_id:
            return True
        
        # 先验证element_id是否存在
        try:
            element = self.model.find_by_id(self.element_id)
        except ElementNotFoundError:
            # 直接重新抛出异常，不捕获
            raise
            
        # 先检查新ID是否与现有ID冲突
        if self.new_id in self.model._id_map:
            raise DuplicateIdError(f"ID '{self.new_id}' 已存在")
            
        # 更新元素ID
        element.id = self.new_id
        # 更新模型中的ID索引
        self.model.update_element_id(self.element_id, self.new_id)
        
        return True
        
    def can_execute(self):
        """检查命令是否可以执行"""
        # 检查新ID是否为空
        if not self.new_id:
            return False
            
        # 如果新旧ID相同，无需操作，但视为可执行
        if self.element_id == self.new_id:
            return True
            
        try:
            # 检查旧元素是否存在
            self.model.find_by_id(self.element_id)
            
            # 检查新ID是否已存在
            try:
                self.model.find_by_id(self.new_id)
                # 如果找到了同名元素，说明会有ID冲突
                return False
            except ElementNotFoundError:
                # 新ID不存在，可以安全使用
                return True
                
        except ElementNotFoundError:
            return False
        except Exception:
            return False
        
    def undo(self):
        """撤销编辑ID命令"""
        try:
            # 找到元素（现在使用新ID）
            element = self.model.find_by_id(self.new_id)
            
            # 恢复回原始ID
            element.id = self.old_id
            
            # 更新模型中的ID索引
            self.model.update_element_id(self.new_id, self.old_id)
            
            return True
        except ElementNotFoundError:
            # 如果元素已被删除，则无法撤销
            return False
    
    def __str__(self):
        """命令的字符串表示"""
        return f"EditIdCommand('{self.element_id}' -> '{self.new_id}')"
from src.commands.base import Command
from src.core.exceptions import ElementNotFoundError, IdCollisionError, InvalidOperationError, DuplicateIdError
from src.commands.command_exceptions import CommandExecutionError, CommandParameterError

class EditIdCommand(Command):
    """编辑HTML元素ID的命令"""
    
    def __init__(self, model, element_id, new_id):
        super().__init__()
        self.model = model
        self.element_id = element_id
        self.new_id = new_id
        self.old_id = element_id
        self.description = f"编辑ID: '{element_id}' -> '{new_id}'"
        
    def _validate_params(self) -> None:
        """验证参数有效性"""
        if not self.new_id:
            raise InvalidOperationError("新ID不能为空")
            
        if self.element_id == self.new_id:
            return
            
        if self.new_id in self.model._id_map:
            raise DuplicateIdError(f"ID '{self.new_id}' 已存在")

    def can_execute(self):
        """检查命令是否可以执行"""
        try:
            self._validate_params()
            return True
        except (InvalidOperationError, DuplicateIdError):
            return False

    def execute(self):
        """执行编辑ID命令"""
        try:
            # 检查是否为空ID
            if not self.new_id:
                raise InvalidOperationError("新ID不能为空")
                
            # 如果新旧ID相同，无需操作
            if self.element_id == self.new_id:
                return True
            
            # 查找元素 - 如果不存在会抛出ElementNotFoundError
            element = self.model.find_by_id(self.element_id)
            
            # 检查新ID是否与现有ID冲突
            if self.new_id in self.model._id_map:
                raise DuplicateIdError(f"ID '{self.new_id}' 已存在")
                
            # 更新元素ID
            self.original_id = element.id
            element.id = self.new_id
            
            # 更新模型中的ID索引
            self.model.update_element_id(self.element_id, self.new_id)
            
            return True
        except ElementNotFoundError as e:
            # 明确捕获ElementNotFoundError并重新抛出
            raise CommandExecutionError(f"元素 '{self.element_id}' 不存在") from e
        except DuplicateIdError as e:
            # 明确捕获DuplicateIdError并重新抛出
            raise CommandExecutionError(f"ID冲突: {e}") from e
        except Exception as e:
            raise CommandExecutionError(f"执行编辑ID命令时出错: {str(e)}") from e

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
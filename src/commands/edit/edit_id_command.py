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
        """检查命令是否可以执行（仅基本校验）"""
        try:
            # 只检查非空和自身相等的情况
            if not self.new_id:
                return False
            if self.element_id == self.new_id:
                return False
            return True
        except Exception:
            return False

    def execute(self):
        """执行编辑ID命令"""
        try:
            print(f"开始执行ID修改：{self.element_id} -> {self.new_id}")
            # 完整参数验证
            self._validate_params()
            print("参数验证通过")
            
            # 查找元素
            print(f"正在查找元素：{self.element_id}")
            element = self.model.find_by_id(self.element_id)
            print(f"找到元素：{element}")
                
            # 更新元素ID
            print(f"更新ID前检查：新ID '{self.new_id}' 是否存在？{self.new_id in self.model._id_map}")
            self.original_id = element.id
            element.id = self.new_id
            print(f"执行模型ID映射更新：{self.element_id} -> {self.new_id}")
            self.model.update_element_id(self.element_id, self.new_id)
            
            return True
        except (ElementNotFoundError, DuplicateIdError, InvalidOperationError):
            # 直接抛出原始异常
            raise
        except Exception as e:
            print(f"捕获到未预期异常：{type(e).__name__} - {str(e)}")
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
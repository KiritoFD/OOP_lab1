# 命令解析器
from typing import Optional

# 使用绝对导入路径 - 修复循环导入
from src.commands.base import Command
from src.commands.io import ReadCommand, SaveCommand, InitCommand
from src.commands.edit.delete_command import DeleteCommand
from src.commands.edit.edit_text_command import EditTextCommand
from src.commands.edit.append_command import AppendCommand
from src.commands.edit.edit_id_command import EditIdCommand
from src.commands.display import PrintTreeCommand
from src.commands.display import SpellCheckCommand
from src.commands.edit.insert_command import InsertCommand
from src.core.exceptions import InvalidCommandError

class CommandParser:
    """命令解析器，用于将字符串命令解析为Command对象"""
    
    def __init__(self, processor, model):
        self.processor = processor
        self.model = model
        
    def parse(self, command_string: str) -> Optional[Command]:
        """解析命令字符串 - 公开方法，供应用调用"""
        return self.parse_command(command_string)
        
    def parse_command(self, command_string: str) -> Optional[Command]:
        """解析命令字符串"""
        parts = command_string.split()
        if not parts:
            return None
            
        command_name = parts[0].lower()
        
        try:
            if command_name == 'read':
                if len(parts) != 2:
                    raise InvalidCommandError("Read 命令需要一个文件路径参数")
                file_path = parts[1]
                # 移除引号，如果存在
                if (file_path.startswith('"') and file_path.endswith('"')) or \
                   (file_path.startswith("'") and file_path.endswith("'")):
                    file_path = file_path[1:-1]
                return ReadCommand(self.processor, self.model, file_path)
                
            elif command_name == 'save':
                if len(parts) != 2:
                    raise InvalidCommandError("Save 命令需要一个文件路径参数")
                file_path = parts[1]
                # 移除引号，如果存在
                if (file_path.startswith('"') and file_path.endswith('"')) or \
                   (file_path.startswith("'") and file_path.endswith("'")):
                    file_path = file_path[1:-1]
                return SaveCommand(self.model, file_path)
                
            elif command_name == 'init':
                return InitCommand(self.model)
                
            elif command_name == 'append':
                if len(parts) < 4:
                    raise InvalidCommandError("Append 命令需要 tag, id, parent_id 和可选的 text 参数")
                tag = parts[1]
                id_value = parts[2]
                parent_id = parts[3]
                text = ' '.join(parts[4:]) if len(parts) > 4 else None
                return AppendCommand(self.model, tag, id_value, parent_id, text)
                
            elif command_name == 'insert':
                if len(parts) < 4:
                    raise InvalidCommandError("Insert 命令需要 tag, id, location 和可选的 text 参数")
                tag = parts[1]
                id_value = parts[2]
                location = parts[3]
                text = ' '.join(parts[4:]) if len(parts) > 4 else None
                return InsertCommand(self.model, tag, id_value, location, text)
                
            elif command_name == 'delete':
                if len(parts) != 2:
                    raise InvalidCommandError("Delete 命令需要一个元素ID参数")
                element_id = parts[1]
                return DeleteCommand(self.model, element_id)
                
            elif command_name == 'edit-text':
                if len(parts) < 2:
                    raise InvalidCommandError("Edit-text 命令需要 element_id 和可选的 text 参数")
                element_id = parts[1]
                text = ' '.join(parts[2:]) if len(parts) > 2 else ''
                return EditTextCommand(self.model, element_id, text)
                
            elif command_name == 'edit-id':
                if len(parts) != 3:
                    raise InvalidCommandError("Edit-id 命令需要 oldId 和 newId 参数")
                old_id = parts[1]
                new_id = parts[2]
                return EditIdCommand(self.model, old_id, new_id)
                
            elif command_name == 'print':
                return PrintTreeCommand(self.model)
                
            elif command_name == 'spellcheck':
                return SpellCheckCommand(self.model)
                
            elif command_name == 'undo':
                # 特殊处理，返回一个空字符表示应该调用处理器的undo方法
                return "UNDO"
                
            elif command_name == 'redo':
                # 特殊处理，返回一个空字符表示应该调用处理器的redo方法
                return "REDO"
                
            else:
                raise InvalidCommandError(f"未知命令: {command_name}")
        
        except InvalidCommandError as e:
            print(f"命令解析错误: {str(e)}")
            return None
        except Exception as e:
            print(f"发生错误: {str(e)}")
            return None

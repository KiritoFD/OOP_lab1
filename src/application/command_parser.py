# 命令解析器
from typing import List, Optional
from ..commands.base import Command, CommandProcessor
from ..commands.edit_commands import (
    InsertCommand, AppendCommand, DeleteCommand, 
    EditTextCommand, EditIdCommand
)
from ..commands.display_commands import PrintTreeCommand, SpellCheckCommand
from ..commands.io_commands import ReadCommand, SaveCommand, InitCommand
from ..core.html_model import HtmlModel

class CommandParser:
    """命令解析器，负责解析用户输入并创建相应的命令对象"""
    
    def __init__(self, model: HtmlModel, processor: CommandProcessor):
        self.model = model
        self.processor = processor
        
    def parse(self, command_line: str) -> Optional[Command]:
        """
        解析命令行输入，创建并返回相应的命令对象
        
        Args:
            command_line: 用户输入的命令行文本
            
        Returns:
            创建的命令对象，如果命令无效则返回None
        """
        if not command_line or command_line.strip() == "":
            return None
            
        parts = command_line.strip().split()
        command_name = parts[0].lower()
        
        try:
            # 编辑类命令
            if command_name == "insert" and len(parts) >= 4:
                # insert tagName idValue insertLocation [textContent]
                tag_name = parts[1]
                id_value = parts[2]
                location = parts[3]
                text = " ".join(parts[4:]) if len(parts) > 4 else None
                return InsertCommand(self.model, tag_name, id_value, location, text)
                
            elif command_name == "append" and len(parts) >= 4:
                # append tagName idValue parentElement [textContent]
                tag_name = parts[1]
                id_value = parts[2]
                parent_id = parts[3]
                text = " ".join(parts[4:]) if len(parts) > 4 else None
                return AppendCommand(self.model, tag_name, id_value, parent_id, text)
                
            elif command_name == "edit-id" and len(parts) == 3:
                # edit-id oldId newId
                old_id = parts[1]
                new_id = parts[2]
                return EditIdCommand(self.model, old_id, new_id)
                
            elif command_name == "edit-text" and len(parts) >= 2:
                # edit-text element [newTextContent]
                element_id = parts[1]
                text = " ".join(parts[2:]) if len(parts) > 2 else ""
                return EditTextCommand(self.model, element_id, text)
                
            elif command_name == "delete" and len(parts) == 2:
                # delete element
                element_id = parts[1]
                return DeleteCommand(self.model, element_id)
                
            # 显示类命令
            elif command_name == "print-tree" and len(parts) == 1:
                # print-tree
                return PrintTreeCommand(self.model)
                
            elif command_name == "spell-check" and len(parts) == 1:
                # spell-check
                return SpellCheckCommand(self.model)
                
            # IO类命令
            elif command_name == "read" and len(parts) == 2:
                # read filepath
                filepath = parts[1]
                return ReadCommand(self.model, filepath)
                
            elif command_name == "save" and len(parts) == 2:
                # save filepath
                filepath = parts[1]
                return SaveCommand(self.model, filepath)
                
            elif command_name == "init" and len(parts) == 1:
                # init
                return InitCommand(self.model)
                
            # 撤销和重做
            elif command_name == "undo" and len(parts) == 1:
                # 直接执行处理器的撤销，不创建命令
                if self.processor.undo():
                    print("撤销成功")
                else:
                    print("无法撤销")
                return None
                
            elif command_name == "redo" and len(parts) == 1:
                # 直接执行处理器的重做，不创建命令
                if self.processor.redo():
                    print("重做成功")
                else:
                    print("无法重做")
                return None
                
            else:
                print(f"无效的命令: {command_line}")
                return None
                
        except Exception as e:
            print(f"命令创建失败: {str(e)}")
            return None

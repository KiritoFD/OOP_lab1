# Create this file if it doesn't exist already

# filepath: c:\Github\OOP_lab1\src\session\editor.py
"""Editor class implementation"""

from src.core.html_model import HtmlModel
from src.commands.base import CommandProcessor
from src.commands.io import SaveCommand

class Editor:
    """Represents an HTML file editor instance"""
    
    def __init__(self, filename):
        """Initialize editor instance"""
        self.filename = filename
        self.model = HtmlModel()
        self.model.editor = self  # Make model aware of its editor for modification tracking
        self.processor = CommandProcessor()
        self.modified = False
        self.show_id = True  # Default to showing IDs
        
    def save(self):
        """Save editor content to file"""
        try:
            cmd = SaveCommand(self.model, self.filename)
            cmd.processor = self.processor
            result = self.processor.execute(cmd)
            if result:
                self.modified = False
            return result
        except Exception as e:
            print(f"保存文件失败: {str(e)}")
            return False
            
    def save_as(self, new_filename):
        """Save editor content to a new file"""
        try:
            cmd = SaveCommand(self.model, new_filename)
            cmd.processor = self.processor
            result = self.processor.execute(cmd)
            if result:
                self.filename = new_filename
                self.modified = False
            return result
        except Exception as e:
            print(f"另存为失败: {str(e)}")
            return False
    
    def execute_command(self, command):
        """Execute an edit command in this editor"""
        try:
            if not hasattr(command, 'recordable'):
                command.recordable = True
                
            result = self.processor.execute(command)
            if result and command.recordable:
                self.modified = True
            return result
        except Exception as e:
            print(f"执行命令失败: {str(e)}")
            return False

import os
import json
import pickle
from pathlib import Path

from src.core.html_model import HtmlModel
from src.commands.base import CommandProcessor
from src.commands.io.commands import InitCommand, ReadCommand, SaveCommand

class Editor:
    """Represents a single editor instance for a file"""
    
    def __init__(self, filename=None):
        self.filename = filename
        self.model = HtmlModel()
        self.processor = CommandProcessor()
        self.modified = False
        self.show_id = True
        
        # Initialize with empty HTML if no file or new file
        if not filename or not os.path.exists(filename):
            cmd = InitCommand(self.model)
            self.processor.execute_command(cmd)
        else:
            cmd = ReadCommand(self.model, filename)
            self.processor.execute_command(cmd)
    
    def get_filename(self):
        """Get the filename of this editor"""
        return self.filename
        
    def get_basename(self):
        """Get the base filename (without path) of this editor"""
        return os.path.basename(self.filename) if self.filename else None
    
    def is_modified(self):
        """Check if the content has been modified"""
        return self.modified
    
    def set_modified(self, modified):
        """Set the modified state"""
        self.modified = modified
    
    def save(self, filename=None):
        """Save the editor content to a file"""
        target_file = filename or self.filename
        if not target_file:
            raise ValueError("No filename specified for save operation")
        
        cmd = SaveCommand(self.model, target_file)
        result = self.processor.execute_command(cmd)
        if result:
            self.filename = target_file
            self.modified = False
        return result


class EditorSession:
    """Manages multiple editors in a session"""
    
    def __init__(self):
        self.editors = []  # List of Editor objects
        self.current_editor_index = -1
        self.current_dir = os.getcwd()
    
    def load_file(self, filepath):
        """Load a file into a new editor"""
        abs_path = os.path.abspath(filepath)
        
        # Check if file is already open
        for i, editor in enumerate(self.editors):
            if editor.get_filename() == abs_path:
                self.current_editor_index = i
                return True
        
        # Create new editor for the file
        try:
            editor = Editor(abs_path)
            self.editors.append(editor)
            self.current_editor_index = len(self.editors) - 1
            return True
        except Exception as e:
            print(f"Error loading file: {e}")
            return False
    
    def save_current_file(self, filepath=None):
        """Save the current editor to a file"""
        if not self.has_active_editor():
            return False
            
        editor = self.get_current_editor()
        return editor.save(filepath)
    
    def close_current_file(self):
        """Close the current editor"""
        if not self.has_active_editor():
            return False
        
        # Remove the current editor
        self.editors.pop(self.current_editor_index)
        
        # Update index
        if not self.editors:
            self.current_editor_index = -1
        elif self.current_editor_index >= len(self.editors):
            self.current_editor_index = len(self.editors) - 1
            
        return True
    
    def switch_to_file(self, filename):
        """Switch to editor with the given filename"""
        # Try exact path match first
        abs_path = os.path.abspath(filename)
        for i, editor in enumerate(self.editors):
            if editor.get_filename() == abs_path:
                self.current_editor_index = i
                return True
        
        # Try basename match as fallback
        for i, editor in enumerate(self.editors):
            if editor.get_basename() == filename:
                self.current_editor_index = i
                return True
                
        return False
    
    def get_editor_list(self):
        """Return list of all editors"""
        return self.editors
    
    def has_active_editor(self):
        """Check if there is an active editor"""
        return 0 <= self.current_editor_index < len(self.editors)
    
    def get_current_editor(self):
        """Get the current editor"""
        if not self.has_active_editor():
            return None
        return self.editors[self.current_editor_index]
    
    def get_current_model(self):
        """Get the model of the current editor"""
        editor = self.get_current_editor()
        return editor.model if editor else None
    
    def get_current_filename(self):
        """Get the filename of the current editor"""
        editor = self.get_current_editor()
        return editor.get_filename() if editor else None
    
    def set_show_id(self, show_id):
        """Set whether to show element IDs in the current editor"""
        if not self.has_active_editor():
            return False
            
        editor = self.get_current_editor()
        editor.show_id = show_id
        return True
    
    def get_show_id(self):
        """Get whether element IDs are shown in the current editor"""
        editor = self.get_current_editor()
        return editor.show_id if editor else True
    
    def save_session(self):
        """Save the current session state"""
        session_file = self._get_session_file_path()
        
        session_data = {
            'current_index': self.current_editor_index,
            'editors': []
        }
        
        for editor in self.editors:
            editor_data = {
                'filename': editor.get_filename(),
                'show_id': editor.show_id,
                'modified': editor.is_modified()
            }
            session_data['editors'].append(editor_data)
            
        try:
            with open(session_file, 'w') as f:
                json.dump(session_data, f)
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False
    
    def load_session(self):
        """Load a previously saved session"""
        session_file = self._get_session_file_path()
        
        if not os.path.exists(session_file):
            return False
            
        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
                
            # Clear current editors
            self.editors = []
            self.current_editor_index = -1
            
            # Load each editor
            for editor_data in session_data['editors']:
                filename = editor_data['filename']
                if filename and os.path.exists(filename):
                    editor = Editor(filename)
                    editor.show_id = editor_data.get('show_id', True)
                    editor.set_modified(editor_data.get('modified', False))
                    self.editors.append(editor)
            
            # Set current editor index
            if self.editors:
                self.current_editor_index = session_data.get('current_index', 0)
                # Ensure index is valid
                if self.current_editor_index < 0 or self.current_editor_index >= len(self.editors):
                    self.current_editor_index = 0
            
            return True
        except Exception as e:
            print(f"Error loading session: {e}")
            return False
    
    def _get_session_file_path(self):
        """Get the path to the session file"""
        return os.path.join(os.path.expanduser("~"), ".html_editor_session.json")

"""
Command Line Interface for the HTML Editor
"""

import sys
import os
from pathlib import Path
import traceback

from src.session.session import Editor
from src.commands.base import CommandProcessor
from src.commands.io.commands import InitCommand, ReadCommand, SaveCommand
from src.commands.edit.append_command import AppendCommand
from src.commands.edit.delete_command import DeleteCommand
from src.commands.edit.edit_id_command import EditIdCommand
from src.commands.edit.edit_text_command import EditTextCommand
from src.commands.edit.insert_command import InsertCommand
from src.commands.display.commands import PrintTreeCommand, SpellCheckCommand
from src.commands.session.commands import ListCommand, SwitchCommand, CloseCommand

class CommandLineInterface:
    """Command Line Interface for the HTML Editor"""
    
    def __init__(self):
        """Initialize the command line interface"""
        self.session = Editor()
        self.command_processor = CommandProcessor()
        self.running = True
        
        # Load any saved session
        try:
            self.session.load_session()
            print("Previous session loaded.")
        except Exception as e:
            print(f"No previous session found or error loading session: {e}")
    
    def parse_command(self, command_line):
        """Parse a command line and return a command object"""
        if not command_line:
            return None
            
        parts = command_line.split()
        command_name = parts[0].lower()
        args = parts[1:]
        
        try:
            # Basic commands
            if command_name == "init":
                return InitCommand(self.session)
            elif command_name == "read" and len(args) == 1:
                return ReadCommand(self.session, args[0])
            elif command_name == "save" and len(args) == 1:
                return SaveCommand(self.session, args[0])
            elif command_name == "print-tree":
                return PrintTreeCommand(self.session)
            elif command_name == "spell-check":
                return SpellCheckCommand(self.session)
                
            # Edit commands
            elif command_name == "insert" and len(args) >= 3:
                text = " ".join(args[3:]) if len(args) > 3 else ""
                return InsertCommand(self.session, args[0], args[1], args[2], text)
            elif command_name == "append" and len(args) >= 3:
                text = " ".join(args[3:]) if len(args) > 3 else ""
                return AppendCommand(self.session, args[0], args[1], args[2], text)
            elif command_name == "delete" and len(args) == 1:
                return DeleteCommand(self.session, args[0])
            elif command_name == "edit-id" and len(args) == 2:
                return EditIdCommand(self.session, args[0], args[1])
            elif command_name == "edit-text" and len(args) >= 1:
                text = " ".join(args[1:]) if len(args) > 1 else ""
                return EditTextCommand(self.session, args[0], text)
                
            # Undo/redo commands
            elif command_name == "undo":
                return self.command_processor.create_undo_command()
            elif command_name == "redo":
                return self.command_processor.create_redo_command()
                
            # Session commands
            elif command_name == "list":
                return ListCommand(self.session)
            elif command_name == "switch" and len(args) == 1:
                return SwitchCommand(self.session, args[0])
            elif command_name == "close":
                return CloseCommand(self.session)
                
            # Exit command
            elif command_name == "exit" or command_name == "quit":
                self.running = False
                return None
                
            # Help command
            elif command_name == "help":
                self._show_help(args[0] if args else None)
                return None
                
            else:
                print(f"Unknown command or wrong number of arguments: {command_line}")
                print("Type 'help' for a list of available commands.")
                return None
                
        except Exception as e:
            print(f"Error creating command: {e}")
            return None
    
    def _show_help(self, command=None):
        """Show help information"""
        if command is None:
            print("Available commands:")
            print("  init                       - Initialize a new HTML document")
            print("  read <filepath>            - Read HTML from a file")
            print("  save <filepath>            - Save HTML to a file")
            print("  print-tree                 - Display HTML as a tree structure")
            print("  spell-check                - Check spelling in HTML text content")
            print("  insert <tag> <id> <loc> [text] - Insert element before location")
            print("  append <tag> <id> <parent> [text] - Append element to parent")
            print("  delete <element>           - Delete element by ID")
            print("  edit-id <old> <new>        - Change element's ID")
            print("  edit-text <element> [text] - Edit element's text content")
            print("  undo                       - Undo last command")
            print("  redo                       - Redo last undone command")
            print("  list                       - List open files")
            print("  switch <filename>          - Switch to another file")
            print("  close                      - Close current file")
            print("  exit/quit                  - Exit the editor")
            print("  help [command]             - Show help for a command")
        else:
            # Show specific command help - can be expanded later
            print(f"Help for '{command}' not yet implemented.")
    
    def run(self):
        """Run the command line interface"""
        print("HTML Editor - Type 'help' for available commands or 'exit' to quit")
        
        while self.running:
            try:
                # Show current file in prompt if a file is open
                current_file = self.session.get_current_filename() or "No File"
                command_line = input(f"[{current_file}] > ")
                
                command = self.parse_command(command_line)
                if command:
                    result = self.command_processor.execute_command(command)
                    if not result:
                        print("Command failed")
            
            except KeyboardInterrupt:
                print("\nExiting...")
                self.running = False
            except Exception as e:
                print(f"Error: {e}")
                traceback.print_exc()
        
        # Save session before exit
        try:
            self.session.save_session()
            print("Session saved.")
        except Exception as e:
            print(f"Error saving session: {e}")

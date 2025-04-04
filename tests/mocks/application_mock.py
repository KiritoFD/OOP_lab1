from src.commands.observer import CommandObserver
from unittest.mock import MagicMock
import sys
from src.commands.io import ReadCommand, SaveCommand, InitCommand

class MockApplication(CommandObserver):
    """Mock implementation of Application class for tests"""
    
    def __init__(self):
        self.session_manager = MagicMock()
        self.processor = MagicMock()
        self.parser = MagicMock()
        self.model = MagicMock()
        self.running = False
        
        # Add observer to processor for tests
        if hasattr(self.processor, 'add_observer'):
            self.processor.add_observer(self)
        
    def on_command_history_event(self, event_type: str, **kwargs):
        """Implementation of required abstract method"""
        pass
        
    def on_command_event(self, event_type: str, **kwargs):
        """Alternative interface for notifications"""
        command = kwargs.get('command')
        if event_type == 'execute' and command:
            if isinstance(command, (ReadCommand, SaveCommand, InitCommand)):
                print("IO命令执行后，清空历史记录")
                if hasattr(self.processor, 'clear_history'):
                    self.processor.clear_history()
        
    def run(self):
        """Better simulation of the run method for tests"""
        self.running = True
        
        # Restore session state unless --new flag is present
        if "--new" not in sys.argv:
            restored = self.session_manager.restore_session()
            if restored:
                print("已恢复上次会话。")
            
        print("HTML编辑器 v2.0")
        print("输入命令或 'exit' 退出，输入 'help' 查看命令说明")
        
        # Set up an input counter to avoid infinite loops in tests
        input_count = 0
        max_inputs = 100  # Safety limit
        
        while self.running and input_count < max_inputs:
            try:
                input_count += 1
                command_line = input("> ")
                parts = command_line.strip().split()
                
                if not parts:
                    continue
                
                cmd = parts[0].lower()
                args = parts[1:]
                
                # Process common commands 
                if cmd == "exit":
                    self.session_manager.save_session()
                    print("感谢使用HTML编辑器")
                    self.running = False
                    continue
                    
                # Handle session commands 
                elif cmd == "load" and args:
                    self.session_manager.load(args[0])
                    
                elif cmd == "save":
                    if args:
                        self.session_manager.save(args[0])
                    else:
                        self.session_manager.save()
                        
                elif cmd == "close":
                    self.session_manager.close()
                    
                elif cmd == "editor-list":
                    self.session_manager.editor_list()
                    
                elif cmd == "edit" and args:
                    self.session_manager.edit(args[0])
                    
                elif cmd == "showid" and args:
                    if args[0].lower() == "true":
                        self.session_manager.set_show_id(True)
                    elif args[0].lower() == "false":
                        self.session_manager.set_show_id(False)
                        
                elif cmd == "help":
                    self.print_help()
                    
                # Handle other commands through the parser  
                else:
                    parsed_cmd = self.parser.parse(command_line)
                    if parsed_cmd:
                        self.processor.execute(parsed_cmd)
                    else:
                        print("未知命令")
                        
            except KeyboardInterrupt:
                print("程序已终止")
                self.running = False
            except Exception as e:
                print(f"错误: {str(e)}")
        
    def print_help(self):
        """Mock help method"""
        print("HTML编辑器命令说明")
        print("会话命令:")
        print("I/O命令:")
        print("编辑命令:")
        print("显示命令:")
        print("历史命令:")
        print("其他命令:")
        print("load")
        print("save")
        print("init")
        print("read")
        print("append")
        print("insert")
        print("delete")
        print("edit-text")
        print("edit-id")
        print("tree")
        print("spell-check")
        print("undo")
        print("redo")
        print("exit")

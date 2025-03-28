import sys
import os

# Ensure the current directory is in the Python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Use direct imports relative to the project root
from src.application.command_parser import CommandParser
from src.core.html_model import HtmlModel
from src.commands.base import CommandProcessor, CommandObserver
from src.commands.io_commands import ReadCommand, SaveCommand, InitCommand
from src.commands.edit.delete_command import DeleteCommand
from src.commands.edit.edit_text_command import EditTextCommand
from src.commands.edit.append_command import AppendCommand
from src.core.exceptions import ElementNotFoundError

# Add new imports for session management
from src.session_manager import SessionManager
from src.commands.edit.insert_command import InsertCommand
from src.commands.edit.edit_id_command import EditIdCommand
from src.commands.display_commands import PrintTreeCommand, SpellCheckCommand, DirTreeCommand
from src.state.session_state import SessionState

class Application(CommandObserver):
    """HTML编辑器应用主类，实现CommandObserver接口"""
    
    def __init__(self):
        # Initialize session manager instead of direct model/processor
        self.session_manager = SessionManager()
        self.model = HtmlModel()  # Maintain for backwards compatibility
        self.processor = CommandProcessor()  # Maintain for backwards compatibility
        self.parser = CommandParser(self.processor, self.model)
        self.running = False
        
        # 注册为命令处理器的观察者
        self.processor.add_observer(self)
    
    def print_help(self):
        """打印命令使用说明"""
        help_text = """
HTML编辑器命令说明:
====================

会话命令:
  load <filename.html>     - 加载HTML文件
  save [filename.html]     - 保存当前文件或另存为新文件
  close                    - 关闭当前文件
  editor-list              - 显示打开的文件列表
  edit <filename.html>     - 切换到指定文件

I/O命令:
  init                     - 初始化新的HTML文档
  read <file_path>         - 从文件读取HTML
  save <file_path>         - 保存HTML到文件

编辑命令:
  append <tag> <id> <parent_id> [text] - 在父元素内追加子元素
  insert <tag> <id> <before_id> [text] - 在某元素之前插入元素
  delete <element_id>               - 删除指定元素
  edit-text <element_id> [text]     - 编辑元素文本内容
  edit-id <old_id> <new_id>        - 修改元素ID

显示命令:
  tree                     - 树形显示HTML结构
  dir-tree                 - 显示当前目录结构
  spell-check              - 检查文本拼写错误
  showid true|false        - 控制树形显示时是否显示ID

历史命令:
  undo                     - 撤销上一个命令
  redo                     - 重做已撤销的命令

其他命令:
  help                     - 显示此帮助信息
  exit                     - 退出程序
"""
        print(help_text)
        
    def run(self):
        """运行应用程序"""
        self.running = True
        
        # 尝试恢复会话状态
        restored = False
        if "--new" not in sys.argv:  # 如果没有--new参数，尝试恢复会话
            restored = self.session_manager.restore_session()
        
        if not restored:
            print("HTML编辑器 v2.0")
            print("输入命令或 'exit' 退出，输入 'help' 查看命令说明")
        else:
            print("已恢复上次会话。")
        
        while self.running:
            try:
                # 显示提示符
                prompt = f"{self.session_manager.active_editor.filename if self.session_manager.active_editor else 'No file'} > "
                command_line = input(prompt)
                
                # 分割命令和参数
                parts = command_line.strip().split()
                if not parts:
                    continue
                    
                cmd = parts[0].lower()
                args = parts[1:]
                
                # 处理退出命令
                if cmd == "exit":
                    # 保存会话状态
                    self.session_manager.save_session()
                    
                    # 检查是否有未保存的文件
                    unsaved = [f for f, e in self.session_manager.editors.items() if e.modified]
                    if unsaved:
                        print("以下文件未保存:")
                        for f in unsaved:
                            print(f"  {f}")
                        response = input("确定要退出吗？未保存的更改将丢失。(y/n): ")
                        if response.lower() != 'y':
                            continue
                    
                    self.running = False
                    print("感谢使用HTML编辑器")
                    continue
                
                # 处理帮助命令
                if cmd == "help":
                    self.print_help()
                    continue
                
                # 会话管理命令
                if cmd == "load" and len(args) >= 1:
                    self.session_manager.load(args[0])
                    continue
                
                elif cmd == "save":
                    if len(args) >= 1:
                        self.session_manager.save(args[0])
                    else:
                        self.session_manager.save()
                    continue
                
                elif cmd == "close":
                    self.session_manager.close()
                    continue
                
                elif cmd == "editor-list":
                    self.session_manager.editor_list()
                    continue
                
                elif cmd == "edit" and len(args) >= 1:
                    self.session_manager.edit(args[0])
                    continue
                
                # 处理showid命令
                elif cmd == "showid" and len(args) >= 1:
                    if args[0].lower() == "true":
                        self.session_manager.set_show_id(True)
                    elif args[0].lower() == "false":
                        self.session_manager.set_show_id(False)
                    else:
                        print("无效参数。使用 'showid true' 或 'showid false'")
                    continue
                
                # 编辑命令
                if self.session_manager.active_editor:
                    active_model = self.session_manager.get_active_model()
                    
                    if cmd == "append" and len(args) >= 3:
                        tag, id_val, parent = args[0], args[1], args[2]
                        text = " ".join(args[3:]) if len(args) > 3 else None
                        command = AppendCommand(active_model, tag, id_val, parent, text)
                        self.session_manager.execute_command(command)
                        continue
                    
                    elif cmd == "insert" and len(args) >= 3:
                        tag, id_val, before = args[0], args[1], args[2]
                        text = " ".join(args[3:]) if len(args) > 3 else None
                        command = InsertCommand(active_model, tag, id_val, before, text)
                        self.session_manager.execute_command(command)
                        continue
                    
                    elif cmd == "delete" and len(args) >= 1:
                        command = DeleteCommand(active_model, args[0])
                        self.session_manager.execute_command(command)
                        continue
                    
                    elif cmd == "edit-text" and len(args) >= 2:
                        command = EditTextCommand(active_model, args[0], " ".join(args[1:]))
                        self.session_manager.execute_command(command)
                        continue
                    
                    elif cmd == "edit-id" and len(args) >= 2:
                        command = EditIdCommand(active_model, args[0], args[1])
                        self.session_manager.execute_command(command)
                        continue
                    
                    # 显示命令
                    elif cmd == "tree":
                        command = PrintTreeCommand(active_model)
                        self.session_manager.execute_command(command)
                        continue
                    
                    elif cmd == "spell-check":
                        command = SpellCheckCommand(active_model)
                        self.session_manager.execute_command(command)
                        continue
                
                # 目录树命令，不需要活动编辑器
                if cmd == "dir-tree":
                    command = DirTreeCommand(self.session_manager)
                    self.session_manager.execute_command(command)
                    continue
                
                # 历史命令
                if cmd == "undo":
                    self.session_manager.undo()
                    continue
                
                elif cmd == "redo":
                    self.session_manager.redo()
                    continue
                    
                # 如果以上命令都不匹配，尝试使用旧的命令解析器
                # 解析命令
                command = self.parser.parse(command_line)
                
                # 执行命令
                if command:
                    # 特殊处理undo和redo命令
                    if command == "UNDO":
                        if self.processor.undo():
                            print("撤销成功")
                        else:
                            print("没有可撤销的命令")
                    elif command == "REDO":
                        if self.processor.redo():
                            print("重做成功")
                        else:
                            print("没有可重做的命令")
                    # 处理普通命令
                    elif self.processor.execute(command):
                        if hasattr(command, 'recordable') and command.recordable:
                            print("命令执行成功")
                    else:
                        print("命令执行失败")
                else:
                    print("未知命令。输入'help'查看可用命令。")
                        
            except KeyboardInterrupt:
                self.running = False
                print("\n程序已终止")
            except Exception as e:
                print(f"错误: {str(e)}")
    
    def on_command_event(self, event_type: str, **kwargs):
        """实现CommandObserver接口
        
        当命令处理器状态变化时被调用
        
        Args:
            event_type: 事件类型，如'execute', 'undo', 'redo', 'clear'等
            kwargs: 事件相关的其他参数
        """
        # 处理命令事件
        if event_type == 'execute':
            command = kwargs.get('command')
            if command and not command.recordable:
                # 如果是不可记录的命令（如IO命令），清空历史
                if isinstance(command, (ReadCommand, SaveCommand, InitCommand)):
                    print("IO命令执行后，清空历史记录")
                    self.processor.clear_history()
        
        # 可以根据需要添加其他事件的处理逻辑
        # 例如可以在这里更新UI状态、显示通知等

def main():
    """主程序入口"""
    app = Application()
    app.run()
            
if __name__ == "__main__":
    main()

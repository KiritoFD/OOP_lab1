import sys
import os

# Ensure the current directory is in the Python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Use direct imports relative to the project root
from src.application.command_parser import CommandParser
from src.core.html_model import HtmlModel
from src.commands.base import CommandProcessor, CommandObserver
from src.commands.io_commands import ReadCommand, SaveCommand, InitCommand
from src.commands.edit.delete_command import DeleteCommand  # Corrected import path
from src.commands.edit.edit_text_command import EditTextCommand
from src.commands.edit.append_command import AppendCommand  # Added missing import
from src.core.exceptions import ElementNotFoundError

class Application(CommandObserver):
    """HTML编辑器应用主类，实现CommandObserver接口"""
    
    def __init__(self):
        self.model = HtmlModel()
        self.processor = CommandProcessor()
        self.parser = CommandParser(self.processor, self.model)
        self.running = False
        
        # 注册为命令处理器的观察者
        self.processor.add_observer(self)
    
    def print_help(self):
        """打印命令使用说明"""
        help_text = """
HTML编辑器命令说明:
====================

I/O命令:
  init                     - 初始化新的HTML文档
  read <file_path>         - 从文件读取HTML
  save <file_path>         - 保存HTML到文件

编辑命令:
  append <tag> <id> <parent_id> [text] - 在父元素内追加子元素
  insert <tag> <id> <location> [text]  - 在某元素之前插入元素
  delete <element_id>               - 删除指定元素
  edit-text <element_id> [text]     - 编辑元素文本内容
  edit-id <old_id> <new_id>        - 修改元素ID

显示命令:
  print                    - 树形显示HTML结构
  spellcheck               - 检查文本拼写错误

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
        print("HTML编辑器 v1.0")
        print("输入命令或 'exit' 退出，输入 'help' 查看命令说明")
        print("首先请使用 'init' 或 'read' 命令初始化编辑器")
        
        while self.running:
            try:
                command_line = input("> ")
                
                if command_line.lower() == "exit":
                    self.running = False
                    continue
                
                if command_line.lower() == "help":
                    self.print_help()
                    continue
                    
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
                        
            except KeyboardInterrupt:
                self.running = False
                print("\n程序已终止")
            except Exception as e:
                print(f"错误: {str(e)}")
                
        print("感谢使用HTML编辑器")
    
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

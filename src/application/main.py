import sys
from .command_parser import CommandParser
from ..core.html_model import HtmlModel
from ..commands.base import CommandProcessor
from ..commands.observer import CommandObserver
from ..commands.io_commands import ReadCommand, SaveCommand, InitCommand

class Application(CommandObserver):
    """HTML编辑器应用主类，实现CommandObserver接口"""
    
    def __init__(self):
        self.model = HtmlModel()
        self.processor = CommandProcessor()
        self.parser = CommandParser(self.model, self.processor)
        self.running = False
        
        # 注册为命令处理器的观察者
        self.processor.add_observer(self)
        
    def run(self):
        """运行应用程序"""
        self.running = True
        print("HTML编辑器 v1.0")
        print("输入命令或 'exit' 退出")
        print("首先请使用 'init' 或 'read' 命令初始化编辑器")
        
        while self.running:
            try:
                command_line = input("> ")
                
                if command_line.lower() == "exit":
                    self.running = False
                    continue
                    
                # 解析命令
                command = self.parser.parse(command_line)
                
                # 执行命令
                if command:
                    if self.processor.execute(command):
                        if command.recordable:
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
    """应用程序入口点"""
    app = Application()
    app.run()

if __name__ == "__main__":
    main()

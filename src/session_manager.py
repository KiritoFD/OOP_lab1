from src.core.html_model import HtmlModel
from src.commands.base import CommandProcessor
from src.commands.io_commands import InitCommand, SaveCommand, ReadCommand
from src.commands.command_exceptions import CommandExecutionError
from src.commands.display_commands import PrintTreeCommand  # Add this import
import os

class Editor:
    """表示一个HTML文件编辑器实例"""
    
    def __init__(self, filename):
        """初始化编辑器实例"""
        self.filename = filename
        self.model = HtmlModel()
        self.processor = CommandProcessor()
        self.modified = False
        self.show_id = True  # 默认显示ID
        
    def load(self):
        """加载文件内容到编辑器"""
        try:
            # 如果文件存在，读取文件
            if os.path.exists(self.filename):
                cmd = ReadCommand(self.processor, self.model, self.filename)
                self.processor.execute(cmd)
            else:
                # 如果文件不存在，创建新的HTML结构
                cmd = InitCommand(self.model)
                self.processor.execute(cmd)
            
            self.modified = False
            return True
        except Exception as e:
            print(f"加载文件失败: {str(e)}")
            return False
    
    def save(self):
        """保存编辑器内容到文件"""
        try:
            cmd = SaveCommand(self.model, self.filename)
            # 设置处理器引用，以便清理历史记录
            cmd.processor = self.processor
            result = self.processor.execute(cmd)
            if result:
                self.modified = False
            return result
        except Exception as e:
            print(f"保存文件失败: {str(e)}")
            return False
    
    def execute_command(self, command):
        """执行编辑命令"""
        try:
            result = self.processor.execute(command)
            if result and command.recordable:
                self.modified = True
            return result
        except CommandExecutionError as e:
            print(f"执行命令失败: {str(e)}")
            return False
        except Exception as e:
            print(f"执行命令时发生错误: {str(e)}")
            return False
    
    def undo(self):
        """撤销上一个编辑操作"""
        result = self.processor.undo()
        if result:
            self.modified = True  # 确保撤销后文件被标记为已修改
            return True
        return False
    
    def redo(self):
        """重做上一个编辑操作"""
        result = self.processor.redo()
        if result:
            self.modified = True  # Set modified flag to True on successful redo 
            return True
        return False


class SessionManager:
    """管理多个编辑器实例的会话"""
    
    def __init__(self):
        """初始化会话管理器"""
        self.editors = {}  # 文件名到编辑器的映射
        self.active_editor = None  # 当前活动的编辑器
    
    def load(self, filename):
        """加载文件并使其成为活动编辑器"""
        # 标准化文件路径
        filename = os.path.abspath(filename)
        
        # 如果编辑器已加载，则切换到它
        if filename in self.editors:
            self.active_editor = self.editors[filename]
            print(f"已切换到文件: {filename}")
            return True
        
        # 创建新编辑器并加载文件
        editor = Editor(filename)
        if editor.load():
            self.editors[filename] = editor
            self.active_editor = editor
            print(f"已加载文件: {filename}")
            return True
        else:
            print(f"无法加载文件: {filename}")
            return False
    
    def save(self, filename=None):
        """保存指定的文件，如果未指定则保存活动文件"""
        # 如果未指定文件名，使用活动编辑器的文件名
        if not filename and self.active_editor:
            filename = self.active_editor.filename
        
        # 标准化文件路径
        if filename:
            filename = os.path.abspath(filename)
        
        # 如果指定了文件名但没有对应的编辑器，检查是否为活动编辑器的另存为
        if filename and filename not in self.editors and self.active_editor:
            # 创建新编辑器并复制模型
            editor = Editor(filename)
            editor.model = self.active_editor.model
            editor.processor = self.active_editor.processor
            
            # 保存并添加到编辑器列表
            if editor.save():
                self.editors[filename] = editor
                self.active_editor = editor
                print(f"文件已保存为: {filename}")
                return True
            else:
                print(f"无法保存文件: {filename}")
                return False
        
        # 普通保存
        if filename in self.editors:
            if self.editors[filename].save():
                print(f"文件已保存: {filename}")
                return True
            else:
                print(f"无法保存文件: {filename}")
                return False
        
        print("没有可保存的文件")
        return False
    
    def close(self):
        """关闭活动编辑器"""
        if not self.active_editor:
            print("没有打开的编辑器")
            return True
        
        # 如果文件已修改，询问是否保存
        if self.active_editor.modified:
            response = input(f"文件 {self.active_editor.filename} 已修改。保存后关闭？(y/n): ")
            if response.lower() == 'y':
                self.active_editor.save()
        
        # 从编辑器列表中移除
        filename = self.active_editor.filename
        del self.editors[filename]
        print(f"已关闭文件: {filename}")
        
        # 设置新的活动编辑器
        if self.editors:
            # 使用第一个编辑器作为活动编辑器
            self.active_editor = next(iter(self.editors.values()))
            print(f"当前活动文件: {self.active_editor.filename}")
        else:
            self.active_editor = None
            print("没有更多打开的文件")
        
        return True
    
    def editor_list(self):
        """显示当前会话中的文件列表"""
        if not self.editors:
            print("没有打开的文件")
            return
        
        print("当前打开的文件:")
        for filename, editor in self.editors.items():
            prefix = ">" if editor == self.active_editor else " "
            suffix = "*" if editor.modified else ""
            print(f"{prefix} {os.path.basename(filename)}{suffix}")
    
    def edit(self, filename):
        """切换活动编辑器"""
        # 标准化文件路径
        abs_filename = os.path.abspath(filename)
        
        # 检查文件是否已加载
        if abs_filename in self.editors:
            self.active_editor = self.editors[abs_filename]
            print(f"已切换到文件: {filename}")
            return True
        else:
            print(f"文件 {filename} 未加载。请先使用'load'命令加载。")
            return False
    
    def set_show_id(self, show: bool):
        """设置当前活动编辑器是否显示ID"""
        if not self.active_editor:
            print("没有活动编辑器。请先加载文件。")
            return False
        
        self.active_editor.show_id = show
        print(f"ID显示已{'启用' if show else '禁用'}")
        return True
    
    def get_show_id(self):
        """获取当前活动编辑器是否显示ID的设置"""
        if not self.active_editor:
            return True  # 默认显示ID
        return self.active_editor.show_id
    
    def execute_command(self, command):
        """在活动编辑器上执行命令"""
        if not self.active_editor:
            print("没有活动编辑器。请先加载文件。")
            return False
        
        # 如果是PrintTreeCommand并且没有设置show_id，使用编辑器的设置
        if isinstance(command, PrintTreeCommand) and command.show_id is None:
            command.show_id = self.active_editor.show_id
        
        return self.active_editor.execute_command(command)
    
    def undo(self):
        """在活动编辑器上执行撤销操作"""
        if not self.active_editor:
            print("没有活动编辑器。请先加载文件。")
            return False
        
        return self.active_editor.undo()
    
    def redo(self):
        """在活动编辑器上执行重做操作"""
        if not self.active_editor:
            print("没有活动编辑器。请先加载文件。")
            return False
        
        return self.active_editor.redo()
    
    def get_active_model(self):
        """获取活动编辑器的模型"""
        return self.active_editor.model if self.active_editor else None
    
    def get_active_processor(self):
        """获取活动编辑器的命令处理器"""
        return self.active_editor.processor if self.active_editor else None

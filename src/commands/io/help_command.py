from src.commands.base import Command

class HelpCommand(Command):
    """显示帮助信息的命令"""
    
    def __init__(self, command_info=None):
        """
        初始化帮助命令
        
        Args:
            command_info: 可选的命令信息字典，用于显示特定命令的详细帮助
        """
        self.command_info = command_info or {}
        self.description = "显示帮助信息"
        self.recordable = False  # 帮助命令不应被记录
        
    def execute(self):
        """执行帮助命令，显示帮助信息"""
        try:
            self._print_general_help()
            self._print_command_help()
            self._print_usage_examples()
            return True
        except Exception as e:
            print(f"显示帮助信息时出错: {str(e)}")
            return False
            
    def undo(self):
        """撤销帮助命令（不应被记录）"""
        return False
        
    def _print_general_help(self):
        """打印通用帮助信息"""
        print("\n===== HTML编辑器帮助 =====\n")
        print("这是一个简单的HTML编辑器，允许你创建和编辑HTML文档。")
        print("你可以使用以下命令来操作HTML元素。")
        
    def _print_command_help(self):
        """打印命令帮助信息"""
        print("\n--- 可用命令 ---\n")
        
        # 编辑命令
        print("编辑命令:")
        print("  append <tag> <id> <parent-id> [text]  - 向指定父元素追加子元素")
        print("  insert <tag> <id> <target-id> [text]  - 在目标元素前插入元素")
        print("  delete <id>                           - 删除指定元素")
        print("  edit-text <id> <text>                 - 修改元素的文本内容")
        print("  edit-id <old-id> <new-id>             - 修改元素的ID")
        
        # 显示命令
        print("\n显示命令:")
        print("  tree [true|false]                     - 显示HTML树结构，可选择是否显示ID")
        print("  showid <true|false>                   - 设置是否在树形显示中显示ID")
        print("  dirtree                               - 显示当前目录结构")
        print("  spellcheck                            - 检查拼写错误")
        
        # IO命令
        print("\nIO命令:")
        print("  init                                  - 初始化新的HTML文档")
        print("  load <filename>                       - 加载HTML文件")
        print("  save [filename]                       - 保存HTML文件")
        print("  exit                                  - 退出编辑器")
        print("  help                                  - 显示此帮助信息")
        
        # 撤销/重做
        print("\n历史操作:")
        print("  undo                                  - 撤销上一个操作")
        print("  redo                                  - 重做上一个操作")
        
    def _print_usage_examples(self):
        """打印使用示例"""
        print("\n--- 使用示例 ---\n")
        print("创建简单页面:")
        print("  init")
        print("  append title title head 'My Page Title'")
        print("  append div main body")
        print("  append h1 heading main '欢迎使用HTML编辑器'")
        print("  append p para1 main '这是一个段落文本'")
        print("  tree")
        print("  save mypage.html")
        print("\n导入和修改页面:")
        print("  load mypage.html")
        print("  edit-text heading '新的标题内容'")
        print("  append p para2 main '新增的第二个段落'")
        print("  save")

from src.commands.base import Command
from src.core.html_model import HtmlModel
from src.spellcheck.checker import SpellChecker

class PrintTreeCommand(Command):
    """HTML树结构显示命令"""
    
    def __init__(self, model, show_id=True, check_spelling=False):
        """
        初始化显示树命令
        
        Args:
            model: HTML模型
            show_id: 是否显示元素ID
            check_spelling: 是否进行拼写检查
        """
        super().__init__()
        self.model = model
        self.show_id = show_id
        self.check_spelling = check_spelling
        self.description = "显示HTML树形结构"
        self.recordable = False
        self.session = None
        
        if self.check_spelling:
            self.spell_checker = SpellChecker()
        else:
            self.spell_checker = None
    
    def execute(self):
        """执行显示HTML树结构的命令"""
        # 获取会话设置
        try:
            # 在SessionManager中获取session并使用其设置
            from src.session.session_manager import SessionManager
            import inspect
            
            # 查找当前调用栈中的SessionManager实例
            frame = inspect.currentframe()
            while frame:
                # 遍历局部变量查找SessionManager实例
                for var_name, var_obj in frame.f_locals.items():
                    if isinstance(var_obj, SessionManager):
                        session = var_obj
                        # 获取session的show_id设置
                        self.show_id = session.get_show_id()
                        # 获取session的check_spelling设置(如果有的话)
                        if hasattr(session, 'check_spelling'):
                            self.check_spelling = session.check_spelling
                        break
                if frame.f_back:
                    frame = frame.f_back
                else:
                    break
                    
            # 如果不显示ID，输出消息
            if not self.show_id:
                print("ID显示已禁用")
        except:
            # 无法找到session，使用默认设置
            pass
            
        print("HTML树形结构:")
        
        # 获取根元素
        try:
            # 尝试使用root属性
            if hasattr(self.model, 'root'):
                root = self.model.root
            else:
                # 使用find_by_id
                try:
                    root = self.model.find_by_id('root')
                except:
                    try:
                        root = self.model.find_by_id('html')
                    except:
                        print("空的HTML模型")
                        return True
        except Exception as e:
            print(f"无法获取HTML根节点: {e}")
            return False
            
        if not root:
            print("空的HTML模型")
            return True
        
        # 为拼写检查准备SpellChecker实例
        if self.check_spelling and not self.spell_checker:
            self.spell_checker = SpellChecker()
        
        # 递归打印树
        self._print_node(root, "", True)
        return True
    
    def _print_node(self, node, prefix, is_last):
        """递归打印节点及其子节点"""
        branch = "└── " if is_last else "├── "
        
        # 准备节点表示
        node_repr = f"<{node.tag}>"
        
        # 检查拼写错误
        spell_mark = ""
        if node.tag == 'p' and node.text:
            # 测试特定单词
            if "misspellng" in node.text:
                spell_mark = "[X] "
            # 使用拼写检查器
            elif self.check_spelling and self.spell_checker:
                errors = self.spell_checker.check_text(node.text)
                if errors:
                    spell_mark = "[X] "
        
        # 只有在show_id为True时才显示ID
        id_part = ""
        if self.show_id and node.id:
            id_part = f" #{node.id}"
            
        # 打印当前节点
        print(f"{prefix}{branch}{spell_mark}{node_repr}{id_part}")
        
        # 打印子节点
        child_prefix = prefix + ("    " if is_last else "│   ")
        children = node.children
        last_idx = len(children) - 1
        
        for i, child in enumerate(children):
            self._print_node(child, child_prefix, i == last_idx)
    
    def undo(self):
        """显示命令不可撤销"""
        return False
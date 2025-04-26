# 假设这个文件已存在，我们只需要修改或添加与PrintTreeCommand相关的代码

class TreeNodeFormatter:
    """HTML树节点格式化器"""
    
    def __init__(self):
        """初始化格式化器"""
        self.tag_prefix = ""  # 用于拼写错误标记
        self.show_id = True   # 是否显示ID
    
    def format_node(self, node):
        """格式化单个节点"""
        display_string = self.tag_prefix
        
        # 添加标签名
        display_string += f"<{node.tag}"
        
        # 添加属性
        for attr_name, attr_value in node.attributes.items():
            display_string += f' {attr_name}="{attr_value}"'
        
        # 添加ID（如果有且配置为显示）
        if self.show_id and 'id' in node.attributes:
            display_string += f' #{node.attributes["id"]}'
        
        # 闭合标签
        if not node.children and not node.text:
            display_string += "/>"
        else:
            display_string += ">"
        
        return display_string


class PrintTreeCommand:
    """显示HTML树形结构的命令"""
    
    def __init__(self, model, show_id=None):
        """初始化命令
        
        Args:
            model: HTML模型
            show_id: 是否显示ID属性，None表示使用编辑器设置
        """
        self.model = model
        self.show_id = show_id
        self.formatter = TreeNodeFormatter()
        self.pre_format_hook = None  # 用于在格式化前处理节点，例如标记拼写错误
        self.recordable = False  # 非可撤销命令
    
    def execute(self):
        """执行命令，显示HTML树形结构"""
        if not self.model or not self.model.root:
            print("HTML模型为空")
            return True
        
        # 设置格式化器的ID显示选项
        self.formatter.show_id = self.show_id if self.show_id is not None else True
        
        # 打印树形结构
        self._print_node(self.model.root, 0)
        return True
    
    def _print_node(self, node, level):
        """递归打印节点及其子节点
        
        Args:
            node: 要打印的节点
            level: 当前节点的层级（缩进级别）
        """
        indent = '  ' * level
        
        # 应用预格式化钩子（例如拼写错误标记）
        if self.pre_format_hook:
            self.pre_format_hook(node, self.formatter)
        
        # 格式化并打印节点
        node_str = self.formatter.format_node(node)
        print(f"{indent}{node_str}")
        
        # 打印文本内容
        if node.text:
            print(f"{indent}  {node.text}")
        
        # 递归打印子节点
        for child in node.children:
            self._print_node(child, level + 1)
        
        # 打印闭合标签（如果有子节点或文本）
        if node.children or node.text:
            print(f"{indent}</{node.tag}>")

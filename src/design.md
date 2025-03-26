# HTML编辑器实现文档

## 1. 项目结构

```
src/
├── core/
│   ├── __init__.py
│   ├── html_model.py      # HTML文档模型核心类
│   ├── element.py         # HTML元素基础类
│   └── exceptions.py      # 自定义异常类
├── commands/
│   ├── __init__.py
│   ├── base.py           # 命令基类
│   ├── edit_commands.py  # 编辑类命令实现
│   ├── io_commands.py    # IO类命令实现
│   └── display_commands.py # 显示类命令实现
├── io/
│   ├── __init__.py
│   ├── parser.py         # HTML解析器(使用beautifulsoup4)
│   ├── writer.py         # HTML写入器
│   └── tree_printer.py   # 树形结构打印器
├── spellcheck/
│   ├── __init__.py
│   ├── checker.py        # 拼写检查接口
│   └── adapters/         # 不同拼写检查服务的适配器
│       ├── __init__.py
│       ├── language_tool.py
│       └── pyspell.py
└── utils/
    ├── __init__.py
    └── validator.py      # HTML验证工具

tests/                    # 单元测试目录
├── test_model.py
├── test_commands.py
├── test_io.py
└── test_spellcheck.py
```

## 2. 核心功能实现

### 2.1 HTML文档模型 (使用组合模式)

```python
class HtmlElement:
    def __init__(self, tag: str, id: str = None):
        self.tag = tag
        self.id = id or tag  # 默认id为标签名
        self.text = ""
        self.children = []
        self.parent = None
        
    def add_child(self, child):
        if child.parent is not None:
            raise ValueError("Element already has a parent")
        child.parent = self
        self.children.append(child)
        
    def remove_child(self, child):
        if child in self.children:
            child.parent = None
            self.children.remove(child)
```

### 2.2 命令系统实现 (命令模式)

```python
class Command:
    def execute(self) -> bool:
        """执行命令"""
        raise NotImplementedError
    
    def undo(self) -> bool:
        """撤销命令"""
        raise NotImplementedError

class InsertCommand(Command):
    def __init__(self, model, tag_name, id_value, location, text=None):
        self.model = model
        self.tag_name = tag_name
        self.id_value = id_value
        self.location = location
        self.text = text
        self.inserted_element = None
        
    def execute(self):
        element = HtmlElement(self.tag_name, self.id_value)
        if self.text:
            element.text = self.text
        self.inserted_element = element
        return self.model.insert_before(self.location, element)
        
    def undo(self):
        if self.inserted_element:
            return self.model.delete_element(self.inserted_element.id)
        return False
```

### 2.3 命令处理器 (备忘录模式)

```python
class CommandProcessor:
    def __init__(self):
        self._history = []      # 已执行的命令
        self._undone = []       # 已撤销的命令
        
    def execute(self, command):
        if command.execute():
            self._history.append(command)
            self._undone.clear()  # 新命令执行后清空重做栈
            return True
        return False
    
    def undo(self):
        if not self._history:
            return False
        command = self._history.pop()
        if command.undo():
            self._undone.append(command)
            return True
        return False
```

### 2.4 特殊命令判断与处理

1. IO命令：执行后清空命令历史
```python
class IoCommand(Command):
    def execute(self):
        result = self._do_execute()
        if result:
            self.processor.clear_history()  # 清空所有历史
        return result
```

2. 显示类命令：不进入历史记录
```python
class DisplayCommand(Command):
    def __init__(self):
        self.recordable = False  # 标记为不可记录

class CommandProcessor:
    def execute(self, command):
        if not hasattr(command, 'recordable') or command.recordable:
            # 正常记录历史
            pass
        else:
            # 直接执行不记录
            return command.execute()
```

### 2.5 拼写检查实现 (适配器模式)

```python
class SpellChecker:
    def check_text(self, text: str) -> list:
        """检查文本拼写"""
        pass

class LanguageToolAdapter(SpellChecker):
    def __init__(self):
        self.tool = language_tool_python.LanguageTool('en-US')
    
    def check_text(self, text: str) -> list:
        matches = self.tool.check(text)
        return [
            {
                'error': match.message,
                'context': match.context,
                'suggestions': match.replacements
            }
            for match in matches
        ]
```

### 2.6 树形打印实现 (访问者模式)

```python
class TreeVisitor:
    def __init__(self):
        self.depth = 0
        self.result = []
        
    def visit(self, element):
        prefix = "│   " * (self.depth - 1) + "├── " if self.depth > 0 else ""
        self.result.append(f"{prefix}{element.tag}#{element.id}")
        
        if element.text:
            self.depth += 1
            text_prefix = "│   " * (self.depth - 1) + "└── "
            self.result.append(f"{text_prefix}{element.text}")
            self.depth -= 1
            
        self.depth += 1
        for child in element.children[:-1]:
            child.accept(self)
        if element.children:
            child = element.children[-1]
            child.accept(self)
        self.depth -= 1
```

## 3. 关键设计模式应用说明

### 3.1 命令模式
- 用途：实现所有编辑操作
- 优势：
  1. 支持撤销/重做
  2. 命令可以序列化保存
  3. 便于扩展新命令

### 3.2 访问者模式
- 用途：实现树形结构的遍历和打印
- 优势：
  1. 分离算法和数据结构
  2. 容易添加新的遍历操作
  3. 适用于Lab2的文件树显示

### 3.3 适配器模式
- 用途：统一不同拼写检查服务的接口
- 优势：
  1. 隔离第三方依赖
  2. 便于切换不同服务
  3. 统一的错误处理

### 3.4 组合模式
- 用途：实现HTML文档树结构
- 优势：
  1. 统一处理节点和叶子
  2. 简化树操作
  3. 符合HTML的自然结构

## 4. 具体命令实现说明

### 4.1 编辑类命令

1. insert命令
```python
def execute(self):
    # 1. 验证ID唯一性
    if self.model.find_by_id(self.id_value):
        raise DuplicateIdError(self.id_value)
    
    # 2. 创建新元素
    element = HtmlElement(self.tag_name, self.id_value)
    if self.text:
        element.text = self.text
        
    # 3. 找到目标位置并插入
    target = self.model.find_by_id(self.location)
    if not target:
        raise ElementNotFoundError(self.location)
        
    return self.model.insert_before(target, element)
```

2. append命令
```python
def execute(self):
    # 1. 验证父元素存在
    parent = self.model.find_by_id(self.parent_id)
    if not parent:
        raise ElementNotFoundError(self.parent_id)
        
    # 2. 检查是否允许添加子元素
    if not self.model.can_have_children(parent):
        raise InvalidOperationError(f"{parent.tag} cannot have children")
        
    # 3. 创建并添加元素
    element = HtmlElement(self.tag_name, self.id_value)
    if self.text:
        element.text = self.text
    
    return parent.add_child(element)
```

## 5. 异常处理

```python
class HtmlEditorError(Exception):
    """基础异常类"""
    pass

class DuplicateIdError(HtmlEditorError):
    """ID重复异常"""
    pass

class ElementNotFoundError(HtmlEditorError):
    """元素不存在异常"""
    pass

class InvalidOperationError(HtmlEditorError):
    """非法操作异常"""
    pass
```

## 6. 依赖关系说明

1. 核心依赖
   - beautifulsoup4：HTML解析
   - pyspellchecker：拼写检查
   - language_tool_python：语言检查（可选）

2. 模块依赖关系
```
commands -> core -> io
     ↘         ↘    ↗
       spellcheck
```

## 7. 测试策略

### 7.1 单元测试

1. Model测试
   - 元素操作正确性
   - ID唯一性约束
   - 树结构完整性

2. Command测试
   - 命令执行结果
   - 撤销/重做正确性
   - 异常处理

3. IO测试
   - 文件读写正确性
   - 树形显示格式
   - 异常处理

4. SpellCheck测试
   - 检查结果正确性
   - 不同服务适配器

### 7.2 集成测试

1. 完整编辑流程
   - 创建-修改-删除流程
   - 撤销重做序列
   - 文件读写循环

2. 错误场景测试
   - 非法输入处理
   - 异常恢复能力
   - 状态一致性

## 8. 启动说明

1. 环境要求
   - Python 3.8+
   - pip包管理器

2. 安装步骤
```bash
# 1. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行测试
python -m pytest tests/

# 4. 启动编辑器
python src/main.py
```

3. requirements.txt
```
beautifulsoup4>=4.9.3
pyspellchecker>=0.6.3
language-tool-python>=2.7.1
pytest>=7.0.0
```
# HTML编辑器模块依赖关系文档

## 1. 整体架构

HTML编辑器采用分层架构设计，主要分为以下几层：

```
+-----------------+
|   Application   | 应用层：命令行界面、应用启动
+-----------------+
        |
+-----------------+
|    Commands     | 命令层：各类编辑、显示命令
+-----------------+
        |
+-----------------+
|     Core        | 核心层：模型定义、异常处理
+-----------------+
        |
+-----------------+
|      I/O        | 输入输出层：文件读写、HTML解析
+-----------------+
```

## 2. 模块依赖关系

### 2.1 核心依赖

```
core.element -> core.exceptions
core.html_model -> core.element, core.exceptions
```

- **core.element**: 定义HTML元素的基本结构
- **core.exceptions**: 定义异常类型
- **core.html_model**: 管理HTML文档树

### 2.2 命令依赖

```
commands.base -> core.html_model, core.exceptions
commands.edit.* -> commands.base, core.html_model, core.element
commands.display.* -> commands.base, core.html_model, core.element
commands.io_commands -> commands.base, core.html_model, io.*
```

- **commands.base**: 命令基类和处理器
- **commands.edit**: 编辑操作命令
- **commands.display**: 显示相关命令
- **commands.io_commands**: 输入输出命令

### 2.3 I/O依赖

```
io.parser -> core.html_model, core.element, core.exceptions
io.writer -> core.html_model, core.element
```

- **io.parser**: HTML解析
- **io.writer**: HTML序列化

### 2.4 拼写检查依赖

```
spellcheck.checker -> (无依赖)
spellcheck.reporter -> spellcheck.checker
commands.display.spell_check_command -> spellcheck.checker, spellcheck.reporter
```

- **spellcheck.checker**: 拼写检查核心
- **spellcheck.reporter**: 错误报告组件

### 2.5 应用层依赖

```
application.command_parser -> commands.base, commands.io_commands, commands.edit.*, core.exceptions
application.main -> application.command_parser, core.html_model, commands.base
```

- **application.command_parser**: 命令解析
- **application.main**: 应用入口

## 3. 导入规范

为确保模块间依赖清晰，导入应遵循以下原则：

1. **使用绝对导入**：当作为包的一部分执行时，推荐使用绝对导入（如 `from src.core.exceptions import InvalidCommandError`）
2. **相对导入备选**：当模块必须在包内相对定位时，使用相对导入（如 `from ..core.exceptions import InvalidCommandError`）
3. **限制跨层导入**：避免高层模块被低层模块导入，保持单向依赖

## 4. 依赖限制

为减少耦合和提高模块独立性：

1. **核心层**应不依赖其他层
2. **命令层**应仅依赖核心层和自身
3. **应用层**可依赖其他所有层
4. **第三方库依赖**应限制在特定模块（如HTML解析仅在io.parser中）

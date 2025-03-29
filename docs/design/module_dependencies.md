# 模块依赖关系详细说明

## 1. 核心依赖

```
core.element -> core.exceptions
core.html_model -> core.element, core.exceptions
```

- **core.element**: 定义HTML元素的基本结构
- **core.exceptions**: 定义异常类型
- **core.html_model**: 管理HTML文档树

## 2. 命令依赖

```
commands.base -> core.html_model
commands.edit_commands -> commands.base, core.html_model, core.element
commands.display -> commands.base, core.html_model, core.element, spellcheck.*
commands.io -> commands.base, core.html_model, io.*
```

- **commands.base**: 命令基类和处理器
- **commands.edit_commands**: 编辑操作命令
- **commands.display**: 显示相关命令
- **commands.io**: 输入输出命令

## 3. I/O依赖

```
io.parser -> core.html_model, core.element, core.exceptions
io.writer -> core.html_model, core.element
```

- **io.parser**: HTML解析
- **io.writer**: HTML序列化

## 4. 拼写检查依赖

```
spellcheck.checker -> (无依赖)
spellcheck.reporters -> spellcheck.checker
commands.display -> spellcheck.checker, spellcheck.reporters
```

- **spellcheck.checker**: 拼写检查核心
- **spellcheck.reporters**: 错误报告组件

## 5. 应用层依赖

```
application.command_parser -> commands.*
application.main -> application.command_parser, core.html_model
```

- **application.command_parser**: 命令解析
- **application.main**: 应用入口

## 6. 依赖隔离说明

1. **第三方库依赖隔离**:
   - 仅在io.parser中依赖HTML解析库
   - 仅在spellcheck.checker中依赖拼写检查库

2. **功能模块解耦**:
   - 核心模型不依赖任何上层模块
   - I/O模块仅依赖核心模块
   - 命令模块通过接口和依赖注入减少耦合

3. **横向依赖减少**:
   - 各命令子模块间无相互依赖
   - 拼写检查模块与核心模块无直接依赖

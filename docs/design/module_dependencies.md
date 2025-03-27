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
commands.edit.* -> commands.base, core.html_model, core.element
commands.display.* -> commands.base, core.html_model, core.element, spellcheck.*
commands.io.* -> commands.base, core.html_model
commands.session.* -> commands.base, core.*, commands.*
```

- **commands.base**: 命令基类和处理器
- **commands.edit**: 编辑操作命令
- **commands.display**: 显示相关命令
- **commands.io**: 输入输出命令
- **commands.session**: 会话管理命令

## 3. 插件系统依赖

```
plugins.plugin_base -> (无依赖)
plugins.spell_check_plugin -> plugins.plugin_base, spellcheck.checker
```

- **plugins.plugin_base**: 插件系统基础组件
- **plugins.spell_check_plugin**: 拼写检查插件实现

## 4. 应用层依赖

```
app -> core.session, commands.*, plugins.*
main -> app
```

- **app**: 应用程序主类
- **main**: 程序入口点

## 5. 依赖隔离说明

为确保系统的模块化和可维护性，所有第三方依赖应当通过适配器层进行隔离。例如，拼写检查功能可能依赖外部库，应当封装在 `spellcheck.checker` 模块内，不允许其他模块直接引用外部库。

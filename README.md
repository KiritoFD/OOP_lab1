# HTML编辑器

一个基于命令行的HTML文档编辑工具，支持HTML树结构操作、拼写检查及文件读写功能。本项目根据面向对象程序设计课程Lab1要求实现，旨在展示对OO设计思想和设计模式的理解应用。

## 运行与测试说明

### 环境要求
- Python 3.9+ | 依赖包：见requirements.txt

### 安装依赖 & 运行程序
```bash
pip install -r requirements.txt
python main.py                  # 普通启动
python main.py --new            # 强制创建新会话
python main.py file.html        # 启动时打开指定文件
```

### 执行测试
```bash
pytest                          # 执行所有测试
pytest tests/core/              # 测试核心模块
pytest tests/commands/edit/     # 测试编辑命令
pytest tests/io/                # 测试IO功能
pytest tests/spellcheck/        # 测试拼写检查
pytest -m unit                  # 执行单元测试
pytest -m integration           # 执行集成测试
pytest --cov=src tests/         # 生成测试覆盖率报告
```

## 测试覆盖率报告 | 总体覆盖率: 74.3% 📊

| 模块 | 核心文件 | 覆盖率 | | 模块 | 核心文件 | 覆盖率 |
|:-----|:---------|:-----:|--|:-----|:---------|:-----:|
| **核心** | core/element.py | 65% | | **编辑命令** | commands/edit/append_command.py | 92% |
| | core/exceptions.py | 90% | | | commands/edit/delete_command.py | 90% |
| | core/html_model.py | 71% | | | commands/edit/edit_id_command.py | 80% |
| **命令系统** | commands/base.py | 86% | | | commands/edit/edit_text_command.py | 82% |
| | commands/command_exceptions.py | 89% | | | commands/edit/insert_command.py | 77% |
| | commands/display_commands.py | 87% | | **I/O模块** | commands/io_commands.py | 78% |
| | commands/observer.py | 80% | | | io/parser.py | 62% |
| **应用层** | application/command_parser.py | 46% | | | io/writer.py | 64% |
| | main.py | 44% | | **拼写检查** | spellcheck/checker.py | 75% |
| **会话管理** | session_manager.py | 91% | | | spellcheck/adapters/language_tool.py | 20% |
| | state/session_state.py | 90% | | **其他** | utils/html_utils.py | 33% |

> **注**: 已移除零覆盖率文件以更准确反映项目整体测试状况

## 项目说明

### 功能特点
- **HTML树形结构操作**: 插入、追加、删除、修改元素
- **文档树视图**: 以树形结构显示HTML文档
- **拼写检查**: 检查文档中的拼写错误并提供建议
- **文件操作**: 读取和保存HTML文件
- **多文件编辑**: 支持同时编辑多个文件
- **撤销/重做**: 完整的操作历史管理
- **会话恢复**: 退出后可恢复上次编辑状态
率报告
### 架构设计
项目采用模块化分层架构，遵循SOLID原则： 总体覆盖率: 74.3% 📊
- **核心层**: HTML模型定义和基础操作
- **命令层**: 实现各类编辑和显示命令件路径 | 语句数 | 覆盖率 | 图示 |
- **I/O层**: 处理文件读写和解析|:--------|:---------|:-----:|:-----:|:-----|
- **应用层**: 提供命令行界面和程序流程控制
|| src\core\element.py | 48 | 65% | ███████████████⚫⚫⚫⚫⚫⚫⚫⚫ |
应用了多种设计模式： 90% | █████████████████████⚫⚫ |
- **命令模式**: 实现撤销/重做功能███████████⚫⚫⚫⚫⚫⚫⚫ |
- **组合模式**: 构建HTML元素树结构
- **访问者模式**: 遍历树结构进行拼写检查
- **适配器模式**: 隔离第三方依赖██████⚫⚫ |
- **观察者模式**: 实现命令执行通知████⚫⚫⚫ |
observer.py | 5 | 80% | ████████████████⚫⚫⚫⚫ |
详细资料: [architecture.md](docs/architecture.md) | [requirements_fulfillment.md](docs\requirements_fulfillment.md) | [depedencies.md](docs\detailed_dependencies.md) | [uml](docs\uml_complete_diagram.md)
⚫ |
## 命令使用说明⚫ |
███████⚫⚫⚫⚫ |
### 编辑命令edit\edit_text_command.py | 40 | 82% | ████████████████████⚫⚫⚫⚫ |
- **insert** `insert 标签名 ID值 插入位置 [文本内容]` - 在指定元素前插入新元素|
- **append** `append 标签名 ID值 父元素ID [文本内容]` - 在指定元素内添加子元素
- **edit-id** `edit-id 原ID 新ID` - 修改元素的ID
- **edit-text** `edit-text 元素ID [新文本内容]` - 修改元素的文本内容
- **delete** `delete 元素ID` - 删除指定元素及其子元素

### 显示命令⚫⚫⚫⚫ |
- **print-tree** `print-tree` 或 `tree` - 以树形结构显示当前HTML
- **spell-check** `spell-check` - 检查文本内容的拼写错误
- **dir-tree** `dir-tree [目录路径]` - 以树形结构显示目录anager.py | 203 | 91% | ██████████████████████⚫⚫ |
- **showid** `showid true|false` - 控制是否在树中显示元素ID

### I/O命令k\adapters\language_tool.py | 10 | 20% | ████⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫ |
- **read** `read 文件路径` - 从文件读取HTML |
- **save** `save [文件路径]` - 将当前HTML保存到文件
- **init** `init` - 创建空白HTML结构l_utils.py | 9 | 33% | ███████⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫ |

### 撤销和重做
- **undo** `undo` - 撤销上一个编辑操作502** | **74.3%** | ██████████████████⚫⚫⚫⚫⚫⚫ |
- **redo** `redo` - 重做上一个被撤销的操作
代码，⚫ 表示未覆盖代码 (每个符号代表约4%的覆盖率)
### 会话管理命令
- **load** `load 文件路径` - 打开新文件或加载已有文件
- **editor-list** `editor-list` 或 `list` - 显示所有打开的文件
- **edit** `edit 文件路径` - 切换到指定文件
- **close** `close` - 关闭当前编辑会话
- **exit/quit** `exit` 或 `quit` - 退出程序
- **help** `help` - 显示命令帮助
器实现了以下核心功能：
## 注意事项
1. 必须先执行`read`或`init`命令初始化HTML模型后才能使用其他命令树形结构操作**：插入、追加、删除、修改元素
2. I/O操作后会清空命令历史，无法执行撤销/重做- **文档树视图**：以树形结构显示HTML文档
3. 元素ID在整个文档中必须唯一写错误并提供建议
4. html、head、body和title标签自动使用标签名作为ID- **文件操作**：读取和保存HTML文件
5. 退出程序时会自动保存会话状态，下次启动时可恢复
6. 拼写错误的节点在树形显示中会标记为[X]

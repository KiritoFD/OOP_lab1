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

## 测试覆盖率报告 | 总体覆盖率: 90%

### 完整覆盖率报告

```
pytest --cov . >test_out.txt
```

| 文件路径                                           |     语句数     |    未覆盖    |    覆盖率    |
| :------------------------------------------------- | :------------: | :-----------: | :-----------: |
| cleanup_cache.py                                   |       0       |       0       |     100%     |
| conftest.py                                        |       13       |       0       |     100%     |
| main.py                                            |      161      |      30      |      81%      |
| src\__init__.py                                  |       0       |       0       |     100%     |
| src\application\__init__.py                      |       0       |       0       |     100%     |
| src\application\command_parser.py                  |       87       |      47      |      46%      |
| src\commands\__init__.py                         |       0       |       0       |     100%     |
| src\commands\base.py                               |       59       |       8       |      86%      |
| src\commands\command_exceptions.py                 |       9       |       1       |      89%      |
| src\commands\display\__init__.py                 |       0       |       0       |     100%     |
| src\commands\display\base.py                       |       0       |       0       |     100%     |
| src\commands\display\dir_tree.py                   |       0       |       0       |     100%     |
| src\commands\display\print_tree.py                 |       0       |       0       |     100%     |
| src\commands\display\spell_check.py                |       0       |       0       |     100%     |
| src\commands\display_commands.py                   |      145      |      19      |      87%      |
| src\commands\edit\__init__.py                    |       6       |       0       |     100%     |
| src\commands\edit\append_command.py                |       52       |       4       |      92%      |
| src\commands\edit\delete_command.py                |       48       |       5       |      90%      |
| src\commands\edit\edit_id_command.py               |       56       |      11      |      80%      |
| src\commands\edit\edit_text_command.py             |       40       |       7       |      82%      |
| src\commands\edit\insert_command.py                |       73       |      17      |      77%      |
| src\commands\io\__init__.py                      |       0       |       0       |     100%     |
| src\commands\io\init.py                            |       0       |       0       |     100%     |
| src\commands\io\read.py                            |       0       |       0       |     100%     |
| src\commands\io\save.py                            |       0       |       0       |     100%     |
| src\commands\io_commands.py                        |      120      |      27      |      78%      |
| src\commands\observer.py                           |       5       |       1       |      80%      |
| src\core\__init__.py                             |       0       |       0       |     100%     |
| src\core\element.py                                |       48       |      17      |      65%      |
| src\core\exceptions.py                             |       20       |       2       |      90%      |
| src\core\html_element.py                           |       0       |       0       |     100%     |
| src\core\html_model.py                             |       96       |      28      |      71%      |
| src\core\html_writer.py                            |       0       |       0       |     100%     |
| src\io\__init__.py                               |       0       |       0       |     100%     |
| src\io\html_writer.py                              |       0       |       0       |     100%     |
| src\io\parser.py                                   |      125      |      48      |      62%      |
| src\io\writer.py                                   |       47       |      17      |      64%      |
| src\main.py                                        |      126      |      70      |      44%      |
| src\session_manager.py                             |      203      |      19      |      91%      |
| src\spellcheck\__init__.py                       |       0       |       0       |     100%     |
| src\spellcheck\adapters\__init__.py              |       0       |       0       |     100%     |
| src\spellcheck\adapters\language_tool.py           |       10       |       8       |      20%      |
| src\spellcheck\checker.py                          |       79       |      20      |      75%      |
| src\state\__init__.py                            |       0       |       0       |     100%     |
| src\state\session_state.py                         |       39       |       4       |      90%      |
| src\utils\html_utils.py                            |       9       |       6       |      33%      |
| tests\__init__.py                                |       0       |       0       |     100%     |
| tests\application\__init__.py                    |       0       |       0       |     100%     |
| tests\application\test_command_parser.py           |       0       |       0       |     100%     |
| tests\commands\__init__.py                       |       0       |       0       |     100%     |
| tests\commands\display\test_print_tree_command.py  |      161      |      30      |      81%      |
| tests\commands\display\test_spell_check_command.py |      135      |       3       |      98%      |
| tests\commands\edit\__init__.py                  |       0       |       0       |     100%     |
| tests\commands\edit\conftest.py                    |       7       |       0       |     100%     |
| tests\commands\edit\test_append_command.py         |      100      |       4       |      96%      |
| tests\commands\edit\test_delete_command.py         |       90       |       6       |      93%      |
| tests\commands\edit\test_edit_id_command.py        |      103      |       3       |      97%      |
| tests\commands\edit\test_edit_text_command.py      |      104      |       1       |      99%      |
| tests\commands\edit\test_insert_command.py         |       78       |       3       |      96%      |
| tests\commands\file\test_read_command.py           |       0       |       0       |     100%     |
| tests\commands\io\__init__.py                    |       0       |       0       |     100%     |
| tests\commands\io\test_io_commands.py              |       0       |       0       |     100%     |
| tests\commands\io\test_save_command.py             |       0       |       0       |     100%     |
| tests\conftest.py                                  |       23       |       1       |      96%      |
| tests\core\test_element.py                         |       0       |       0       |     100%     |
| tests\core\test_html_model.py                      |       0       |       0       |     100%     |
| tests\core\test_html_model_comprehensive.py        |       0       |       0       |     100%     |
| tests\core\test_parser.py                          |       0       |       0       |     100%     |
| tests\html_utils\test_html_utils.py                |       0       |       0       |     100%     |
| tests\input\__init__.py                          |       0       |       0       |     100%     |
| tests\integration\__init__.py                    |       0       |       0       |     100%     |
| tests\integration\test_comprehensive.py            |      244      |       8       |      97%      |
| tests\integration\test_edge_cases.py               |      177      |      18      |      90%      |
| tests\integration\test_html_lifecycle.py           |       0       |       0       |     100%     |
| tests\integration\test_integration.py              |       0       |       0       |     100%     |
| tests\integration\test_malformed_html.py           |       63       |       0       |     100%     |
| tests\integration\test_performance.py              |      104      |       0       |     100%     |
| tests\integration\test_real_world_scenarios.py     |       86       |       0       |     100%     |
| tests\io\__init__.py                             |       0       |       0       |     100%     |
| tests\io\test_init_command.py                      |       66       |       1       |      98%      |
| tests\io\test_malformed_html.py                    |       58       |       0       |     100%     |
| tests\io\test_read_command.py                      |       82       |       0       |     100%     |
| tests\test_io.py                                   |      153      |       0       |     100%     |
| tests\test_main.py                                 |      169      |      20      |      88%      |
| tests\test_main_session_persistence.py             |       44       |       3       |      93%      |
| tests\test_model.py                                |       85       |       6       |      93%      |
| tests\test_session_comprehensive.py                |      267      |       0       |     100%     |
| tests\test_session_integration.py                  |       0       |       0       |     100%     |
| tests\test_session_manager.py                      |       0       |       0       |     100%     |
| tests\test_session_state.py                        |      112      |       0       |     100%     |
| tests\test_spellcheck.py                           |      112      |       5       |      96%      |
| tests\test_system_integration.py                   |      137      |       0       |     100%     |
| **总计**                                     | **5344** | **553** | **90%** |

## 项目说明

### 功能特点

- **HTML树形结构操作**: 插入、追加、删除、修改元素
- **文档树视图**: 以树形结构显示HTML文档
- **拼写检查**: 检查文档中的拼写错误并提供建议
- **文件操作**: 读取和保存HTML文件
- **多文件编辑**: 支持同时编辑多个文件
- **撤销/重做**: 完整的操作历史管理
- **会话恢复**: 退出后可恢复上次编辑状态

### 架构设计

项目采用模块化分层架构，遵循SOLID原则：

- **核心层**: HTML模型定义和基础操作
- **命令层**: 实现各类编辑和显示命令
- **I/O层**: 处理文件读写和解析
- **应用层**: 提供命令行界面和程序流程控制

应用了多种设计模式：

- **命令模式**: 实现撤销/重做功能
- **组合模式**: 构建HTML元素树结构
- **访问者模式**: 遍历树结构进行拼写检查
- **适配器模式**: 隔离第三方依赖
- **观察者模式**: 实现命令执行通知

详细资料: [architecture.md](docs/architecture.md) | [requirements_fulfillment.md](docs\requirements_fulfillment.md) | [depedencies.md](docs\detailed_dependencies.md) | [uml](docs\uml_complete_diagram.md)

## 命令使用说明

### 编辑命令

- **insert** `insert 标签名 ID值 插入位置 [文本内容]` - 在指定元素前插入新元素
- **append** `append 标签名 ID值 父元素ID [文本内容]` - 在指定元素内添加子元素
- **edit-id** `edit-id 原ID 新ID` - 修改元素的ID
- **edit-text** `edit-text 元素ID [新文本内容]` - 修改元素的文本内容
- **delete** `delete 元素ID` - 删除指定元素及其子元素

### 显示命令

- **print-tree** `print-tree` 或 `tree` - 以树形结构显示当前HTML
- **spell-check** `spell-check` - 检查文本内容的拼写错误
- **dir-tree** `dir-tree [目录路径]` - 以树形结构显示目录
- **showid** `showid true|false` - 控制是否在树中显示元素ID

### I/O命令

- **read** `read 文件路径` - 从文件读取HTML
- **save** `save [文件路径]` - 将当前HTML保存到文件
- **init** `init` - 创建空白HTML结构

### 撤销和重做

- **undo** `undo` - 撤销上一个编辑操作
- **redo** `redo` - 重做上一个被撤销的操作

### 会话管理命令

- **load** `load 文件路径` - 打开新文件或加载已有文件
- **editor-list** `editor-list` 或 `list` - 显示所有打开的文件
- **edit** `edit 文件路径` - 切换到指定文件
- **close** `close` - 关闭当前编辑会话
- **exit/quit** `exit` 或 `quit` - 退出程序
- **help** `help` - 显示命令帮助

## 注意事项

1. 必须先执行 `read`或 `init`命令初始化HTML模型后才能使用其他命令
2. I/O操作后会清空命令历史，无法执行撤销/重做
3. 元素ID在整个文档中必须唯一
4. html、head、body和title标签自动使用标签名作为ID
5. 退出程序时会自动保存会话状态，下次启动时可恢复
6. 拼写错误的节点在树形显示中会标记为[X]

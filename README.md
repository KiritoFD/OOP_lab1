# HTML编辑器

一个基于命令行的HTML文档编辑工具，支持HTML树结构操作、拼写检查及文件读写功能。本项目根据面向对象程序设计课程Lab1要求实现，旨在展示对OO设计思想和设计模式的理解应用。

## 运行与测试说明

### 环境要求

- Python 3.9+
- 依赖包：见requirements.txt

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行程序

```bash
python main.py
```

或者指定启动参数：

```bash
python main.py --new     # 强制创建新会话，不恢复上次状态
python main.py file.html # 启动时打开指定文件
```

### 执行测试

执行所有测试：

```bash
pytest
```

执行特定模块测试：

```bash
pytest tests/core/          # 测试核心模块
pytest tests/commands/edit/ # 测试编辑命令
pytest tests/io/            # 测试IO功能
pytest tests/spellcheck/    # 测试拼写检查
```

执行特定标记的测试：

```bash
pytest -m unit        # 执行单元测试
pytest -m integration # 执行集成测试
pytest -m "not slow"  # 跳过耗时测试
```

生成测试覆盖率报告：

```bash
pytest --cov=src tests/
```
---------- coverage: platform win32, python 3.12.7-final-0 -----------
当前覆盖率
Name                                       Stmts   Miss  Cover
--------------------------------------------------------------
src\__init__.py                                0      0   100%
src\application\__init__.py                    0      0   100%
src\application\command_parser.py             87     47    46%
src\commands\__init__.py                       0      0   100%
src\commands\base.py                          59      8    86%
src\commands\command_exceptions.py             9      1    89%
src\commands\display\__init__.py               0      0   100%
src\commands\display\base.py                   0      0   100%
src\commands\display\dir_tree.py               0      0   100%
src\commands\display\print_tree.py             0      0   100%
src\commands\display\spell_check.py            0      0   100%
src\commands\display_commands.py             145     19    87%
src\commands\edit\__init__.py                  6      0   100%
src\commands\edit\append_command.py           52      4    92%
src\commands\edit\delete_command.py           48      5    90%
src\commands\edit\edit_id_command.py          56     11    80%
src\commands\edit\edit_text_command.py        40      7    82%
src\commands\edit\insert_command.py           73     17    77%
src\commands\io\__init__.py                    0      0   100%
src\commands\io\init.py                        0      0   100%
src\commands\io\read.py                        0      0   100%
src\commands\io\save.py                        0      0   100%
src\commands\io_commands.py                  120     27    78%
src\commands\observer.py                       5      1    80%
src\core\__init__.py                           0      0   100%
src\core\element.py                           48     17    65%
src\core\exceptions.py                        20      2    90%
src\core\html_element.py                       0      0   100%
src\core\html_model.py                        96     28    71%
src\core\html_writer.py                        0      0   100%
src\core\parser.py                            69     69     0%
src\io\__init__.py                             0      0   100%
src\io\html_writer.py                          0      0   100%
src\io\parser.py                             125     48    62%
src\io\writer.py                              47     17    64%
src\main.py                                  126     70    44%
src\session_manager.py                       203     19    91%
src\spellcheck\__init__.py                     0      0   100%
src\spellcheck\adapters\__init__.py            0      0   100%
src\spellcheck\adapters\language_tool.py      10      8    20%
src\spellcheck\checker.py                     79     20    75%
src\spellcheck\models.py                      18     18     0%
src\spellcheck\reporters.py                   41     41     0%
src\state\__init__.py                          0      0   100%
src\state\session_state.py                    39      4    90%
src\utils\html_utils.py                        9      6    33%
--------------------------------------------------------------
TOTAL                                       1630    514    68%

## 项目说明

### 功能特点

本HTML编辑器实现了以下核心功能：

- **HTML树形结构操作**：插入、追加、删除、修改元素
- **文档树视图**：以树形结构显示HTML文档
- **拼写检查**：检查文档中的拼写错误并提供建议
- **文件操作**：读取和保存HTML文件
- **多文件编辑**：支持同时编辑多个文件
- **撤销/重做**：完整的操作历史管理
- **会话恢复**：退出后可恢复上次编辑状态

### 架构设计

项目采用模块化分层架构，遵循SOLID原则：

- **核心层**：HTML模型定义和基础操作
- **命令层**：实现各类编辑和显示命令
- **I/O层**：处理文件读写和解析
- **应用层**：提供命令行界面和程序流程控制

应用了多种设计模式：

- **命令模式**：实现撤销/重做功能
- **组合模式**：构建HTML元素树结构
- **访问者模式**：遍历树结构进行拼写检查
- **适配器模式**：隔离第三方依赖
- **观察者模式**：实现命令执行通知

详细架构说明请参见 [architecture.md](docs/architecture.md)

具体功能实现参见[requirements_fulfillment.md](docs\requirements_fulfillment.md)

依赖关系详见[depedencies.md](docs\detailed_dependencies.md)

UML图详见[uml](docs\uml_complete_diagram.md)

## 命令使用说明

### 编辑命令

1. **插入元素** - 在指定元素前插入新元素

```
insert 标签名 ID值 插入位置 [文本内容]
```

2. **添加子元素** - 在指定元素内添加子元素

```
append 标签名 ID值 父元素ID [文本内容]
```

3. **修改ID** - 修改元素的ID

```
edit-id 原ID 新ID
```

4. **修改文本** - 修改元素的文本内容

```
edit-text 元素ID [新文本内容]
```

5. **删除元素** - 删除指定元素及其子元素

```
delete 元素ID
```

### 显示命令

6. **显示树结构** - 以树形结构显示当前HTML

```
print-tree
```

或简写:

```
tree
```

7. **拼写检查** - 检查文本内容的拼写错误

```
spell-check
```

8. **显示目录结构** - 以树形结构显示目录

```
dir-tree [目录路径]
```

9. **控制ID显示** - 控制是否在树中显示元素ID

```
showid true|false
```

### I/O命令

10. **读取文件** - 从文件读取HTML

```
read 文件路径
```

11. **保存文件** - 将当前HTML保存到文件

```
save [文件路径]
```

12. **初始化** - 创建空白HTML结构

```
init
```

### 撤销和重做

13. **撤销** - 撤销上一个编辑操作

```
undo
```

14. **重做** - 重做上一个被撤销的操作

```
redo
```

### 会话管理命令

15. **加载文件** - 打开新文件或加载已有文件

```
load 文件路径
```

16. **列出编辑器** - 显示所有打开的文件

```
editor-list
```

或简写:

```
list
```

17. **切换文件** - 切换到指定文件

```
edit 文件路径
```

18. **关闭当前文件** - 关闭当前编辑会话

```
close
```

### 其他命令

19. **退出** - 退出程序

```
exit
```

或

```
quit
```

20. **帮助** - 显示命令帮助

```
help
```

## 注意事项

1. 必须先执行 `read`或 `init`命令初始化HTML模型后才能使用其他命令
2. I/O操作后会清空命令历史，无法执行撤销/重做
3. 元素ID在整个文档中必须唯一
4. html、head、body和title标签自动使用标签名作为ID
5. 退出程序时会自动保存会话状态，下次启动时可恢复
6. 拼写错误的节点在树形显示中会标记为[X]

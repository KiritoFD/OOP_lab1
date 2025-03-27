# HTML编辑器架构设计文档

## 1. 项目概述

HTML编辑器是一个基于命令行的工具，用于编辑HTML文档。它支持基本的编辑功能、多文件管理、拼写检查、树形结构显示等功能。本文档详细描述系统架构设计，包括模块划分、依赖关系和关键设计决策。

## 2. 系统架构

### 2.1 架构分层

系统采用分层架构设计，从下至上包括：

```
+-------------------+
|    Application    | 应用层：命令行界面、应用启动
+-------------------+
         |
+-------------------+
|     Session       | 会话层：多文件管理、会话持久化
+-------------------+
         |
+-------------------+
|     Commands      | 命令层：命令执行、撤销/重做
+-------------------+
         |
+-------------------+
|  Core / Services  | 核心层：HTML模型、拼写检查
+-------------------+
         |
+-------------------+
|      I/O          | I/O层：文件操作、展示渲染
+-------------------+
```

### 2.2 模块依赖关系

```
+------------+       +------------+       +------------+
|     I/O    | <---- |    Core    | <---- |  Commands  |
+------------+       +------------+       +------------+
                           ^                    ^
                           |                    |
                           +--------------------+
                                     |
                            +------------------+
                            |     Session      |
                            +------------------+
                                     |
                            +------------------+
                            |   Application    |
                            +------------------+
```

## 3. 详细模块设计

### 3.1 核心模块 (Core)

负责HTML文档模型的定义和基本操作。

#### 3.1.1 主要组件

- **HtmlElement**: HTML元素基类
  - 属性：tag, id, text, parent, children
  - 方法：add_child(), remove_child(), find_by_id()
  
- **HtmlDocument**: HTML文档类
  - 管理元素树和ID索引
  - 提供元素查找、添加、修改和删除的方法
  
- **ElementFactory**: HTML元素工厂
  - 创建各种类型的HTML元素

#### 3.1.2 文件清单

- `src/core/model.py`: HTML元素模型定义
- `src/core/document.py`: HTML文档管理
- `src/core/exceptions.py`: 自定义异常类

#### 3.1.3 设计模式

- **组合模式**: 用于表示HTML元素的树形结构
- **工厂模式**: 用于创建HTML元素

### 3.2 命令模块 (Commands)

实现编辑器的所有命令操作，采用命令模式设计。

#### 3.2.1 主要组件

- **Command**: 命令基类
  - 方法：execute(), undo()
  
- **CommandProcessor**: 命令处理器
  - 管理命令执行、撤销和重做
  
- **编辑命令**:
  - InsertCommand: 在元素前插入新元素
  - AppendCommand: 在元素内添加子元素
  - DeleteCommand: 删除元素
  - EditTextCommand: 编辑元素文本
  - EditIdCommand: 修改元素ID
  
- **显示命令**:
  - PrintTreeCommand: 显示HTML树结构
  - SpellCheckCommand: 执行拼写检查
  - ShowIdCommand: 控制ID显示选项
  - DirectoryTreeCommand: 显示目录结构

#### 3.2.2 文件清单

- `src/commands/base.py`: 命令基类和处理器
- `src/commands/edit/`: 编辑命令实现
- `src/commands/display/`: 显示命令实现
- `src/commands/io/`: IO命令实现
- `src/commands/session/`: 会话命令实现

#### 3.2.3 设计模式

- **命令模式**: 封装所有操作为命令对象
- **备忘录模式**: 保存命令执行前的状态用于撤销

### 3.3 I/O模块 (IO)

处理文件读写和显示渲染。

#### 3.3.1 主要组件

- **HtmlParser**: HTML解析器
  - 将HTML文本转换为模型对象
  
- **HtmlWriter**: HTML写入器
  - 将模型序列化为HTML文本
  
- **TreeRenderer**: 树形结构渲染器
  - 将HTML模型渲染为树形文本
  - 支持ID显示控制和拼写错误标记
  
- **DirectoryTreeRenderer**: 目录树渲染器
  - 显示文件目录的树形结构

#### 3.3.2 文件清单

- `src/io/parser.py`: HTML解析实现
- `src/io/writer.py`: HTML序列化实现
- `src/io/display/`: 显示渲染相关实现

#### 3.3.3 设计模式

- **适配器模式**: 封装第三方HTML解析库
- **策略模式**: 实现不同的渲染策略
- **装饰器模式**: 增强树形渲染功能

### 3.4 拼写检查模块 (SpellCheck)

提供文本拼写检查功能。

#### 3.4.1 主要组件

- **SpellChecker**: 拼写检查接口
  - 方法：check_text()
  
- **LanguageToolChecker**: 基于LanguageTool的实现
  
- **SpellError**: 表示拼写错误的数据类
  
- **SpellErrorReporter**: 错误报告生成器

#### 3.4.2 文件清单

- `src/spell/checker.py`: 拼写检查器实现
- `src/spell/error.py`: 拼写错误模型
- `src/spell/reporter.py`: 错误报告工具

#### 3.4.3 设计模式

- **策略模式**: 支持多种拼写检查实现
- **访问者模式**: 遍历HTML树进行检查

### 3.5 会话模块 (Session)

管理多文件编辑会话及其状态。

#### 3.5.1 主要组件

- **Editor**: 单文件编辑器
  - 包含HTML模型和命令历史
  
- **EditorSession**: 会话管理器
  - 管理多个编辑器实例
  - 维护当前活动编辑器
  
- **SessionPersistence**: 会话持久化
  - 保存和恢复会话状态

#### 3.5.2 文件清单

- `src/session/editor.py`: 编辑器类
- `src/session/session.py`: 会话管理
- `src/session/persistence.py`: 持久化实现

#### 3.5.3 设计模式

- **单例模式**: 确保会话管理的全局唯一性
- **观察者模式**: 监听编辑器状态变化

### 3.6 应用模块 (Application)

提供用户界面和程序入口。

#### 3.6.1 主要组件

- **CommandLineInterface**: 命令行界面
  - 处理用户输入和命令解析
  
- **Application**: 应用主类
  - 初始化各组件
  - 管理程序生命周期

#### 3.6.2 文件清单

- `src/app/cli.py`: 命令行交互界面
- `src/app/main.py`: 程序入口
- `main.py`: 应用启动脚本

#### 3.6.3 设计模式

- **外观模式**: 为复杂系统提供简单接口
- **中介者模式**: 协调各模块之间的交互

## 4. 关键设计决策

### 4.1 命令模式实现

采用命令模式封装所有编辑操作，实现撤销/重做功能。每个命令对象包含:
- 执行操作所需的所有数据
- 执行前的状态快照（用于撤销）
- 执行和撤销的具体实现

命令历史记录由CommandProcessor管理，支持以下规则:
- 编辑类命令可以撤销和重做
- 在撤销后执行新命令会清空重做栈
- 显示类命令在撤销/重做时被跳过
- IO命令执行后会清空命令历史

### 4.2 HTML模型设计

HTML模型采用组合模式，主要考虑:
- 使用继承关系表示不同类型的HTML元素
- 使用组合关系表示元素之间的嵌套
- 使用ID索引提高元素查找效率
- 通过Observer模式监听模型变化

### 4.3 多文件会话管理

多文件会话管理采用如下设计:
- 每个Editor实例管理一个HTML文档
- EditorSession维护所有打开的Editor和当前活动Editor
- 每个Editor有独立的命令历史和显示设置
- 会话状态通过JSON格式持久化

### 4.4 扩展性考虑

系统设计时考虑了以下扩展性需求:
- 使用接口隔离第三方依赖
- 采用策略模式支持多种拼写检查实现
- 通过装饰器模式扩展显示功能
- 使用工厂模式简化新命令的添加

### 4.5 第三方依赖管理

为减少对第三方库的直接依赖:
- 使用适配器模式封装HTML解析库
- 使用接口定义拼写检查服务
- 将外部依赖限制在特定模块内

## 5. 项目文件结构

```
OOP_lab1/
├── src/                  # 源代码
│   ├── core/             # 核心HTML模型
│   │   ├── model.py      # 元素模型定义
│   │   ├── document.py   # 文档管理
│   │   └── exceptions.py # 自定义异常
│   │
│   ├── commands/         # 命令实现
│   │   ├── base.py       # 命令基类和处理器
│   │   ├── edit/         # 编辑命令
│   │   │   ├── append_command.py
│   │   │   ├── insert_command.py
│   │   │   ├── delete_command.py
│   │   │   ├── edit_text_command.py
│   │   │   └── edit_id_command.py
│   │   ├── display/      # 显示命令
│   │   │   ├── print_tree_command.py
│   │   │   ├── spell_check_command.py
│   │   │   ├── show_id_command.py
│   │   │   └── directory_tree_command.py
│   │   ├── io/           # IO命令
│   │   │   ├── read_command.py
│   │   │   ├── save_command.py
│   │   │   └── init_command.py
│   │   └── session/      # 会话命令
│   │       ├── load_command.py
│   │       ├── close_command.py
│   │       ├── list_command.py
│   │       └── switch_command.py
│   │
│   ├── io/               # 输入输出处理
│   │   ├── parser.py     # HTML解析器
│   │   ├── writer.py     # HTML序列化
│   │   └── display/      # 显示相关
│   │       ├── tree_renderer.py
│   │       └── directory_renderer.py
│   │
│   ├── spell/            # 拼写检查功能
│   │   ├── checker.py    # 拼写检查器
│   │   ├── error.py      # 错误模型
│   │   └── reporter.py   # 错误报告
│   │
│   ├── session/          # 会话管理
│   │   ├── editor.py     # 编辑器管理
│   │   ├── session.py    # 会话管理
│   │   └── persistence.py # 会话持久化
│   │
│   └── app/              # 应用层
│       ├── cli.py        # 命令行界面
│       └── main.py       # 程序入口
│
├── tests/                # 测试代码
│   ├── core/             # 核心测试
│   ├── commands/         # 命令测试
│   ├── io/               # IO测试
│   ├── spell/            # 拼写检查测试
│   └── session/          # 会话管理测试
│
├── main.py               # 程序启动脚本
└── requirements.txt      # 依赖说明
```

## 6. 测试策略

### 6.1 单元测试

针对每个模块的核心功能进行单元测试:
- 核心模型的元素操作和文档管理
- 各类命令的执行和撤销功能
- IO操作的解析和序列化
- 拼写检查的错误检测

### 6.2 集成测试

测试模块之间的交互:
- 命令与HTML模型的交互
- 会话管理与编辑器的交互
- 拼写检查与HTML模型的集成

### 6.3 端到端测试

验证完整功能流程:
- 完整的编辑、撤销、重做流程
- 文件读写和会话持久化
- 多文件管理和切换

## 7. 运行要求

### 7.1 环境要求
- Python 3.8或以上
- pip包管理工具

### 7.2 安装依赖
```bash
pip install -r requirements.txt
```

### 7.3 启动应用
```bash
python main.py
```

### 7.4 运行测试
```bash
python -m unittest discover tests
```

## 8. 主要文件说明

### 8.1 核心文件

| 文件 | 描述 |
|------|------|
| `src/core/model.py` | HTML元素基类和具体实现 |
| `src/core/document.py` | HTML文档管理，负责元素树和ID索引 |
| `src/commands/base.py` | 命令基类和命令处理器实现 |
| `src/io/parser.py` | HTML解析器，将文本转换为模型 |
| `src/io/writer.py` | HTML序列化，将模型转换为文本 |
| `src/session/editor.py` | 单文件编辑器实现 |
| `src/session/session.py` | 多文件会话管理 |
| `src/app/cli.py` | 命令行界面实现 |

### 8.2 扩展文件

| 文件 | 描述 |
|------|------|
| `src/spell/checker.py` | 拼写检查器实现 |
| `src/io/display/directory_renderer.py` | 目录结构渲染器 |
| `src/session/persistence.py` | 会话状态持久化 |
| `src/commands/display/show_id_command.py` | ID显示控制命令 |

## 9. 总结

HTML编辑器采用模块化、分层架构设计，通过合理应用设计模式实现了功能扩展和组件解耦。系统分为核心、命令、IO、拼写检查、会话和应用六大模块，相互协作完成HTML编辑功能。架构设计考虑了代码复用、扩展性和可维护性，为实现基础和增强功能提供了坚实基础。
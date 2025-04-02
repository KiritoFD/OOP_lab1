# 测试指南：分层分功能测试策略

## 目录
1. [总体测试策略](#总体测试策略)
2. [测试层次](#测试层次)
3. [功能测试分类](#功能测试分类)
4. [测试目录结构](#测试目录结构)
5. [命名规范](#命名规范)
6. [测试执行命令](#测试执行命令)
7. [测试用例编写指南](#测试用例编写指南)

## 总体测试策略

本项目采用分层和分功能相结合的测试策略，确保应用的各个部分在不同级别上都经过充分测试：

- **分层测试**: 按照软件架构层次进行测试，从底层组件到高层功能
- **分功能测试**: 围绕特定功能或用户场景进行测试，保证各个功能点的完整性

这种组合策略能够同时保证代码的技术质量和业务功能的正确实现。

## 测试层次

### 1. 单元测试 (Unit Tests)

针对系统中的最小可测试组件，通常是类或方法级别。

- **特点**：独立执行，快速运行，使用模拟代替外部依赖
- **目标**：验证各组件的独立行为
- **工具**：pytest, unittest.mock

#### 单元测试示例

测试命令类中的单个方法：

```python
def test_append_command_adds_child():
    model = HtmlModel()
    cmd = AppendCommand(model, 'div', 'test-div', 'body')
    assert cmd.execute() is True
    assert model.find_by_id('test-div') is not None
```

### 2. 集成测试 (Integration Tests)

测试多个组件协同工作的情况。

- **特点**：测试组件间的交互，可能涉及部分外部依赖
- **目标**：验证组件间的协作和接口正确性
- **工具**：pytest, 部分模拟

#### 集成测试示例

测试CommandProcessor与Command之间的交互：

```python
def test_processor_executes_command_sequence():
    model = HtmlModel()
    processor = CommandProcessor()
    processor.execute(InitCommand(model))
    processor.execute(AppendCommand(model, 'div', 'content', 'body'))
    processor.execute(AppendCommand(model, 'p', 'text', 'content', 'Hello'))
    assert model.find_by_id('text').text == 'Hello'
```

### 3. 系统测试 (System Tests)

测试整个应用系统作为一个整体的行为。

- **特点**：从用户角度测试完整流程，较少使用模拟
- **目标**：验证系统整体功能和性能
- **工具**：pytest, pytest-mock (较少使用)

#### 系统测试示例

测试完整的用户工作流：

```python
def test_full_application_workflow():
    # 创建会话，加载文件
    # 执行编辑操作
    # 保存文件
    # 验证整个过程正确完成
```

## 功能测试分类

### 1. 核心功能测试

测试应用的基础功能模块：

- **HTML模型测试**: 测试HTML元素的创建、访问和修改
- **命令系统测试**: 测试命令的执行、撤销和重做
- **文件操作测试**: 测试文件的加载和保存

### 2. 特性功能测试

测试应用的特定功能：

- **拼写检查测试**: 测试拼写错误的检测和显示
- **目录树显示测试**: 测试目录结构的显示
- **会话管理测试**: 测试会话状态的保存和恢复

### 3. 用户场景测试

模拟实际用户操作场景：

- **编辑文档场景**: 从加载到编辑到保存的完整流程
- **错误处理场景**: 模拟各种错误情况及其处理
- **大文件处理场景**: 测试处理大型HTML文件的性能

## 测试目录结构

## 测试执行命令

### 全局命令

运行所有测试:
```bash
pytest
```

生成覆盖率报告:
```bash
pytest --cov=src tests/
```

HTML格式覆盖率报告:
```bash
pytest --cov=src --cov-report=html tests/
```

运行单元测试:
```bash
pytest -m unit
```

运行集成测试:
```bash
pytest -m integration
```

运行慢速测试:
```bash
pytest -m slow
```

运行非慢速测试:
```bash
pytest -m "not slow"
```

组合标记:
```bash
pytest -m "integration and slow"
```

### 核心组件测试

HTML模型基础测试:
```bash
pytest tests/core/test_html_model.py
```

HTML模型全面测试:
```bash
pytest tests/core/test_html_model_comprehensive.py
```

HTML元素测试:
```bash
pytest tests/core/test_element.py
```

### 命令系统测试

命令基础设施测试:
```bash
pytest tests/commands/test_commands.py
```

所有编辑命令测试:
```bash
pytest tests/commands/edit/
```

添加命令测试:
```bash
pytest tests/commands/edit/test_append_command.py
```

删除命令测试:
```bash
pytest tests/commands/edit/test_delete_command.py
```

修改ID命令测试:
```bash
pytest tests/commands/edit/test_edit_id_command.py
```

修改文本命令测试:
```bash
pytest tests/commands/edit/test_edit_text_command.py
```

插入命令测试:
```bash
pytest tests/commands/edit/test_insert_command.py
```

所有显示命令测试:
```bash
pytest tests/commands/display/
```

树形显示命令测试:
```bash
pytest tests/commands/display/test_print_tree_command.py
```

拼写检查命令测试:
```bash
pytest tests/commands/display/test_spell_check_command.py
```

拼写检查注入测试:
```bash
pytest tests/commands/display/test_spell_check_injection.py
```

目录树命令测试:
```bash
pytest tests/commands/display/test_dir_tree_command.py
```

读取文件测试:
```bash
pytest tests/commands/file/test_read_command.py
```

保存文件测试:
```bash
pytest tests/commands/io/test_save_command.py
```

IO操作测试:
```bash
pytest tests/commands/io/test_io.py
```

HTML解析器测试:
```bash
pytest tests/io/test_parser.py
```

### 撤销/重做测试

命令历史测试:
```bash
pytest tests/commands/do/test_command_history.py
```

撤销命令测试:
```bash
pytest tests/commands/do/test_undoredo_commands.py::TestUndoRedoCommands::test_undo_*
```

重做命令测试:
```bash
pytest tests/commands/do/test_undoredo_commands.py::TestUndoRedoCommands::test_redo_*
```

撤销重做集成测试:
```bash
pytest tests/commands/do/test_processor_history_integration.py
```

### 会话管理测试

会话状态测试:
```bash
pytest tests/session/test_session_state.py
```

会话持久化测试:
```bash
pytest tests/session/test_main_session_persistence.py
```

显示增强测试:
```bash
pytest tests/test_display_enhancements.py
```

### 集成测试

全面集成测试:
```bash
pytest tests/integration/test_comprehensive.py
```

HTML模型基础集成测试:
```bash
pytest tests/integration/test_comprehensive.py::TestComprehensiveIntegration::test_html_model_basics
```

编辑命令集成测试:
```bash
pytest tests/integration/test_comprehensive.py::TestComprehensiveIntegration::test_editing_commands
```

IO操作集成测试:
```bash
pytest tests/integration/test_comprehensive.py::TestComprehensiveIntegration::test_io_and_tree_structure
```

拼写检查集成测试:
```bash
pytest tests/integration/test_comprehensive.py::TestComprehensiveIntegration::test_spellcheck
```

撤销重做集成测试:
```bash
pytest tests/integration/test_comprehensive.py::TestComprehensiveIntegration::test_undo_redo_functionality
```

IO命令历史测试:
```bash
pytest tests/integration/test_comprehensive.py::TestComprehensiveIntegration::test_io_command_clears_history
```

特殊字符处理测试:
```bash
pytest tests/integration/test_comprehensive.py::TestComprehensiveIntegration::test_special_characters_handling
```

错误处理集成测试:
```bash
pytest tests/integration/test_comprehensive.py::TestComprehensiveIntegration::test_error_handling
```

### 系统测试

完整系统测试:
```bash
pytest tests/test_system_integration.py
```

应用工作流测试:
```bash
pytest tests/test_system_integration.py::TestSystemIntegration::test_full_application_workflow
```

特性覆盖测试:
```bash
pytest tests/test_system_integration.py::TestSystemIntegration::test_feature_coverage
```

测试覆盖检查:
```bash
pytest tests/test_system_integration.py::TestSystemIntegration::test_run_all_individual_tests
```

主程序功能测试:
```bash
pytest tests/test_main.py
```

### 特殊场景测试

无效命令测试:
```bash
pytest tests/test_main.py::test_invalid_command
```

参数缺失测试:
```bash
pytest tests/test_main.py::test_missing_arguments
```

元素不存在测试:
```bash
pytest tests/test_main.py::test_element_not_found
```

权限错误测试:
```bash
pytest tests/commands/display/test_dir_tree_command.py::TestDirTreeCommand::test_permission_denied_handling
```

特殊字符保存测试:
```bash
pytest tests/io/test_save_command.py::TestSaveCommand::test_save_special_chars
```

拼写检查错误处理测试:
```bash
pytest tests/commands/display/test_spell_check_command.py::TestSpellCheckError
```

### 调试命令

查找失败测试:
```bash
pytest -v | grep FAILED
```

查找预期失败的测试:
```bash
pytest -v | grep XFAIL
```

仅执行失败测试:
```bash
pytest --lf
```

调试模式运行:
```bash
pytest --pdb tests/io/test_save_command.py::TestSaveCommand::test_save_special_chars
```

详细输出:
```bash
pytest -vv tests/commands/display/test_spell_check_command.py
```

并行执行测试:
```bash
pytest -n auto
```

覆盖率热点分析:
```bash
pytest --cov=src --cov-report=term-missing tests/
```

## 测试用例编写指南


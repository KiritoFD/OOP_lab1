# HTML编辑器项目 - 详细UML类图

本文档提供HTML编辑器项目的详细UML类图和架构概述，帮助开发者理解系统的核心组件和它们之间的关系。

## 完整类图

```plantuml
@startuml HTML编辑器系统架构

skinparam packageStyle rectangle
skinparam linetype ortho
skinparam nodesep 60
skinparam ranksep 50
skinparam padding 5
skinparam defaultTextAlignment center

' 核心模块
package "核心层 (Core)" {
  class HtmlElement {
    -String tag
    -String id
    -String text
    -List<HtmlElement> children
    -HtmlElement parent
    -Dict attributes
    +add_child(HtmlElement child)
    +remove_child(HtmlElement child)
    +set_attribute(name, value)
    +get_attribute(name): String
    +is_ancestor_of(element): Boolean
    +find_child(id): HtmlElement
  }

  class HtmlModel {
    +HtmlElement root
    -Dict _id_map
    +find_by_id(id): HtmlElement
    +append_child(parent_id, tag, id, text): HtmlElement
    +insert_before(target_id, tag, id, text): HtmlElement
    +delete_element(element_id): Boolean
    +update_element_id(old_id, new_id)
    +replace_content(new_root)
    -_register_id(element)
    -_unregister_id(element)
  }

  abstract class HtmlVisitor {
    +{abstract} visit(element): void
  }

  HtmlElement "1" o-- "*" HtmlElement : 子元素 >
  HtmlElement "*" --o "1" HtmlElement : 父元素 >
  HtmlModel "1" *-- "1" HtmlElement : 根元素 >
  HtmlElement ..> HtmlVisitor : 接受访问 >
}

' I/O模块
package "I/O层" {
  class HtmlParser {
    +parse(html_content, model): void
    +parse_string(html_content, model): HtmlElement
    +parse_file(file_path, model): HtmlElement
    -_create_element_tree(soup_element): HtmlElement
    -_register_element_ids(element, model): void
  }

  class HtmlWriter {
    +write(model, file_path): Boolean
    +to_string(model): String
    -_element_to_string(element, indent): String
  }
}

' 工具模块
package "工具层" {
  class HtmlValidator {
    +{static} validate_model(model): Boolean
    +{static} validate_element(element): Boolean
    +{static} collect_ids(element, id_set): void
  }
}

' 拼写检查模块
package "拼写检查层" {
  class SpellChecker {
    -language_tool
    -Dict cache
    +check_text(text): List<SpellError>
    +get_suggestions(word): List<String>
  }

  class SpellError {
    +String word
    +List<String> suggestions
    +String context
    +Integer start_pos
    +Integer end_pos
  }

  SpellChecker ..> SpellError : 创建 >
}

' 命令模块
package "命令层" {
  abstract class Command {
    #HtmlModel model
    #Boolean recordable
    #String description
    +{abstract} execute(): Boolean
    +{abstract} undo(): Boolean
  }

  class CommandProcessor {
    -List _commands
    -List _undone
    -List _observers
    +execute(command): Boolean
    +undo(): Boolean
    +redo(): Boolean
    +clear_history(): void
    +add_observer(observer): void
  }

  interface CommandObserver {
    +on_command_event(event_type, kwargs): void
  }

  ' 编辑命令
  package "编辑命令" {
    class AppendCommand {
      +execute(): Boolean
      +undo(): Boolean
    }

    class DeleteCommand {
      +execute(): Boolean
      +undo(): Boolean
    }

    class EditTextCommand {
      +execute(): Boolean
      +undo(): Boolean
    }

    class EditIdCommand {
      +execute(): Boolean
      +undo(): Boolean
    }

    class InsertCommand {
      +execute(): Boolean
      +undo(): Boolean
    }
  }

  ' 显示命令
  package "显示命令" {
    class PrintTreeCommand {
      -Boolean show_id
      -Boolean check_spelling
      -SpellChecker spell_checker
      +execute(): Boolean
      +undo(): Boolean
      -_print_node(node, prefix, is_last): void
    }

    class SpellCheckCommand {
      +execute(): Boolean
      +undo(): Boolean
    }

    class DirTreeCommand {
      +execute(): Boolean
      +undo(): Boolean
    }
  }

  ' IO命令
  package "IO命令" {
    class ReadCommand {
      +execute(): Boolean
      +undo(): Boolean
    }

    class SaveCommand {
      +execute(): Boolean
      +undo(): Boolean
    }

    class InitCommand {
      +execute(): Boolean
      +undo(): Boolean
    }
  }

  ' 撤销重做命令
  package "命令历史" {
    class UndoCommand {
      +execute(): Boolean
      +undo(): Boolean
    }

    class RedoCommand {
      +execute(): Boolean
      +undo(): Boolean
    }

    class CommandHistory {
      -List history
      -List redos
      +add_command(command): void
      +get_last_command(): Command
      +can_undo(): Boolean
      +can_redo(): Boolean
      +clear(): void
    }
  }

  CommandProcessor o-- Command
  CommandProcessor o-- CommandObserver
  CommandProcessor *-- CommandHistory
  Command <|-- AppendCommand
  Command <|-- DeleteCommand
  Command <|-- EditTextCommand
  Command <|-- EditIdCommand
  Command <|-- InsertCommand
  Command <|-- PrintTreeCommand
  Command <|-- SpellCheckCommand
  Command <|-- DirTreeCommand
  Command <|-- ReadCommand
  Command <|-- SaveCommand
  Command <|-- InitCommand
  Command <|-- UndoCommand
  Command <|-- RedoCommand
}

' 会话管理模块
package "会话层" {
  class Editor {
    +String filename
    +HtmlModel model
    +CommandProcessor processor
    +Boolean modified
    +Boolean show_id
    +load(): Boolean
    +save(): Boolean
    +execute_command(command): Boolean
    +undo(): Boolean
    +redo(): Boolean
    +save_as(new_filename): Boolean
  }

  class SessionManager {
    -Dict editors
    +Editor active_editor
    -SessionState state_manager
    +restore_session(): Boolean
    +save_session(): Boolean
    +load(filename): Boolean
    +save(filename): Boolean
    +close(): Boolean
    +editor_list(): void
    +set_show_id(show): Boolean
    +get_show_id(): Boolean
    +execute_command(command): Boolean
    +get_active_model(): HtmlModel
    +get_active_processor(): CommandProcessor
  }

  class SessionState {
    -String state_file
    +load_state(): Dict
    +save_state(files, active, settings): Boolean
  }

  SessionManager "1" o-- "*" Editor
  SessionManager "1" o-- "1" SessionState
  Editor "1" *-- "1" HtmlModel
  Editor "1" *-- "1" CommandProcessor
}

' 应用层模块
package "应用层" {
  class Application {
    -SessionManager session_manager
    -CommandParser parser
    -Boolean running
    +run(): void
    +print_help(): void
    +on_command_event(event_type, kwargs): void
  }

  class CommandParser {
    +parse(command_line): Command
  }

  Application "1" *-- "1" SessionManager
  Application "1" *-- "1" CommandParser
  Application ..|> CommandObserver
}

' 主要依赖关系
HtmlValidator ..> HtmlModel : 验证 >
HtmlValidator ..> HtmlElement : 验证 >
HtmlParser ..> HtmlModel : 填充 >
HtmlParser ..> HtmlElement : 创建 >
ReadCommand ..> HtmlParser : 使用 >
SaveCommand ..> HtmlWriter : 使用 >
PrintTreeCommand ..> SpellChecker : 使用 >
SpellCheckCommand ..> SpellChecker : 使用 >
Application ..> SessionManager : 管理 >
SessionManager ..> Command : 执行 >
Command ..> HtmlModel : 修改 >

@enduml
```

## 系统架构分层

该HTML编辑器系统采用清晰的分层架构设计:

1. **核心层** - 基础数据结构和模型
2. **I/O层** - 文件读写与解析
3. **工具层** - 辅助功能模块
4. **拼写检查层** - 文本检查服务
5. **命令层** - 命令模式实现
6. **会话层** - 编辑会话管理
7. **应用层** - 程序入口和用户交互

通过这种分层设计和明确的依赖关系管理，系统实现了高内聚低耦合，使各组件能够独立开发、测试和维护。

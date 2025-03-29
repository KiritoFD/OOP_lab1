# HTML Editor Project

This project implements an interactive HTML editor with advanced features like spell checking, tree visualization, and command-based manipulation of HTML documents.

## Project Structure

### Project Tree

```
HTML Editor Project
├── src
│   ├── application
│   │   └── command_parser.py
│   ├── commands
│   │   ├── base.py
│   │   ├── command_exceptions.py
│   │   ├── display
│   │   │   ├── base.py
│   │   │   ├── dir_tree.py
│   │   │   ├── print_tree.py
│   │   │   └── spell_check.py
│   │   ├── edit
│   │   │   ├── append_command.py
│   │   │   ├── delete_command.py
│   │   │   ├── edit_id_command.py
│   │   │   ├── edit_text_command.py
│   │   │   └── insert_command.py
│   │   ├── io
│   │   │   ├── init.py
│   │   │   ├── read.py
│   │   │   └── save.py
│   │   └── observer.py
│   ├── core
│   │   ├── element.py
│   │   ├── exceptions.py
│   │   ├── html_element.py
│   │   ├── html_model.py
│   │   └── html_writer.py
│   ├── io
│   │   ├── html_writer.py
│   │   ├── parser.py
│   │   └── writer.py
│   ├── spellcheck
│   │   ├── adapters
│   │   │   └── language_tool.py
│   │   └── checker.py
│   ├── state
│   │   └── session_state.py
│   └── utils
│       └── html_utils.py
├── tests   #test部分结构与src基本照应，不再完整写出
│   ├── application
│   ├── commands
│   ├── core
│   ├── html_utils
│   ├── integration
│   ├── io
│   └── input
├── docs
├── run.py
└── requirements.txt
```

### Environment Requirements

- Python 3.9+ | Dependencies: See `requirements.txt`

### Installation & Running

```bash
pip install -r requirements.txt
python run.py                  # Normal startup
python run.py --new            # Force create a new session
python run.py file.html        # Open a specific file at startup
```

### Testing

```bash
pytest                          # Run all tests
pytest tests/core/              # Test core modules
pytest tests/commands/edit/     # Test edit commands
pytest tests/io/                # Test I/O functionality
pytest tests/spellcheck/        # Test spell checking
pytest -m unit                  # Run unit tests
pytest -m integration           # Run integration tests
pytest --cov=src tests/         # Generate test coverage report
```

## Test Coverage Report | Overall Coverage: 90%

### Full Coverage Report

```
pytest --cov . >test_out.txt
```

| File Path                                          | Statements | Missed | Coverage |
| :------------------------------------------------- | :--------: | :----: | :------: |
| cleanup_cache.py                                   |     0     |   0   |   100%   |
| conftest.py                                        |     13     |   0   |   100%   |
| main.py                                            |    161    |   30   |   81%   |
| src\__init__.py                                  |     0     |   0   |   100%   |
| src\application\__init__.py                      |     0     |   0   |   100%   |
| src\application\command_parser.py                  |     87     |   47   |   46%   |
| src\commands\__init__.py                         |     0     |   0   |   100%   |
| src\commands\base.py                               |     59     |   8   |   86%   |
| src\commands\command_exceptions.py                 |     9     |   1   |   89%   |
| src\commands\display\__init__.py                 |     0     |   0   |   100%   |
| src\commands\display\base.py                       |     0     |   0   |   100%   |
| src\commands\display\dir_tree.py                   |     0     |   0   |   100%   |
| src\commands\display\print_tree.py                 |     0     |   0   |   100%   |
| src\commands\display\spell_check.py                |     0     |   0   |   100%   |
| src\commands\display.py                            |    145    |   19   |   87%   |
| src\commands\edit\__init__.py                    |     6     |   0   |   100%   |
| src\commands\edit\append_command.py                |     52     |   4   |   92%   |
| src\commands\edit\delete_command.py                |     48     |   5   |   90%   |
| src\commands\edit\edit_id_command.py               |     56     |   11   |   80%   |
| src\commands\edit\edit_text_command.py             |     40     |   7   |   82%   |
| src\commands\edit\insert_command.py                |     73     |   17   |   77%   |
| src\commands\io\__init__.py                      |     0     |   0   |   100%   |
| src\commands\io\init.py                            |     0     |   0   |   100%   |
| src\commands\io\read.py                            |     0     |   0   |   100%   |
| src\commands\io\save.py                            |     0     |   0   |   100%   |
| src\commands\io.py                                 |    120    |   27   |   78%   |
| src\commands\observer.py                           |     5     |   1   |   80%   |
| src\core\__init__.py                             |     0     |   0   |   100%   |
| src\core\element.py                                |     48     |   17   |   65%   |
| src\core\exceptions.py                             |     20     |   2   |   90%   |
| src\core\html_element.py                           |     0     |   0   |   100%   |
| src\core\html_model.py                             |     96     |   28   |   71%   |
| src\core\html_writer.py                            |     0     |   0   |   100%   |
| src\io\__init__.py                               |     0     |   0   |   100%   |
| src\io\html_writer.py                              |     0     |   0   |   100%   |
| src\io\parser.py                                   |    125    |   48   |   62%   |
| src\io\writer.py                                   |     47     |   17   |   64%   |
| src\main.py                                        |    126    |   70   |   44%   |
| src\session_manager.py                             |    203    |   19   |   91%   |
| src\spellcheck\__init__.py                       |     0     |   0   |   100%   |
| src\spellcheck\adapters\__init__.py              |     0     |   0   |   100%   |
| src\spellcheck\adapters\language_tool.py           |     10     |   8   |   20%   |
| src\spellcheck\checker.py                          |     79     |   20   |   75%   |
| src\state\__init__.py                            |     0     |   0   |   100%   |
| src\state\session_state.py                         |     39     |   4   |   90%   |
| src\utils\html_utils.py                            |     9     |   6   |   33%   |
| tests\__init__.py                                |     0     |   0   |   100%   |
| tests\application\__init__.py                    |     0     |   0   |   100%   |
| tests\application\test_command_parser.py           |     0     |   0   |   100%   |
| tests\commands\__init__.py                       |     0     |   0   |   100%   |
| tests\commands\display\test_print_tree_command.py  |    161    |   30   |   81%   |
| tests\commands\display\test_spell_check_command.py |    135    |   3   |   98%   |
| tests\commands\edit\__init__.py                  |     0     |   0   |   100%   |
| tests\commands\edit\conftest.py                    |     7     |   0   |   100%   |
| tests\commands\edit\test_append_command.py         |    100    |   4   |   96%   |
| tests\commands\edit\test_delete_command.py         |     90     |   6   |   93%   |
| tests\commands\edit\test_edit_id_command.py        |    103    |   3   |   97%   |
| tests\commands\edit\test_edit_text_command.py      |    104    |   1   |   99%   |
| tests\commands\edit\test_insert_command.py         |     78     |   3   |   96%   |
| tests\commands\file\test_read_command.py           |     0     |   0   |   100%   |
| tests\commands\io\__init__.py                    |     0     |   0   |   100%   |
| tests\commands\io\test_io.py                       |     0     |   0   |   100%   |
| tests\commands\io\test_save_command.py             |     0     |   0   |   100%   |
| tests\conftest.py                                  |     23     |   1   |   96%   |
| tests\core\test_element.py                         |     0     |   0   |   100%   |
| tests\core\test_html_model.py                      |     0     |   0   |   100%   |
| tests\core\test_html_model_comprehensive.py        |     0     |   0   |   100%   |
| tests\core\test_parser.py                          |     0     |   0   |   100%   |
| tests\html_utils\test_html_utils.py                |     0     |   0   |   100%   |

- **print-tree** `print-tree` or `tree` - Display the current HTML in a tree structure
- **spell-check** `spell-check` - Check for spelling errors in text content
- **dir-tree** `dir-tree [directory_path]` - Display a directory in a tree structure
- **showid** `showid true|false` - Toggle display of element IDs in the tree

### I/O Commands

- **read** `read file_path` - Read HTML from a file
- **save** `save [file_path]` - Save the current HTML to a file
- **init** `init` - Create a blank HTML structure

### Undo/Redo

- **undo** `undo` - Undo the last edit operation
- **redo** `redo` - Redo the last undone operation

### Session Management Commands

- **load** `load file_path` - Open a new file or load an existing file
- **editor-list** `editor-list` or `list` - Display all open files
- **edit** `edit file_path` - Switch to a specified file
- **close** `close` - Close the current editing session
- **exit/quit** `exit` or `quit` - Exit the program
- **help** `help` - Display command help

## Notes

1. You must initialize the HTML model using `read` or `init` before using other commands.
2. I/O operations will clear the command history, making undo/redo unavailable.
3. Element IDs must be unique within the document.
4. `html`, `head`, `body`, and `title` tags automatically use their tag names as IDs.
5. The program automatically saves session state upon exit, allowing recovery on the next startup.
6. Nodes with spelling errors are marked as `[X]` in the tree view.

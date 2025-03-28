# Diff Details

Date : 2025-03-28 23:07:18

Directory c:\\Users\\xy\\Documents\\GitHub\\OOP_lab1

Total : 53 files,  -335 codes, -62 comments, -216 blanks, all -613 lines

[Summary](results.md) / [Details](details.md) / [Diff Summary](diff.md) / Diff Details

## Files
| filename | language | code | comment | blank | total |
| :--- | :--- | ---: | ---: | ---: | ---: |
| [conftest.py](/conftest.py) | Python | 11 | 1 | 2 | 14 |
| [docs/detailed\_dependencies.md](/docs/detailed_dependencies.md) | Markdown | 0 | 0 | 1 | 1 |
| [main.py](/main.py) | Python | 73 | 13 | 18 | 104 |
| [pytest.ini](/pytest.ini) | Ini | 5 | 0 | 0 | 5 |
| [src/commands/display/\_\_init\_\_.py](/src/commands/display/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [src/commands/display/base.py](/src/commands/display/base.py) | Python | 0 | 0 | 1 | 1 |
| [src/commands/display/dir\_tree.py](/src/commands/display/dir_tree.py) | Python | 0 | 0 | 1 | 1 |
| [src/commands/display/print\_tree.py](/src/commands/display/print_tree.py) | Python | 0 | 0 | 1 | 1 |
| [src/commands/display/spell\_check.py](/src/commands/display/spell_check.py) | Python | 0 | 0 | 1 | 1 |
| [src/commands/edit/append\_command.py](/src/commands/edit/append_command.py) | Python | 2 | 1 | 0 | 3 |
| [src/commands/edit/edit\_id\_command.py](/src/commands/edit/edit_id_command.py) | Python | -1 | 1 | 0 | 0 |
| [src/commands/edit/edit\_text\_command.py](/src/commands/edit/edit_text_command.py) | Python | 6 | -4 | 0 | 2 |
| [src/commands/io/\_\_init\_\_.py](/src/commands/io/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [src/commands/io/init.py](/src/commands/io/init.py) | Python | 0 | 0 | 1 | 1 |
| [src/commands/io/read.py](/src/commands/io/read.py) | Python | 0 | 0 | 1 | 1 |
| [src/commands/io/save.py](/src/commands/io/save.py) | Python | 0 | 0 | 1 | 1 |
| [src/commands/parser.py](/src/commands/parser.py) | Python | -92 | -22 | -32 | -146 |
| [src/commands/test\_dir\_tree\_command.py](/src/commands/test_dir_tree_command.py) | Python | -107 | -20 | -33 | -160 |
| [src/commands/writer.py](/src/commands/writer.py) | Python | -45 | -9 | -16 | -70 |
| [src/core/html\_element.py](/src/core/html_element.py) | Python | 0 | 0 | 1 | 1 |
| [src/core/html\_model.py](/src/core/html_model.py) | Python | 0 | 1 | 0 | 1 |
| [src/io/html\_writer.py](/src/io/html_writer.py) | Python | 0 | 0 | 1 | 1 |
| [src/io/parser.py](/src/io/parser.py) | Python | 71 | 17 | 20 | 108 |
| [src/utils/encoding\_utils.py](/src/utils/encoding_utils.py) | Python | 0 | 0 | 1 | 1 |
| [test\_comprehensive.py](/test_comprehensive.py) | Python | -530 | -94 | -178 | -802 |
| [tests/commands/display/test\_print\_tree\_command.py](/tests/commands/display/test_print_tree_command.py) | Python | 0 | 5 | 2 | 7 |
| [tests/commands/display/test\_spell\_check\_command.py](/tests/commands/display/test_spell_check_command.py) | Python | 52 | 11 | 13 | 76 |
| [tests/commands/edit/test\_append\_command.py](/tests/commands/edit/test_append_command.py) | Python | 16 | 4 | 2 | 22 |
| [tests/commands/edit/test\_delete\_command.py](/tests/commands/edit/test_delete_command.py) | Python | 19 | 7 | 0 | 26 |
| [tests/commands/edit/test\_edit\_id\_command.py](/tests/commands/edit/test_edit_id_command.py) | Python | 5 | -1 | 0 | 4 |
| [tests/commands/edit/test\_edit\_text\_command.py](/tests/commands/edit/test_edit_text_command.py) | Python | 3 | 1 | 0 | 4 |
| [tests/commands/edit/test\_insert\_command.py](/tests/commands/edit/test_insert_command.py) | Python | -54 | -15 | -24 | -93 |
| [tests/conftest.py](/tests/conftest.py) | Python | 19 | 3 | 4 | 26 |
| [tests/input/deep\_nested.html](/tests/input/deep_nested.html) | HTML | 1 | 0 | 0 | 1 |
| [tests/input/mock\_spell\_check.html](/tests/input/mock_spell_check.html) | HTML | 18 | 0 | 1 | 19 |
| [tests/input/simple\_tree.html](/tests/input/simple_tree.html) | HTML | -1 | 0 | 0 | -1 |
| [tests/input/special\_chars.html](/tests/input/special_chars.html) | HTML | 3 | 0 | 0 | 3 |
| [tests/integration/test\_comprehensive.py](/tests/integration/test_comprehensive.py) | Python | -3 | 6 | 0 | 3 |
| [tests/integration/test\_edge\_cases.py](/tests/integration/test_edge_cases.py) | Python | 24 | 5 | -3 | 26 |
| [tests/integration/test\_malformed\_html.py](/tests/integration/test_malformed_html.py) | Python | -6 | -1 | 0 | -7 |
| [tests/integration/test\_real\_world\_scenarios.py](/tests/integration/test_real_world_scenarios.py) | Python | -13 | -4 | -6 | -23 |
| [tests/io/test\_init\_command.py](/tests/io/test_init_command.py) | Python | 2 | 11 | 0 | 13 |
| [tests/io/test\_malformed\_html.py](/tests/io/test_malformed_html.py) | Python | -6 | -3 | -5 | -14 |
| [tests/io/test\_read\_command.py](/tests/io/test_read_command.py) | Python | 5 | 4 | 3 | 12 |
| [tests/io/test\_read\_input\_files.py](/tests/io/test_read_input_files.py) | Python | 4 | -2 | -2 | 0 |
| [tests/io/test\_save\_command.py](/tests/io/test_save_command.py) | Python | 0 | 1 | 0 | 1 |
| [tests/io/test\_special\_characters.py](/tests/io/test_special_characters.py) | Python | 40 | 9 | 11 | 60 |
| [tests/spellcheck/test\_spellcheck.py](/tests/spellcheck/test_spellcheck.py) | Python | -111 | -24 | -42 | -177 |
| [tests/test\_commands.py](/tests/test_commands.py) | Python | 13 | -5 | 2 | 10 |
| [tests/test\_io.py](/tests/test_io.py) | Python | 35 | 18 | 17 | 70 |
| [tests/test\_main.py](/tests/test_main.py) | Python | 299 | 31 | 42 | 372 |
| [tests/test\_model.py](/tests/test_model.py) | Python | -47 | -8 | -16 | -71 |
| [tests/test\_spellcheck.py](/tests/test_spellcheck.py) | Python | -45 | 0 | -9 | -54 |

[Summary](results.md) / [Details](details.md) / [Diff Summary](diff.md) / Diff Details
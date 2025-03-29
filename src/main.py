from src.session_manager import SessionManager
from src.commands.edit.append_command import AppendCommand
from src.commands.edit.insert_command import InsertCommand
from src.commands.edit.delete_command import DeleteCommand
from src.commands.edit.edit_text_command import EditTextCommand
from src.commands.edit.edit_id_command import EditIdCommand
from src.commands.display import PrintTreeCommand, SpellCheckCommand, DirTreeCommand
from src.state.session_state import SessionState
import sys

def print_help():
    """显示帮助信息"""
    print("\n可用命令:")
    print("  会话命令:")
    print("    load <filename.html>   - 加载HTML文件")
    print("    save [filename.html]   - 保存当前文件或另存为")
    print("    close                  - 关闭当前文件")
    print("    editor-list            - 显示打开的文件列表")
    print("    edit <filename.html>   - 切换到指定文件")
    
    print("\n  编辑命令:")
    print("    append <tag> <id> <parent_id> [text]  - 在父元素中追加子元素")
    print("    insert <tag> <id> <before_id> [text]  - 在指定元素前插入元素")
    print("    delete <id>                          - 删除元素")
    print("    edit-text <id> <text>                - 编辑元素文本")
    print("    edit-id <old_id> <new_id>            - 更改元素ID")
    
    print("\n  其他命令:")
    print("    tree                   - 显示HTML树结构")
    print("    dir-tree               - 显示当前目录结构")
    print("    spell-check            - 检查拼写错误")
    print("    undo                   - 撤销上一个操作")
    print("    redo                   - 重做上一个操作")
    print("    exit                   - 退出程序")
    print("    help                   - 显示本帮助信息")
    
    print("\n  显示选项:")
    print("    showid true|false      - 控制树形显示时是否显示ID")

def main():
    """主函数"""
    # 创建SessionManager并恢复上一次会话
    session = SessionManager()
    
    # 尝试恢复会话状态
    restored = False
    if "--new" not in sys.argv:  # 如果没有--new参数，尝试恢复会话
        restored = session.restore_session()
    
    if not restored:
        print("欢迎使用HTML编辑器!")
    else:
        print("已恢复上次会话。")
    
    print("输入'help'查看可用命令")
    
    while True:
        try:
            # 显示提示符
            prompt = f"{session.active_editor.filename if session.active_editor else 'No file'} > "
            command = input(prompt).strip().split()
            
            if not command:
                continue
                
            cmd = command[0].lower()
            args = command[1:]
            
            # 会话管理命令
            if cmd == "load" and len(args) >= 1:
                session.load(args[0])
            
            elif cmd == "save":
                if len(args) >= 1:
                    session.save(args[0])
                else:
                    session.save()
            
            elif cmd == "close":
                session.close()
            
            elif cmd == "editor-list":
                session.editor_list()
            
            elif cmd == "edit" and len(args) >= 1:
                session.edit(args[0])
            
            # 编辑命令
            elif cmd == "append" and len(args) >= 3:
                tag, id_val, parent = args[0], args[1], args[2]
                text = " ".join(args[3:]) if len(args) > 3 else None
                
                if session.active_editor:
                    command = AppendCommand(session.get_active_model(), tag, id_val, parent, text)
                    session.execute_command(command)
            
            elif cmd == "insert" and len(args) >= 3:
                tag, id_val, before = args[0], args[1], args[2]
                text = " ".join(args[3:]) if len(args) > 3 else None
                
                if session.active_editor:
                    command = InsertCommand(session.get_active_model(), tag, id_val, before, text)
                    session.execute_command(command)
            
            elif cmd == "delete" and len(args) >= 1:
                if session.active_editor:
                    command = DeleteCommand(session.get_active_model(), args[0])
                    session.execute_command(command)
            
            elif cmd == "edit-text" and len(args) >= 2:
                if session.active_editor:
                    command = EditTextCommand(session.get_active_model(), args[0], " ".join(args[1:]))
                    session.execute_command(command)
            
            elif cmd == "edit-id" and len(args) >= 2:
                if session.active_editor:
                    command = EditIdCommand(session.get_active_model(), args[0], args[1])
                    session.execute_command(command)
            
            # 处理showid命令
            elif cmd == "showid" and len(args) >= 1:
                if args[0].lower() == "true":
                    session.set_show_id(True)
                elif args[0].lower() == "false":
                    session.set_show_id(False)
                else:
                    print("无效参数。使用 'showid true' 或 'showid false'")
            
            # 其他命令
            elif cmd == "tree":
                if session.active_editor:
                    command = PrintTreeCommand(session.get_active_model())
                    session.execute_command(command)
            
            elif cmd == "dir-tree":
                command = DirTreeCommand(session)
                session.execute_command(command)
            
            elif cmd == "spell-check":
                if session.active_editor:
                    command = SpellCheckCommand(session.get_active_model())
                    session.execute_command(command)
            
            elif cmd == "undo":
                session.undo()
            
            elif cmd == "redo":
                session.redo()
            
            elif cmd == "help":
                print_help()
            
            elif cmd == "exit":
                # 保存会话状态
                session.save_session()
                
                # 检查是否有未保存的文件
                unsaved = [f for f, e in session.editors.items() if e.modified]
                if unsaved:
                    print("以下文件未保存:")
                    for f in unsaved:
                        print(f"  {f}")
                    response = input("确定要退出吗？未保存的更改将丢失。(y/n): ")
                    if response.lower() != 'y':
                        continue
                
                print("感谢使用HTML编辑器。再见!")
                break
            
            else:
                print("未知命令。输入'help'查看可用命令。")
        
        except Exception as e:
            print(f"错误: {str(e)}")

if __name__ == "__main__":
    main()

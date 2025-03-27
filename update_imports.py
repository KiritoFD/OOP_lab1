import os
import re
import sys

def update_imports(file_path):
    """更新文件中的导入语句以匹配新的文件结构"""
    print(f"更新文件: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 更新导入路径
    replacements = [
        # 命令模块更新
        (r'from src\.commands import display_commands', r'from src.commands.display import commands as display_commands'),
        (r'from src\.commands\.display_commands import (\w+)', r'from src.commands.display.commands import \1'),
        (r'from src\.commands import io_commands', r'from src.commands.io import commands as io_commands'), 
        (r'from src\.commands\.io_commands import (\w+)', r'from src.commands.io.commands import \1'),
        (r'from src\.commands import session_commands', r'from src.commands.session import commands as session_commands'),
        (r'from src\.commands\.session_commands import (\w+)', r'from src.commands.session.commands import \1'),
        
        
        # 编辑命令更新
        (r'from src\.commands\.edit\.(\w+)_command import (\w+Command)', r'from src.commands.edit.\1 import \2'),
        (r'from src\.commands\.edit import (\w+)_command', r'from src.commands.edit import \1'),
        
        # 插件导入更新
        (r'from src\.plugins import (\w+)', r'from src.plugins.\1 import \1'),
    ]
    
    # 应用所有替换
    original = content
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    # 如果文件内容有变更，写回文件
    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  - 已更新导入路径")
    else:
        print(f"  - 无需更新")

def main():
    """主函数"""
    root_dir = 'c:\\Users\\xy\\Downloads\\OOP_lab1'
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    
    print(f"开始更新导入路径，从目录: {root_dir}")
    
    # 递归处理所有Python文件
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.py'):
                update_imports(os.path.join(root, file))
    
    print("导入路径更新完成")

if __name__ == "__main__":
    main()

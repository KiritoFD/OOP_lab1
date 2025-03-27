#!/usr/bin/env python
"""
修正项目结构的脚本 - 创建必要的目录结构、移动文件并更新导入路径
"""
import os
import re
import sys
import shutil
from pathlib import Path
import argparse

# 项目根目录
ROOT_DIR = Path(r"c:\Users\xy\Downloads\OOP_lab1")

# 需要创建的目录结构
DIRECTORIES = [
    "src/commands/edit",
    "src/commands/display",
    "src/commands/io",
    "src/commands/session",
    "src/core",
    "src/plugins",
    "src/spellcheck",
    "tests/unit",
    "tests/integration",
    "docs/design",
]

# 需要移动的文件映射
FILE_MOVES = {
    # 命令文件
    "src/commands/display_commands.py": "src/commands/display/commands.py",
    "src/commands/io_commands.py": "src/commands/io/commands.py",
    "src/commands/session_commands.py": "src/commands/session/commands.py",
    
    # 测试文件
    "test_comprehensive.py": "tests/integration/test_comprehensive.py",
    "test_session.py": "tests/integration/test_session.py",
    "test_enhanced_display.py": "tests/unit/test_enhanced_display.py",
}

# 需要创建的__init__.py文件列表
INIT_FILES = [
    "src/__init__.py",
    "src/commands/__init__.py",
    "src/commands/edit/__init__.py",
    "src/commands/display/__init__.py",
    "src/commands/io/__init__.py",
    "src/commands/session/__init__.py",
    "src/core/__init__.py",
    "src/plugins/__init__.py",
    "src/spellcheck/__init__.py",
    "tests/__init__.py",
    "tests/unit/__init__.py",
    "tests/integration/__init__.py",
]

# init文件内容
INIT_CONTENT = {
    "src/__init__.py": '"""HTML编辑器源代码包"""',
    "src/commands/__init__.py": '"""命令模块包"""',
    "src/commands/edit/__init__.py": '"""编辑命令模块"""',
    "src/commands/display/__init__.py": '"""显示命令模块 - 提供HTML树形结构显示和拼写检查功能"""\nfrom src.commands.display.commands import PrintTreeCommand, SpellCheckCommand\n\n__all__ = ["PrintTreeCommand", "SpellCheckCommand"]',
    "src/commands/io/__init__.py": '"""IO命令模块"""\nfrom src.commands.io.commands import InitCommand, SaveCommand, ReadCommand\n\n__all__ = ["InitCommand", "SaveCommand", "ReadCommand"]',
    "src/commands/session/__init__.py": '"""会话管理命令模块"""\nfrom src.commands.session.commands import LoadFileCommand, SaveFileCommand, CloseFileCommand, EditorListCommand, SwitchEditorCommand, SetShowIdCommand, DirTreeCommand, SaveSessionCommand, LoadSessionCommand\n\n__all__ = ["LoadFileCommand", "SaveFileCommand", "CloseFileCommand", "EditorListCommand", "SwitchEditorCommand", "SetShowIdCommand", "DirTreeCommand", "SaveSessionCommand", "LoadSessionCommand"]',
    "src/core/__init__.py": '"""核心模型模块"""',
    "src/plugins/__init__.py": '"""插件系统模块"""',
    "src/spellcheck/__init__.py": '"""拼写检查模块"""',
    "tests/__init__.py": '"""测试包"""',
    "tests/unit/__init__.py": '"""单元测试包"""',
    "tests/integration/__init__.py": '"""集成测试包"""',
}

# 导入路径更新规则
IMPORT_REPLACEMENTS = [
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

def create_directories():
    """创建必要的目录结构"""
    print("创建目录结构...")
    for dir_path in DIRECTORIES:
        full_path = ROOT_DIR / dir_path
        if not full_path.exists():
            print(f"  创建目录: {dir_path}")
            full_path.mkdir(parents=True, exist_ok=True)
        else:
            print(f"  目录已存在: {dir_path}")

def move_files(force=False):
    """移动文件到正确的位置"""
    print("移动文件...")
    for src_path, dst_path in FILE_MOVES.items():
        src_full = ROOT_DIR / src_path
        dst_full = ROOT_DIR / dst_path
        
        if src_full.exists():
            if not dst_full.exists() or force:
                print(f"  移动: {src_path} -> {dst_path}")
                # 确保目标目录存在
                dst_full.parent.mkdir(parents=True, exist_ok=True)
                # 如果目标已存在且强制更新，先删除
                if dst_full.exists() and force:
                    dst_full.unlink()
                # 复制而不是移动，以防源文件仍然需要
                shutil.copy2(src_full, dst_full)
                print(f"    ✓ 文件已复制")
            else:
                print(f"  文件已存在于目标位置，无需移动: {dst_path}")
        else:
            print(f"  源文件不存在，跳过: {src_path}")

def create_init_files():
    """创建必要的__init__.py文件"""
    print("创建__init__.py文件...")
    for init_file in INIT_FILES:
        full_path = ROOT_DIR / init_file
        if not full_path.exists():
            print(f"  创建: {init_file}")
            # 获取自定义内容或使用默认内容
            content = INIT_CONTENT.get(init_file, f'"""{os.path.dirname(init_file).split("/")[-1]}包"""')
            full_path.write_text(content, encoding="utf-8")
        else:
            print(f"  文件已存在: {init_file}")

def update_imports():
    """更新导入路径"""
    print("更新导入路径...")
    for root, _, files in os.walk(ROOT_DIR):
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                update_file_imports(file_path)

def update_file_imports(file_path):
    """更新单个文件的导入路径"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 保存原始内容以便比较
        original = content
        
        # 应用所有替换规则
        for pattern, replacement in IMPORT_REPLACEMENTS:
            content = re.sub(pattern, replacement, content)
        
        # 如果内容有变化，写回文件
        if content != original:
            content = re.sub(pattern, replacement, content)
        
        # 如果内容有变化，写回文件
        if content != original:
            print(f"  更新导入路径: {file_path.relative_to(ROOT_DIR)}")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
    except Exception as e:
        print(f"  处理文件出错 {file_path}: {e}")

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='修正项目结构')
    parser.add_argument('--force', '-f', action='store_true', help='强制更新，覆盖现有文件')
    parser.add_argument('--verify', '-v', action='store_true', help='仅验证结构，不进行修改')
    args = parser.parse_args()    print("\n验证项目结构...")
    
    print(f"开始修正项目结构: {ROOT_DIR}")
        print("项目结构修正完成!")

























    main()if __name__ == "__main__":    print("项目结构修正完成!")        verify_structure()    # 5. 验证结构        update_imports()    # 4. 更新导入路径        move_files(force=args.force)    # 3. 移动文件        create_init_files()    # 2. 创建init文件        create_directories()    # 1. 创建目录结构            return        verify_structure()    if args.verify:    # 仅验证结构
def verify_structure():
    """验证项目结构是否正确"""
    # 检查目录是否存在
    for dir_path in DIRECTORIES:
        full_path = ROOT_DIR / dir_path
        if full_path.exists():
            print(f"  ✓ 目录存在: {dir_path}")
        else:
            print(f"  ✗ 目录不存在: {dir_path}")
    
    # 检查目标文件是否存在
    for _, dst_path in FILE_MOVES.items():
        dst_full = ROOT_DIR / dst_path
        if dst_full.exists():
            print(f"  ✓ 文件已移动: {dst_path}")
        else:
            print(f"  ✗ 文件未移动: {dst_path}")
    
    # 检查init文件是否创建
    for init_file in INIT_FILES:
        full_path = ROOT_DIR / init_file
        if full_path.exists():
            print(f"  ✓ 初始化文件存在: {init_file}")
        else:
            print(f"  ✗ 初始化文件不存在: {init_file}")

if __name__ == "__main__":
    main()

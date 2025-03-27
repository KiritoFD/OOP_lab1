#!/usr/bin/env python
"""
检查项目结构的脚本 - 验证目录结构、必要文件和导入路径
"""
import os
import sys
from pathlib import Path
import colorama
from colorama import Fore, Style

# 初始化colorama
colorama.init()

# 项目根目录
ROOT_DIR = Path(r"c:\Users\xy\Downloads\OOP_lab1")

# 应该存在的目录
EXPECTED_DIRS = [
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

# 应该存在的文件
EXPECTED_FILES = [
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
    "src/commands/display/commands.py",
    "src/commands/io/commands.py",
    "src/commands/session/commands.py"
]

# 重要的命令相关文件
KEY_COMMAND_FILES = [
    "src/commands/display/commands.py",
    "src/commands/io/commands.py", 
    "src/commands/session/commands.py"
]

def check_structure():
    """检查项目结构"""
    print(f"{Fore.BLUE}开始检查项目结构: {ROOT_DIR}{Style.RESET_ALL}")
    
    # 1. 检查目录
    print(f"\n{Fore.CYAN}检查目录结构...{Style.RESET_ALL}")
    missing_dirs = []
    
    for dir_path in EXPECTED_DIRS:
        full_path = ROOT_DIR / dir_path
        if full_path.exists():
            print(f"{Fore.GREEN}✓ {dir_path}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ {dir_path} - 目录不存在{Style.RESET_ALL}")
            missing_dirs.append(dir_path)
    
    # 2. 检查文件
    print(f"\n{Fore.CYAN}检查必要文件...{Style.RESET_ALL}")
    missing_files = []
    
    for file_path in EXPECTED_FILES:
        full_path = ROOT_DIR / file_path
        if full_path.exists():
            print(f"{Fore.GREEN}✓ {file_path}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ {file_path} - 文件不存在{Style.RESET_ALL}")
            missing_files.append(file_path)
    
    # 3. 特殊检查 - 关键命令文件内容检查
    print(f"\n{Fore.CYAN}检查关键命令文件...{Style.RESET_ALL}")
    
    for file_path in KEY_COMMAND_FILES:
        full_path = ROOT_DIR / file_path
        if full_path.exists():
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if "Command" in content and "def execute" in content:
                print(f"{Fore.GREEN}✓ {file_path} - 内容有效{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⚠ {file_path} - 可能缺少命令实现{Style.RESET_ALL}")
        
    # 总结
    print(f"\n{Fore.CYAN}检查结果摘要{Style.RESET_ALL}")
    
    if missing_dirs:
        print(f"{Fore.RED}缺失的目录: {len(missing_dirs)}{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}目录结构完整{Style.RESET_ALL}")
        
    if missing_files:
        print(f"{Fore.RED}缺失的文件: {len(missing_files)}{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}必要文件完整{Style.RESET_ALL}")
        
    return missing_dirs, missing_files

if __name__ == "__main__":
    check_structure()

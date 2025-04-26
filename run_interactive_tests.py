"""
交互式测试运行脚本 - 提供用户友好的界面来选择和运行测试
"""

import os
import sys
import time
import subprocess
import platform
import glob
import re
from datetime import datetime

def clear_screen():
    """清除终端屏幕"""
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def display_header():
    """显示程序标题"""
    clear_screen()
    print("=" * 80)
    print(f"{'HTML编辑器测试运行程序':^80}")
    print(f"{'v1.0.0':^80}")
    print("=" * 80)
    print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"Python版本: {platform.python_version()}")
    print("=" * 80)
    print()

def display_main_menu():
    """显示主菜单"""
    print("\n请选择测试类型：")
    print("  [1] 运行所有测试")
    print("  [2] 运行单元测试")
    print("  [3] 运行集成测试")
    print("  [4] 运行系统测试")
    print("  [5] 选择特定模块测试")
    print("  [6] 高级选项")
    print("  [0] 退出")
    print()
    
    return input("请输入选项 [0-6]: ").strip()

def display_module_menu():
    """显示模块选择菜单"""
    clear_screen()
    print("\n请选择要测试的模块：")
    print("  [1] 核心模块 (core)")
    print("  [2] 命令模块 (commands)")
    print("  [3] IO模块 (io)")
    print("  [4] 工具模块 (utils)")
    print("  [5] 会话模块 (session)")
    print("  [6] 拼写检查模块 (spellcheck)")
    print("  [7] 选择特定测试文件")
    print("  [0] 返回主菜单")
    print()
    
    return input("请输入选项 [0-7]: ").strip()

def find_test_files(directory):
    """查找给定目录下的所有测试文件"""
    test_files = []
    pattern = os.path.join(directory, "**", "test_*.py")
    for file_path in glob.glob(pattern, recursive=True):
        # 将文件路径转换为相对于项目根目录的路径
        rel_path = os.path.relpath(file_path, os.getcwd())
        test_files.append(rel_path)
    return sorted(test_files)

def find_test_classes_in_file(file_path):
    """在测试文件中查找所有测试类"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 使用正则表达式查找类定义
    class_pattern = r'class\s+(\w+)[^\n]*:'
    classes = re.findall(class_pattern, content)
    # 仅返回以Test开头的类名
    test_classes = [cls for cls in classes if cls.startswith('Test')]
    return test_classes

def find_test_methods_in_file(file_path, class_name):
    """在测试文件中查找指定类的所有测试方法"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找类定义和它的内容
    class_pattern = f"class\\s+{class_name}[^\\n]*:([\\s\\S]*?)(?:class\\s|$)"
    class_match = re.search(class_pattern, content)
    
    if not class_match:
        return []
    
    class_content = class_match.group(1)
    
    # 查找测试方法
    method_pattern = r'def\s+(test_\w+)\s*\('
    methods = re.findall(method_pattern, class_content)
    return methods

def display_test_class_menu(file_path):
    """显示测试文件中的测试类选择菜单"""
    test_classes = find_test_classes_in_file(file_path)
    
    if not test_classes:
        print("\n该文件中未找到测试类！")
        return None
    
    clear_screen()
    print(f"\n文件: {file_path}")
    print("\n请选择要运行的测试类：")
    
    for i, class_name in enumerate(test_classes, 1):
        print(f"  [{i}] {class_name}")
    
    print("  [0] 返回上一级菜单")
    print()
    
    choice = input(f"请输入选项 [0-{len(test_classes)}]: ").strip()
    
    try:
        choice = int(choice)
        if 1 <= choice <= len(test_classes):
            return test_classes[choice-1]
        elif choice == 0:
            return None
        else:
            print("\n无效选项！请重新选择。")
            return None
    except ValueError:
        print("\n无效输入！请输入数字。")
        return None

def display_test_method_menu(file_path, class_name):
    """显示测试类中的测试方法选择菜单"""
    test_methods = find_test_methods_in_file(file_path, class_name)
    
    if not test_methods:
        print(f"\n类 {class_name} 中未找到测试方法！")
        return None
    
    clear_screen()
    print(f"\n文件: {file_path}")
    print(f"类: {class_name}")
    print("\n请选择要运行的测试方法：")
    print(f"  [A] 运行所有方法")
    
    for i, method_name in enumerate(test_methods, 1):
        print(f"  [{i}] {method_name}")
    
    print("  [0] 返回上一级菜单")
    print()
    
    choice = input(f"请输入选项 [0-{len(test_methods)}/A]: ").strip()
    
    if choice.upper() == 'A':
        return "ALL"
    
    try:
        choice = int(choice)
        if 1 <= choice <= len(test_methods):
            return test_methods[choice-1]
        elif choice == 0:
            return None
        else:
            print("\n无效选项！请重新选择。")
            return None
    except ValueError:
        print("\n无效输入！请输入数字或'A'。")
        return None

def run_command(command):
    """运行命令并等待完成"""
    print("\n" + "=" * 80)
    print(f"执行命令: {' '.join(command)}")
    print("=" * 80)
    print()
    
    start_time = time.time()
    result = subprocess.run(command)
    elapsed_time = time.time() - start_time
    
    print("\n" + "=" * 80)
    print(f"命令执行完成 - 耗时: {elapsed_time:.2f} 秒")
    print(f"退出代码: {result.returncode} ({'成功' if result.returncode == 0 else '失败'})")
    print("=" * 80)
    
    return result.returncode

def run_python_script(script, args=None):
    """运行Python脚本"""
    command = [sys.executable, script]
    if args:
        command.extend(args)
    return run_command(command)

def wait_for_user():
    """等待用户按任意键继续"""
    print("\n按回车键继续...")
    input()

def run_test_by_type(test_type, verbose=True):
    """根据测试类型运行测试"""
    command = [sys.executable, "-m", "pytest"]
    
    # 根据测试类型选择测试目录
    if test_type == "all":
        command.append("tests/")
    elif test_type == "unit":
        command.append("tests/unit/")
    elif test_type == "integration":
        command.append("tests/integration/")
    elif test_type == "system":
        command.append("tests/system/")
    
    if verbose:
        command.append("-v")
        
    return run_command(command)

def run_test_by_module(module, verbose=True):
    """根据模块运行测试"""
    command = [sys.executable, "-m", "pytest"]
    
    # 定位模块测试路径
    if module.startswith("commands/"):
        # 特殊处理命令子模块
        submodule = module.split('/')[1]
        test_path = f"tests/unit/commands/{submodule}"
    else:
        test_path = f"tests/unit/{module}"
    
    command.append(test_path)
    
    if verbose:
        command.append("-v")
        
    return run_command(command)

def run_specific_test_method(file_path, class_name, method_name=None):
    """运行特定的测试方法"""
    command = [sys.executable, "-m", "pytest", file_path]
    
    # 如果指定了方法，添加到命令中
    if method_name and method_name != "ALL":
        command.append(f"{class_name}::{method_name}")
    elif class_name:
        command.append(f"{class_name}")
    
    command.append("-v")
    return run_command(command)

def run_specific_test_file(file_path, verbose=True):
    """运行特定的测试文件，可选择特定类和方法"""
    # 选择测试类
    class_name = display_test_class_menu(file_path)
    if class_name is None:
        return
    
    # 选择测试方法
    method_name = display_test_method_menu(file_path, class_name)
    if method_name is None:
        return
    
    # 运行选择的测试
    run_specific_test_method(file_path, class_name, method_name)

def display_test_file_menu(test_files):
    """显示测试文件选择菜单"""
    clear_screen()
    print("\n请选择要运行的测试文件：")
    
    for i, file_path in enumerate(test_files, 1):
        print(f"  [{i}] {file_path}")
    
    print("  [0] 返回上一级菜单")
    print()
    
    choice = input(f"请输入选项 [0-{len(test_files)}]: ").strip()
    
    try:
        choice = int(choice)
        if 1 <= choice <= len(test_files):
            return test_files[choice-1]
        elif choice == 0:
            return None
        else:
            print("\n无效选项！请重新选择。")
            return None
    except ValueError:
        print("\n无效输入！请输入数字。")
        return None

def display_advanced_menu():
    """显示高级选项菜单"""
    clear_screen()
    print("\n高级测试选项：")
    print("  [1] 运行所有测试(带覆盖率报告)")
    print("  [2] 运行所有测试(生成HTML报告)")
    print("  [3] 运行所有测试(快速失败模式)")
    print("  [4] 运行测试并分析测试结构")
    print("  [5] 清理旧的测试报告")
    print("  [6] 运行性能测试")
    print("  [7] 运行压力测试")
    print("  [0] 返回主菜单")
    print()
    
    return input("请输入选项 [0-7]: ").strip()

def run_test_with_coverage():
    """运行全部测试并生成覆盖率报告"""
    command = [sys.executable, "-m", "pytest", "tests/", "-v", "--cov=src", "--cov-report=term", "--cov-report=html:reports/coverage"]
    return run_command(command)

def run_test_with_html_report():
    """运行测试并生成HTML报告"""
    # 确保reports目录存在
    os.makedirs("reports/html", exist_ok=True)
    command = [sys.executable, "-m", "pytest", "tests/", "-v", "--html=reports/html/report.html"]
    return run_command(command)

def run_test_fail_fast():
    """快速失败模式运行测试"""
    command = [sys.executable, "-m", "pytest", "tests/", "-v", "-xvs"]
    return run_command(command)

def analyze_tests():
    """分析测试结构"""
    print("\n正在分析测试结构...")
    
    test_files = find_test_files("tests")
    
    # 统计数据
    total_files = len(test_files)
    unit_tests = len([f for f in test_files if "/unit/" in f.replace("\\", "/")])
    integration_tests = len([f for f in test_files if "/integration/" in f.replace("\\", "/")])
    system_tests = len([f for f in test_files if "/system/" in f.replace("\\", "/")])
    
    # 显示分析结果
    print(f"\n发现测试文件总数: {total_files}")
    print(f"单元测试文件: {unit_tests}")
    print(f"集成测试文件: {integration_tests}")
    print(f"系统测试文件: {system_tests}")
    
    # 统计测试方法
    test_methods = 0
    for file_path in test_files:
        test_classes = find_test_classes_in_file(file_path)
        for class_name in test_classes:
            methods = find_test_methods_in_file(file_path, class_name)
            test_methods += len(methods)
    
    print(f"测试方法总数: {test_methods}")
    return 0

def clean_reports():
    """清理旧的测试报告"""
    report_dirs = ["reports/coverage", "reports/html"]
    
    for directory in report_dirs:
        if os.path.exists(directory):
            print(f"清理目录: {directory}")
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        import shutil
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"清理文件失败: {file_path} - {e}")
    
    print("清理完成!")
    return 0

def main():
    """主函数"""
    while True:
        display_header()
        choice = display_main_menu()
        
        if choice == "0":
            print("\n感谢使用测试运行程序，再见！")
            break
            
        elif choice == "1":
            run_test_by_type("all")
            
        elif choice == "2":
            run_test_by_type("unit")
            
        elif choice == "3":
            run_test_by_type("integration")
            
        elif choice == "4":
            run_test_by_type("system")
            
        elif choice == "5":
            module_choice = display_module_menu()
            module_map = {
                "1": "core",
                "2": "commands",
                "3": "io",
                "4": "utils", 
                "5": "session",
                "6": "commands/spellcheck"
            }
            
            if module_choice in module_map:
                run_test_by_module(module_map[module_choice])
            elif module_choice == "7":
                # 选择特定测试文件
                test_files = find_test_files("tests")
                if test_files:
                    selected_file = display_test_file_menu(test_files)
                    if selected_file:
                        run_specific_test_file(selected_file)
                else:
                    print("\n未找到测试文件！")
            elif module_choice != "0":
                print("\n无效选项！请重新选择。")
                
        elif choice == "6":
            advanced_choice = display_advanced_menu()
            
            if advanced_choice == "1":
                run_test_with_coverage()
                
            elif advanced_choice == "2":
                run_test_with_html_report()
                
            elif advanced_choice == "3":
                run_test_fail_fast()
                
            elif advanced_choice == "4":
                analyze_tests()
                
            elif advanced_choice == "5":
                clean_reports()
                
            elif advanced_choice == "6":
                print("\n运行性能测试...")
                if os.path.exists("tests/performance"):
                    run_command([sys.executable, "-m", "pytest", "tests/performance", "-v"])
                else:
                    print("\n性能测试目录不存在！")
                
            elif advanced_choice == "7":
                print("\n运行压力测试...")
                if os.path.exists("tests/stress"):
                    run_command([sys.executable, "-m", "pytest", "tests/stress", "-v"])
                else:
                    print("\n压力测试目录不存在！")
                
            elif advanced_choice != "0":
                print("\n无效选项！请重新选择。")
                
        else:
            print("\n无效选项！请重新选择。")
            
        wait_for_user()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断。")
        sys.exit(0)
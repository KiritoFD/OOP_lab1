from typing import List, Dict, Any
from abc import ABC, abstractmethod

class SpellErrorReporter(ABC):
    """拼写错误报告接口"""
    @abstractmethod
    def report_errors(self, errors: List[Dict[str, Any]]) -> None:
        """报告拼写错误
        
        Args:
            errors: 错误信息列表，每个错误是一个包含'error'、'element_id'和'path'的字典
        """
        pass

class ConsoleReporter(SpellErrorReporter):
    """控制台报告器，将拼写错误输出到控制台"""
    def report_errors(self, errors: List[Dict[str, Any]]) -> None:
        """将错误输出到控制台"""
        if not errors:
            print("拼写检查通过，未发现错误。")
            return
            
        print(f"拼写检查完成，发现 {len(errors)} 个可能的拼写错误:")
        
        for i, error_info in enumerate(errors, 1):
            error = error_info['error']
            print(f"{i}. 拼写错误: '{error.wrong_word}'")
            if error.suggestions:
                print(f"   建议修改: {', '.join(error.suggestions[:5])}")
            print(f"   元素: {error_info['path']} (id={error_info['element_id']})")
            print(f"   上下文: \"{error.context}\"")
            print()

class FileReporter(SpellErrorReporter):
    """文件报告器，将拼写错误保存到文件"""
    def __init__(self, file_path: str):
        """初始化文件报告器
        
        Args:
            file_path: 输出文件路径
        """
        self.file_path = file_path
        
    def report_errors(self, errors: List[Dict[str, Any]]) -> None:
        """将错误保存到文件"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                if not errors:
                    f.write("拼写检查通过，未发现错误。\n")
                    return
                    
                f.write(f"拼写检查完成，发现 {len(errors)} 个可能的拼写错误:\n\n")
                
                for i, error_info in enumerate(errors, 1):
                    error = error_info['error']
                    f.write(f"{i}. 拼写错误: '{error.wrong_word}'\n")
                    if error.suggestions:
                        f.write(f"   建议修改: {', '.join(error.suggestions[:5])}\n")
                    f.write(f"   元素: {error_info['path']} (id={error_info['element_id']})\n")
                    f.write(f"   上下文: \"{error.context}\"\n\n")
                    
            print(f"拼写检查结果已保存到文件: {self.file_path}")
            
        except Exception as e:
            print(f"Error writing to file {self.file_path}: {e}")
            # 如果文件写入失败，退回到控制台输出
            ConsoleReporter().report_errors(errors)

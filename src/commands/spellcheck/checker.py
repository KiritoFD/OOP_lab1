from abc import ABC, abstractmethod
from typing import List, Dict, Any, Set, Optional, Tuple
from dataclasses import dataclass
import re
import os
import json
from spellchecker import SpellChecker as PySpellChecker

class SpellError:
    """表示一个拼写错误"""
    
    def __init__(self, wrong_word, suggestions, context, start, end):
        """初始化拼写错误对象
        
        Args:
            wrong_word (str): 拼写错误的单词
            suggestions (list): 建议的正确拼写列表
            context (str): 错误单词的上下文
            start (int): 错误在文本中的起始位置
            end (int): 错误在文本中的结束位置
        """
        self.wrong_word = wrong_word
        self.suggestions = suggestions
        self.context = context
        self.start = start
        self.end = end
        
    def __str__(self):
        return f"拼写错误: '{self.wrong_word}', 建议: {', '.join(self.suggestions)}"

class SpellChecker:
    """拼写检查器实现"""
    
    def __init__(self, language="en", custom_dict=None):
        """初始化拼写检查器
        
        Args:
            language (str): 语言代码
            custom_dict (dict, optional): 自定义字典
        """
        self.checker = PySpellChecker(language=language)
        
        # 加载字典文件
        try:
            dictionary_path = os.path.join("resources", "dictionary.txt")
            if os.path.exists(dictionary_path):
                with open(dictionary_path, 'r', encoding='utf-8') as f:
                    custom_words = [line.strip() for line in f if line.strip()]
                    self.checker.word_frequency.load_words(custom_words)
        except Exception as e:
            print(f"Warning: Could not load dictionary: {e}")
        
        # 如果有自定义字典，直接添加到库的词典中
        if custom_dict:
            self.checker.word_frequency.load_words(list(custom_dict.keys()))
            
    def check_text(self, text: str) -> List[SpellError]:
        """检查文本拼写错误
        
        Args:
            text (str): 要检查的文本
            
        Returns:
            list: SpellError对象列表
        """
        if not text:
            return []
            
        # 提取文本中的单词
        words_with_positions = []
        for match in re.finditer(r'\b[a-zA-Z]+\b', text):
            word = match.group()
            start, end = match.span()
            words_with_positions.append((word, start, end))
        
        # 提取所有单词
        words = [word for word, _, _ in words_with_positions]
        
        # 使用库的unknown()方法直接获取所有拼写错误的单词
        misspelled = self.checker.unknown(words)
        
        errors = []
        # 处理每个拼写错误
        for word, start, end in words_with_positions:
            if word in misspelled:
                # 直接使用库的candidates()方法获取建议
                suggestions = list(self.checker.candidates(word))
                
                # 确保最佳纠正在前面
                correction = self.checker.correction(word)
                if correction in suggestions:
                    suggestions.remove(correction)
                    suggestions.insert(0, correction)
                
                # 获取上下文
                context_start = max(0, start - 30)
                context_end = min(len(text), end + 30)
                context = text[context_start:context_end]
                
                # 创建错误对象
                error = SpellError(
                    wrong_word=word,
                    suggestions=suggestions,
                    context=context,
                    start=start,
                    end=end
                )
                errors.append(error)
                
        return errors
    
    def check_element(self, element):
        """
        检查HTML元素中的文本拼写错误
        
        Args:
            element: HTML元素
            
        Returns:
            list: 拼写错误列表
        """
        if not element.text:
            return []
        
        return self.check_text(element.text)
    
    # 其他方法直接传递到库的方法
    def add_word(self, word: str):
        """添加单词到字典"""
        self.checker.word_frequency.add(word)
        
    def add_words(self, words: List[str]):
        """批量添加单词到字典"""
        self.checker.word_frequency.load_words(words)
    
    def get_word_probability(self, word: str) -> float:
        """获取单词的概率"""
        return self.checker.word_probability(word)
        
    def get_correction(self, word: str) -> str:
        """获取单词的最佳纠正建议"""
        return self.checker.correction(word)

class SpellErrorReporter:
    """拼写错误报告接口"""
    
    def report_errors(self, errors):
        """报告拼写错误
        
        Args:
            errors (list): 错误列表
        """
        raise NotImplementedError("子类必须实现此方法")
    
    # 添加兼容方法
    def report(self, errors):
        """兼容性方法，调用report_errors
        
        Args:
            errors (list): 错误列表
        """
        return self.report_errors(errors)

class ConsoleReporter(SpellErrorReporter):
    """控制台拼写错误报告器"""
    
    def report_errors(self, errors):
        """在控制台输出拼写错误报告
        
        Args:
            errors (list): 错误对象列表或错误字典列表
        """
        if not errors:
            print("未发现拼写错误。")
            return
            
        # 处理两种格式的错误: SpellError对象列表或包含SpellError的字典列表
        for i, error_item in enumerate(errors):
            # 检查这是直接的SpellError对象还是包含error的字典
            if isinstance(error_item, dict):
                # 旧格式 - 字典格式
                error = error_item['error']
                element_id = error_item.get('element_id', 'unknown')
                path = error_item.get('path', '')
            else:
                # 新格式 - 直接是SpellError对象
                error = error_item
                element_id = 'unknown'  # 无法获取元素ID
                path = ''               # 无法获取路径
            
            print(f"发现拼写错误:")
            print(f"\n{i+1}. 位置: {path} (ID: {element_id})")
            print(f"   错误: '{error.wrong_word}'")
            
            if error.suggestions:
                print(f"   建议: {', '.join(error.suggestions)}")
            
            # 显示上下文，高亮错误单词
            context = error.context
            if len(context) > 60:
                # 仅显示错误周围的文本
                start = max(0, error.start - 20)
                end = min(len(context), error.end + 20)
                prefix = "..." if start > 0 else ""
                suffix = "..." if end < len(context) else ""
                displayed_context = prefix + context[start:end] + suffix
            else:
                displayed_context = context
                
            print(f"   上下文: {displayed_context}")
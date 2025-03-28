from abc import ABC, abstractmethod
from typing import List, Dict, Any, Set, Optional
from dataclasses import dataclass
import re
import os
import json

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
    """拼写检查器"""
    
    def __init__(self, language="en_US", custom_dict=None):
        """初始化拼写检查器
        
        Args:
            language (str): 语言代码
            custom_dict (dict, optional): 自定义字典
        """
        self.language = language
        self.custom_dict = custom_dict or {}
        # 尝试导入拼写检查库，如果不可用则使用简单实现
        try:
            from spellcheck import SpellChecker as PySpellChecker
            self.checker = PySpellChecker(language=language)
            self.has_library = True
        except ImportError:
            self.checker = None
            self.has_library = False
            print("警告: 没有找到拼写检查库，将使用简单实现。")
            
    def check_text(self, text):
        """检查文本拼写错误
        
        Args:
            text (str): 要检查的文本
            
        Returns:
            list: SpellError对象列表
        """
        if not text:
            return []
            
        errors = []
        
        if self.has_library:
            # 使用外部库进行检查
            words = text.split()
            for i, word in enumerate(words):
                # 清理单词，移除标点符号
                clean_word = word.strip('.,;:!?()"\'')
                if not clean_word:
                    continue
                    
                # 检查单词是否拼写正确
                if clean_word not in self.custom_dict and self.checker.correction(clean_word) != clean_word:
                    # 找到错误单词在原始文本中的位置
                    start = text.find(word)
                    end = start + len(word)
                    
                    # 获取建议
                    suggestions = list(self.checker.candidates(clean_word))
                    
                    # 创建并添加错误
                    error = SpellError(clean_word, suggestions, text, start, end)
                    errors.append(error)
        else:
            # 简单实现：使用预定义的拼写错误列表
            common_errors = {
                "teh": ["the"],
                "thier": ["their"],
                "recieve": ["receive"],
                "wierd": ["weird"],
                "beleive": ["believe"],
                "seperate": ["separate"],
                "occured": ["occurred"],
                "truely": ["truly"],
                "greatful": ["grateful"],
                "accomodate": ["accommodate"],
                "adress": ["address"],
                "begining": ["beginning"],
                "catagory": ["category"],
                "definately": ["definitely"],
                "embarass": ["embarrass"],
                "existance": ["existence"],
                "favourit": ["favorite"],
                "grammer": ["grammar"],
                "immediatly": ["immediately"],
                "independant": ["independent"],
                "millenium": ["millennium"],
                "neccessary": ["necessary"],
                "occassionly": ["occasionally"],
                "oppurtunity": ["opportunity"],
                "posession": ["possession"],
                "prefered": ["preferred"],
                "reccomend": ["recommend"],
                "refering": ["referring"],
                "relevent": ["relevant"],
                "succesful": ["successful"],
                "tommorow": ["tomorrow"],
                "untill": ["until"],
                "whereever": ["wherever"],
                "wierd": ["weird"],
                "yatch": ["yacht"],
                "misspellng": ["misspelling"],
                "paragreph": ["paragraph"]
            }
            
            words = text.lower().split()
            for word in words:
                clean_word = word.strip('.,;:!?()"\'')
                if clean_word in common_errors:
                    start = text.lower().find(clean_word)
                    end = start + len(clean_word)
                    error = SpellError(clean_word, common_errors[clean_word], text, start, end)
                    errors.append(error)
                    
        return errors

class SpellErrorReporter:
    """拼写错误报告接口"""
    
    def report_errors(self, errors):
        """报告拼写错误
        
        Args:
            errors (list): 错误列表
        """
        raise NotImplementedError("子类必须实现此方法")

class ConsoleReporter(SpellErrorReporter):
    """控制台拼写错误报告器"""
    
    def report_errors(self, errors):
        """在控制台输出拼写错误报告
        
        Args:
            errors (list): 错误字典列表
        """
        if not errors:
            print("未发现拼写错误。")
            return
            
        print(f"发现 {len(errors)} 个拼写错误:")
        
        for i, error_dict in enumerate(errors):
            error = error_dict['error']
            element_id = error_dict['element_id']
            path = error_dict['path']
            
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
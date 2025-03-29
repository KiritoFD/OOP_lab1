from typing import List
from spellchecker import SpellChecker as PySpellChecker
from ..checker import SpellChecker, SpellError

class LanguageToolAdapter(SpellChecker):
    """SpellChecker拼写检查适配器"""
    
    def __init__(self):
        # 初始化PySpellChecker实例
        self.tool = PySpellChecker()
        
    def check_text(self, text) -> List[SpellError]:
        # 首先检查text是否为None
        if text is None:
            return []
            
        # 然后确保text是字符串类型
        if not isinstance(text, str):
            text = str(text)
            
        # 最后检查是否为空字符串
        if not text:
            return []
            
        # 使用PySpellChecker检查文本拼写
        errors = []
        words = text.split()
        for word in words:
            # 检查单词是否拼写错误
            if word.lower() not in self.tool:
                # 获取拼写建议
                suggestions = list(self.tool.candidates(word))
                # 找到单词在文本中的位置
                start = text.find(word)
                end = start + len(word)
                # 创建SpellError对象 - 根据构造函数修改参数顺序
                # 假设SpellError的构造函数为 __init__(self, misspelled_word, suggestions, context, start_pos, end_pos)
                errors.append(SpellError(
                    word,           # 错误单词
                    suggestions,    # 建议列表
                    text,           # 上下文
                    start,          # 开始位置
                    end             # 结束位置
                ))
        return errors

    def check(self, text) -> List[SpellError]:
        """与check_text相同功能，满足测试接口要求"""
        return self.check_text(text)
        
    def __del__(self):
        # 清理资源（PySpellChecker不需要特殊清理）
        pass
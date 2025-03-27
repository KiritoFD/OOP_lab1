from typing import List

class SpellError:
    """表示拼写错误的类"""
    
    def __init__(self, word: str, suggestions: List[str], context: str, start_pos: int, end_pos: int):
        """初始化拼写错误
        
        Args:
            word: 错误的单词
            suggestions: 建议的正确拼写列表
            context: 错误单词所在的上下文
            start_pos: 错误单词在上下文中的起始位置
            end_pos: 错误单词在上下文中的结束位置
        """
        self.word = word
        self.suggestions = suggestions
        self.context = context
        self.start_pos = start_pos
        self.end_pos = end_pos
        
    def __str__(self):
        """返回拼写错误的字符串表示"""
        suggestions_str = ", ".join(self.suggestions) if self.suggestions else "无建议"
        return f"拼写错误: '{self.word}' (建议: {suggestions_str})"
        
    def get_highlighted_context(self):
        """返回带有高亮错误单词的上下文
        
        Returns:
            带有高亮错误单词的上下文，错误单词被 ** 包围
        """
        if not self.context:
            return ""
            
        prefix = self.context[:self.start_pos]
        error_word = self.context[self.start_pos:self.end_pos]
        suffix = self.context[self.end_pos:]
        
        return f"{prefix}**{error_word}**{suffix}"

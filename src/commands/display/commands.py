"""
显示相关命令的实现
"""
from src.commands.base import Command
from src.spell.checker import SpellChecker

class PrintTreeCommand(Command):
    """Display the HTML tree structure"""
    
    def __init__(self, model, show_id=True, spell_checker=None):
        self.model = model
        self.show_id = show_id
        self.spell_checker = spell_checker
    
    def _print_tree(self, element, indent=0):
        # Check if element has spelling errors
        has_spell_error = False
        if self.spell_checker and element.text:
            errors = self.spell_checker.check_text(element.text)
            has_spell_error = len(errors) > 0
        
        # Prepare the element display string
        prefix = "[X] " if has_spell_error else ""
        id_suffix = f" #{element.id}" if self.show_id and element.id else ""
        
        # Print the current element
        print(f"{' ' * indent}{prefix}<{element.tag}>{id_suffix}")
        
        # Print children recursively
        for child in element.children:
            self._print_tree(child, indent + 2)
    
    def execute(self):
        # Get the root element and print the tree
        root = self.model.find_by_id('html')
        if root:
            print("\n--- HTML Tree ---")
            self._print_tree(root)
            print("-----------------")
            return True
        return False
    
    def undo(self):
        # This is a display command, no need to undo
        return False

class SpellCheckCommand(Command):
    """Check the spelling of text in the HTML document"""
    
    def __init__(self, model):
        self.model = model
        self.checker = SpellChecker()
    
    def _check_element(self, element, errors):
        # Check this element's text
        if element.text:
            element_errors = self.checker.check_text(element.text)
            if element_errors:
                errors[element.id] = element_errors
        
        # Check all children recursively
        for child in element.children:
            self._check_element(child, errors)
    
    def execute(self):
        errors = {}
        root = self.model.find_by_id('html')
        self._check_element(root, errors)
        
        # Print the errors
        if errors:
            print("\n--- Spelling Errors ---")
            for element_id, element_errors in errors.items():
                for error in element_errors:
                    print(f"Element '{element_id}': '{error.word}' (Suggestions: {', '.join(error.suggestions)})")
            print("----------------------")
        else:
            print("\nNo spelling errors found.")
        
        return True
    
    def undo(self):
        # This is a display command, no need to undo
        return False

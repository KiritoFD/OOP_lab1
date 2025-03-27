from src.core.exceptions import HTMLEditorError

class CommandException(HTMLEditorError):
    """Base class for command-related exceptions."""
    pass

class CommandExecutionError(CommandException):
    """Exception raised when a command fails to execute."""
    def __init__(self, message="Command execution failed"):
        super().__init__(message)

class CommandParameterError(CommandException):
    """Exception raised when a command has invalid parameters."""
    def __init__(self, message="Invalid command parameters"):
        super().__init__(message)

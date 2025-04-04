"""Common imports for tests"""

# Standard library imports
from typing import List, Dict, Set, Tuple, Optional, Any, Union, Callable, TypeVar, Generic, Iterable
import os
import sys
import json
import re
import unittest
import pytest
from unittest.mock import patch, MagicMock, Mock, call

# Project imports
from src.core.exceptions import (
    InvalidOperationError, 
    ElementNotFoundError,
    DuplicateIdError
)
from src.commands.command_exceptions import CommandExecutionError, CommandParameterError

__all__ = [
    # Standard types
    'List', 'Dict', 'Set', 'Tuple', 'Optional', 'Any', 'Union',
    'Callable', 'TypeVar', 'Generic', 'Iterable',
    
    # Standard modules
    'os', 'sys', 'json', 're', 'unittest', 'pytest',
    
    # Mock utilities
    'patch', 'MagicMock', 'Mock', 'call',
    
    # Project exceptions
    'InvalidOperationError', 'ElementNotFoundError', 'DuplicateIdError',
    'CommandExecutionError', 'CommandParameterError'
]

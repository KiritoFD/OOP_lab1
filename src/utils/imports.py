"""Common imports used across the project"""

# Standard library imports
from typing import List, Dict, Set, Tuple, Optional, Any, Union, Callable, TypeVar, Generic, Iterable
import os
import sys
import json
import re
import time
import datetime
import logging
from pathlib import Path

# Common exception types
from src.core.exceptions import (
    InvalidOperationError,
    ElementNotFoundError,
    DuplicateIdError,
    CommandExecutionError
)

__all__ = [
    # Standard types
    'List', 'Dict', 'Set', 'Tuple', 'Optional', 'Any', 'Union',
    'Callable', 'TypeVar', 'Generic', 'Iterable',
    
    # Standard modules
    'os', 'sys', 'json', 're', 'time', 'datetime', 'logging', 'Path',
    
    # Project exceptions
    'InvalidOperationError', 'ElementNotFoundError', 'DuplicateIdError', 'CommandExecutionError'
]

"""
AI Tools GUI Automation Package

Automate artifact generation across AI platforms.
"""

__version__ = "1.0.0"
__author__ = "AI Tools GUI Automation Team"

from .markdown_parser import MarkdownParser, Artifact
from .file_manager import FileManager
from .base_provider import BaseAIProvider
from .gemini_provider import GeminiProvider
from .chatgpt_provider import ChatGPTProvider
from .claude_provider import ClaudeProvider

__all__ = [
    'MarkdownParser',
    'Artifact',
    'FileManager',
    'BaseAIProvider',
    'GeminiProvider',
    'ChatGPTProvider',
    'ClaudeProvider'
]

"""
AI Module for SCDO
Simplified with Gemini + Granite only
"""

from .model_manager import ModelManager
from .base_model import BaseAIModel
from .granite_model import GraniteModel
from .gemini_model import GeminiModel

__all__ = [
    'ModelManager',
    'BaseAIModel',
    'GraniteModel',
    'GeminiModel',
]

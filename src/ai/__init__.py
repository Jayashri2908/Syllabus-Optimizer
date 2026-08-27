"""
AI Module for SCDO
OpenRouter (primary) + Gemini (fallback)
"""

from .model_manager import ModelManager
from .base_model import BaseAIModel
from .openrouter_model import OpenRouterModel
from .gemini_model import GeminiModel

__all__ = [
    'ModelManager',
    'BaseAIModel',
    'OpenRouterModel',
    'GeminiModel',
]

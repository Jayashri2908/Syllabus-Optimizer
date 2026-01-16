"""
Base AI Model Interface for SCDO
Supports multiple FREE AI providers
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, List
import logging


class BaseAIModel(ABC):
    """Abstract base class for AI model providers"""
    
    def __init__(self, config: Dict = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config or {}
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Generate text from prompt
        
        Args:
            prompt: User prompt
            system_prompt: System/instruction prompt
            temperature: Generation temperature (0-1)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this model is available/configured"""
        pass
    
    def get_model_info(self) -> Dict:
        """Get information about this model"""
        return {
            'name': self.__class__.__name__,
            'provider': 'unknown',
            'cost': 'free',
            'available': self.is_available()
        }

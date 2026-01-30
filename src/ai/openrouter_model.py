"""
OpenRouter Model - Access MiMo and 300+ AI Models
Unified API for multiple providers (Xiaomi MiMo, OpenAI, Anthropic, etc.)
"""

import os
from typing import Optional
from .base_model import BaseAIModel

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OpenRouterModel(BaseAIModel):
    """OpenRouter - Unified access to MiMo-V2-Flash and other models"""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.api_key = os.getenv('OPENROUTER_API_KEY', self.config.get('api_key'))
        # Default to Nvidia Nemotron (Free)
        self.model_name = self.config.get('model', 'nvidia/nemotron-3-nano-30b-a3b:free')
        self.client = None
        
        if self.api_key and OPENAI_AVAILABLE:
            self._initialize()
    
    def _initialize(self):
        """Initialize OpenRouter client"""
        try:
            # OpenRouter uses OpenAI-compatible API
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key,
            )
            self.logger.info(f"Initialized OpenRouter with model: {self.model_name}")
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenRouter: {e}")
            self.client = None
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Generate using OpenRouter (MiMo or other models)"""
        if not self.client:
            raise RuntimeError("OpenRouter client not initialized. Set OPENROUTER_API_KEY environment variable.")
        
        try:
            # Build messages array
            messages = []
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Generate using OpenRouter
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"OpenRouter generation failed: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if OpenRouter is available"""
        return OPENAI_AVAILABLE and self.api_key is not None and self.client is not None
    
    def get_model_info(self) -> dict:
        """Get model information"""
        # Determine model display info
        model_display = self.model_name
        cost_info = 'FREE (OpenRouter)'
        
        if 'free' in self.model_name.lower():
            cost_info = 'FREE (OpenRouter)'
        else:
            cost_info = 'Varies by model (check openrouter.ai/pricing)'
        
        return {
            'name': 'OpenRouter',
            'model': model_display,
            'provider': 'OpenRouter / Nvidia',
            'cost': cost_info,
            'available': self.is_available(),
            'strengths': 'Reasoning, coding, free access'
        }

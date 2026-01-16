"""
Google Gemini Model (FREE TIER)
15 requests/min, 1M tokens/day
"""

import os
from typing import Optional
from .base_model import BaseAIModel

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class GeminiModel(BaseAIModel):
    """Google Gemini 1.5 Flash - Free Tier"""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.api_key = os.getenv('GEMINI_API_KEY', self.config.get('api_key'))
        # Use gemini-2.0-flash-exp - experimental flash model (free tier)
        self.model_name = self.config.get('model', 'gemini-2.0-flash-exp')
        self.model = None
        
        if self.api_key and GEMINI_AVAILABLE:
            self._initialize()
    
    def _initialize(self):
        """Initialize Gemini model"""
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            self.logger.info(f"Initialized Gemini model: {self.model_name}")
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini: {e}")
            self.model = None
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Generate using Gemini"""
        if not self.model:
            raise RuntimeError("Gemini model not initialized. Set GEMINI_API_KEY environment variable.")
        
        try:
            # Combine system and user prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"<system>\n{system_prompt}\n</system>\n\n<user>\n{prompt}\n</user>"
            
            # Configure generation
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            
            # Generate
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            return response.text
            
        except Exception as e:
            self.logger.error(f"Gemini generation failed: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if Gemini is available"""
        return GEMINI_AVAILABLE and self.api_key is not None and self.model is not None
    
    def get_model_info(self) -> dict:
        """Get model information"""
        return {
            'name': 'Google Gemini',
            'model': self.model_name,
            'provider': 'Google',
            'cost': 'FREE (15 req/min, 1M tokens/day)',
            'available': self.is_available(),
            'strengths': 'Fast, high quality, large context window'
        }

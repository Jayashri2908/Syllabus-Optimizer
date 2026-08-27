"""
Google Gemini Model (FREE TIER)
15 requests/min, 1M tokens/day
Uses the google-genai SDK (replaces deprecated google-generativeai)
"""

import os
from typing import Optional
from .base_model import BaseAIModel

try:
    from google import genai
    from google.genai import types as genai_types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class GeminiModel(BaseAIModel):
    """Google Gemini 2.0 Flash - Free Tier"""

    def __init__(self, config: dict = None):
        super().__init__(config)
        self.api_key = os.getenv('GEMINI_API_KEY', self.config.get('api_key'))
        # Use gemini-2.0-flash - stable flash model (free tier)
        self.model_name = self.config.get('model', 'gemini-2.0-flash')
        self.client = None

        if self.api_key and GEMINI_AVAILABLE:
            self._initialize()

    def _initialize(self):
        """Initialize Gemini client"""
        try:
            self.client = genai.Client(api_key=self.api_key)
            self.logger.info(f"Initialized Gemini client for model: {self.model_name}")
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini: {e}")
            self.client = None

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Generate using Gemini"""
        if not self.client:
            raise RuntimeError("Gemini client not initialized. Set GEMINI_API_KEY environment variable.")

        try:
            # Build contents
            contents = prompt

            # Build config
            config = genai_types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            if system_prompt:
                config.system_instruction = system_prompt

            # Generate
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config,
            )

            return response.text

        except Exception as e:
            self.logger.error(f"Gemini generation failed: {e}")
            raise

    def is_available(self) -> bool:
        """Check if Gemini is available"""
        return GEMINI_AVAILABLE and self.api_key is not None and self.client is not None

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

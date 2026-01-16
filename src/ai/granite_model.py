"""
IBM Granite Model (FREE TIER)
Wrapper for existing Granite client
"""

from typing import Optional
from .base_model import BaseAIModel
from ..ibm.granite_client import GraniteClient


class GraniteModel(BaseAIModel):
    """IBM Granite - Free Tier"""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        try:
            self.client = GraniteClient()
            self.logger.info("Initialized IBM Granite model")
        except Exception as e:
            self.logger.warning(f"Granite initialization failed: {e}")
            self.client = None
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Generate using Granite"""
        if not self.client:
            raise RuntimeError("Granite not initialized. Check IBM credentials.")
        
        return self.client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    def is_available(self) -> bool:
        """Check if Granite is available"""
        return self.client is not None
    
    def get_model_info(self) -> dict:
        """Get model information"""
        return {
            'name': 'IBM Granite',
            'model': getattr(self.client.config, 'model', 'granite-3-8b-instruct') if self.client else 'unknown',
            'provider': 'IBM watsonx.ai',
            'cost': 'FREE (with limits)',
            'available': self.is_available(),
            'strengths': 'Education-focused, good for structured content'
        }

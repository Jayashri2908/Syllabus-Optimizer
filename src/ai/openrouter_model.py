"""
OpenRouter Model - Access MiMo and 300+ AI Models
Unified API for multiple providers (Xiaomi MiMo, OpenAI, Anthropic, etc.)
"""

import os
import time
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
        self.model_name = self.config.get('model', 'nvidia/nemotron-3.5-lightning:free')
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
        max_tokens: int = 1000,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        repetition_penalty: Optional[float] = None
    ) -> str:
        """Generate using OpenRouter (MiMo or other models)"""
        self.logger.info(f"OpenRouter: Generating with model '{self.model_name}'")
        
        if not self.client:
            raise RuntimeError("OpenRouter client not initialized. Set OPENROUTER_API_KEY environment variable.")
        
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
        
        # Prepare parameters
        api_params = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        # Add optional parameters if provided
        if top_p is not None: api_params["top_p"] = top_p
        if frequency_penalty is not None: api_params["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None: api_params["presence_penalty"] = presence_penalty
        
        # OpenRouter specific/extra parameters can be passed in 'extra_body'
        extra_body = {}
        if top_k is not None: extra_body["top_k"] = top_k
        if repetition_penalty is not None: extra_body["repetition_penalty"] = repetition_penalty
        
        if extra_body:
            api_params["extra_body"] = extra_body

        # Retry with exponential backoff
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Generate using OpenRouter
                response = self.client.chat.completions.create(**api_params)
                
                # Validate response structure
                if response is None:
                    raise RuntimeError("OpenRouter returned None response - API may be unavailable")
                
                if not hasattr(response, 'choices') or response.choices is None:
                    # Log the full response for debugging
                    self.logger.error(f"OpenRouter response has no choices: {response}")
                    raise RuntimeError("OpenRouter returned invalid response (no choices)")
                
                if len(response.choices) == 0:
                    raise RuntimeError("OpenRouter returned empty choices array")
                
                choice = response.choices[0]
                if not hasattr(choice, 'message') or choice.message is None:
                    raise RuntimeError("OpenRouter choice has no message")
                
                content = choice.message.content
                if content is None:
                    # Some models return None content with a finish_reason
                    finish_reason = getattr(choice, 'finish_reason', 'unknown')
                    self.logger.warning(f"OpenRouter returned None content, finish_reason: {finish_reason}")
                    raise RuntimeError(f"OpenRouter returned empty content (finish_reason: {finish_reason})")
                
                return content
                
            except Exception as e:
                last_error = e
                wait_time = (2 ** attempt) * 1  # 1s, 2s, 4s
                self.logger.warning(f"OpenRouter attempt {attempt + 1}/{max_retries} failed: {e}. Retrying in {wait_time}s...")
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
        
        self.logger.error(f"OpenRouter generation failed after {max_retries} attempts: {last_error}")
        raise RuntimeError(f"OpenRouter failed after {max_retries} retries: {last_error}")
    
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

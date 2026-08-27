"""
AI Model Manager for SCDO
OpenRouter (primary) + Gemini (fallback)
With structured JSON output support for staggered LLM chaining
"""

import logging
import json
import re
from typing import Optional, List, Dict, Any, Type
from pydantic import BaseModel as PydanticBaseModel, ValidationError
from .base_model import BaseAIModel
from .gemini_model import GeminiModel
from .openrouter_model import OpenRouterModel


class ModelManager:
    """Manages OpenRouter and Gemini models with automatic fallback"""
    
    # Priority: OpenRouter first, Gemini fallback
    TASK_MODEL_PRIORITY = {
        'generation': ['openrouter', 'gemini'],
        'analysis': ['openrouter', 'gemini'],
        'optimization': ['openrouter', 'gemini'],
        'validation': ['openrouter', 'gemini'],
    }
    
    def __init__(self, config: Dict = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        self.models = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize OpenRouter (primary) and Gemini (fallback) models"""
        
        # Try OpenRouter first (FREE - recommended)
        try:
            openrouter_config = self.config.get('openrouter', {})
            openrouter = OpenRouterModel(openrouter_config)
            
            if openrouter.is_available():
                self.models['openrouter'] = openrouter
                info = openrouter.get_model_info()
                self.logger.info(f"OPENROUTER available: {info.get('model', 'unknown')}")
            else:
                self.logger.debug("OPENROUTER not available (API key not set)")
        except Exception as e:
            self.logger.debug(f"Could not initialize OpenRouter: {e}")
        
        # Try Gemini as fallback
        try:
            gemini_config = self.config.get('gemini', {})
            gemini = GeminiModel(gemini_config)
            
            if gemini.is_available():
                self.models['gemini'] = gemini
                info = gemini.get_model_info()
                self.logger.info(f"GEMINI available: {info.get('model', 'unknown')}")
            else:
                self.logger.debug("GEMINI not available (API key not set)")
        except Exception as e:
            self.logger.debug(f"Could not initialize Gemini: {e}")
        
        # Warn if no models available
        if not self.models:
            self.logger.error("No AI models available!")
            self.logger.error("Set one of these environment variables:")
            self.logger.error("  OPENROUTER_API_KEY (recommended, free): https://openrouter.ai")
            self.logger.error("  GEMINI_API_KEY (free): https://makersuite.google.com/app/apikey")
    
    def get_model(self, task_type: str = 'generation', preferred_model: Optional[str] = None) -> BaseAIModel:
        """
        Get best available model for task
        
        Args:
            task_type: Type of task
            preferred_model: Optional preferred model name
            
        Returns:
            Best available model
        """
        
        # If specific model requested and available, use it
        if preferred_model and preferred_model in self.models:
            return self.models[preferred_model]
        
        # Get priority list for this task (OpenRouter first, Gemini fallback)
        priority = self.TASK_MODEL_PRIORITY.get(task_type, ['openrouter', 'gemini'])
        
        # Return first available model in priority order
        for model_name in priority:
            if model_name in self.models:
                self.logger.debug(f"Using {model_name} for {task_type}")
                return self.models[model_name]
        
        raise RuntimeError(
            "No AI models available! Set one of these API keys:\n"
            "  - OPENROUTER_API_KEY (recommended, free): https://openrouter.ai\n"
            "  - GEMINI_API_KEY (free): https://makersuite.google.com/app/apikey"
        )
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        task_type: str = 'generation',
        temperature: float = 0.7,
        max_tokens: int = 1000,
        preferred_model: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate text using best available model
        
        Args:
            prompt: User prompt
            system_prompt: System instruction
            task_type: Type of task
            temperature: Generation temperature
            max_tokens: Max tokens
            preferred_model: Optional specific model to use
            
        Returns:
            Generated text
        """
        model = self.get_model(task_type, preferred_model)
        
        return model.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    
    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[Type[PydanticBaseModel]] = None,
        task_type: str = 'generation',
        temperature: float = 0.2,
        max_tokens: int = 1000,
        preferred_model: Optional[str] = None,
        max_retries: int = 2,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate with guaranteed JSON output and optional Pydantic validation.
        
        Args:
            prompt: User prompt (should request JSON output)
            system_prompt: System instruction
            schema: Optional Pydantic model for validation
            task_type: Type of task for model selection
            temperature: Generation temperature (lower = more consistent)
            max_tokens: Max tokens
            preferred_model: Optional specific model to use
            max_retries: Number of retries on parse/validation failure
            
        Returns:
            Parsed and validated JSON as dict
            
        Raises:
            ValueError: If JSON cannot be parsed after retries
            ValidationError: If schema validation fails after retries
        """
        model = self.get_model(task_type, preferred_model)
        
        # Enhance prompt with JSON instructions
        json_prompt = f"""{prompt}

CRITICAL: Respond ONLY with valid JSON. 
- No markdown code blocks (no ```)
- No explanatory text before or after
- Just the JSON object itself"""
        
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                # Generate response
                response = model.generate(
                    prompt=json_prompt,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
                
                # Extract JSON from response
                json_data = self._extract_json(response)
                
                # Validate against schema if provided
                if schema is not None:
                    validated = schema.model_validate(json_data)
                    return validated.model_dump()
                
                return json_data
                
            except (json.JSONDecodeError, ValidationError) as e:
                last_error = e
                self.logger.warning(
                    f"JSON parse/validation failed (attempt {attempt + 1}/{max_retries + 1}): {e}"
                )
                
                # On retry, add more explicit JSON instruction
                if attempt < max_retries:
                    json_prompt = f"""{prompt}

IMPORTANT: Your previous response was not valid JSON. 
Please respond with ONLY a valid JSON object.
- Start with {{ and end with }}
- No markdown, no code blocks, no explanations
- Just pure JSON"""
                    temperature = max(0.1, temperature - 0.1)  # Lower temperature for retry
        
        # All retries failed
        raise ValueError(f"Failed to generate valid JSON after {max_retries + 1} attempts: {last_error}")
    
    def _extract_json(self, response: str) -> Dict[str, Any]:
        """
        Extract JSON from LLM response, handling common formatting issues.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Parsed JSON as dict
            
        Raises:
            json.JSONDecodeError: If no valid JSON found
        """
        if not response:
            raise json.JSONDecodeError("Empty response", "", 0)
        
        text = response.strip()
        
        # Try direct parse first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Remove markdown code blocks
        # Pattern: ```json ... ``` or ``` ... ```
        code_block_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
        matches = re.findall(code_block_pattern, text)
        if matches:
            for match in matches:
                try:
                    return json.loads(match.strip())
                except json.JSONDecodeError:
                    continue
        
        # Try to find JSON object in text
        # Look for { ... } pattern
        brace_pattern = r'\{[\s\S]*\}'
        matches = re.findall(brace_pattern, text)
        if matches:
            # Try longest match first (most complete JSON)
            for match in sorted(matches, key=len, reverse=True):
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
        
        # Try to find JSON array
        bracket_pattern = r'\[[\s\S]*\]'
        matches = re.findall(bracket_pattern, text)
        if matches:
            for match in sorted(matches, key=len, reverse=True):
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
        
        # Final attempt: clean common issues
        cleaned = text
        # Remove leading/trailing non-JSON text
        cleaned = re.sub(r'^[^{\[]*', '', cleaned)
        cleaned = re.sub(r'[^}\]]*$', '', cleaned)
        
        return json.loads(cleaned)
    
    def get_available_models(self) -> List[Dict]:
        """Get list of available models"""
        return [model.get_model_info() for model in self.models.values()]
    
    def print_status(self):
        """Print status of models"""
        print("\n" + "="*60)
        print("AI MODEL STATUS")
        print("="*60)
        
        if not self.models:
            print("\nNo models available!")
            print("\nQuick Setup (Choose one):")
            print("\nOption 1: OpenRouter (RECOMMENDED - FREE)")
            print("   Visit: https://openrouter.ai")
            print("   Get your key in 2 minutes (no credit card)")
            print("   PowerShell: $env:OPENROUTER_API_KEY='your_key'")
            print("   CMD:        set OPENROUTER_API_KEY=your_key")
            print("\nOption 2: Google Gemini (FREE)")
            print("   Visit: https://makersuite.google.com/app/apikey")
            print("   PowerShell: $env:GEMINI_API_KEY='your_key'")
            print("   CMD:        set GEMINI_API_KEY=your_key")
            print("\nBoth are FREE with generous limits!")
        else:
            for name, model in self.models.items():
                info = model.get_model_info()
                print(f"\n  {info['name']} ({info['provider']})")
                print(f"  Model: {info.get('model', 'N/A')}")
                print(f"  Cost: {info['cost']}")
                if 'strengths' in info:
                    print(f"  Best for: {info['strengths']}")
        
        print("\n" + "="*60 + "\n")

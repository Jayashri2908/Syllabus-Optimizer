"""
IBM Granite Client Wrapper for SCDO
Handles authentication, rate limiting, and API calls to IBM Granite model
"""

import os
import time
import yaml
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import logging
from functools import wraps
from dotenv import load_dotenv

try:
    from ibm_watsonx_ai import APIClient
    from ibm_watsonx_ai import Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference
    from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
except ImportError:
    logging.warning("IBM Watson libraries not installed. Install with: pip install ibm-watsonx-ai")


@dataclass
class GraniteConfig:
    """Configuration for IBM Granite model"""
    model: str
    max_tokens: int
    temperature: float
    top_p: float
    top_k: int
    repetition_penalty: float
    api_key: str
    project_id: Optional[str]
    instance_crn: Optional[str]
    url: str
    max_retries: int = 3
    retry_delay: int = 2
    timeout: int = 60


class RateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = []
        
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        now = time.time()
        # Remove requests older than 1 minute
        self.requests = [req_time for req_time in self.requests if now - req_time < 60]
        
        if len(self.requests) >= self.requests_per_minute:
            # Wait until oldest request is more than 1 minute old
            sleep_time = 60 - (now - self.requests[0]) + 0.1
            if sleep_time > 0:
                logging.info(f"Rate limit reached. Waiting {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
                
        self.requests.append(time.time())


class GraniteClient:
    """Client for IBM Granite model API"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Granite client
        
        Args:
            config_path: Path to IBM config YAML file
        """
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_path)
        self.rate_limiter = RateLimiter(requests_per_minute=60)
        self.client = None
        self.model = None
        self._initialize_client()
        
    def _load_config(self, config_path: Optional[str] = None) -> GraniteConfig:
        """Load configuration from YAML file"""
        # Load .env.ibm if it exists
        env_path = Path(__file__).parent.parent.parent / ".env.ibm"
        if env_path.exists():
            load_dotenv(env_path)
            self.logger.info(f"Loaded credentials from {env_path}")
        
        if config_path is None:
            # Default to configs/ibm_config.yaml
            config_path = Path(__file__).parent.parent.parent / "configs" / "ibm_config.yaml"
        
        # Try to load YAML config if it exists
        granite_config = {}
        if Path(config_path).exists():
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
                granite_config = config_data.get('ibm_granite', {})
        
        # Check for environment variables (override YAML)
        api_key = os.getenv('IBM_CLOUD_API_KEY', granite_config.get('api_key'))
        project_id = os.getenv('IBM_PROJECT_ID', granite_config.get('project_id'))
        instance_crn = os.getenv('IBM_WML_CRN', granite_config.get('instance_crn'))
        
        # Validate required credentials - only API key is required now
        if not api_key:
            raise ValueError("IBM Cloud API key is required (set IBM_CLOUD_API_KEY environment variable)")
        
        # Warn if neither project ID nor instance CRN is available
        if not project_id and not instance_crn:
            self.logger.warning("Neither IBM_PROJECT_ID nor IBM_WML_CRN is set. API calls may fail.")
        elif not project_id:
            self.logger.info("Using WML instance CRN instead of project ID")
        
        return GraniteConfig(
            model=granite_config.get('model', 'ibm/granite-4-h-small'),
            max_tokens=granite_config.get('max_tokens', 4096),
            temperature=granite_config.get('temperature', 0.7),
            top_p=granite_config.get('top_p', 1.0),
            top_k=granite_config.get('top_k', 50),
            repetition_penalty=granite_config.get('repetition_penalty', 1.0),
            api_key=api_key,
            project_id=project_id,
            instance_crn=instance_crn,
            url=granite_config.get('url', 'https://us-south.ml.cloud.ibm.com'),
            max_retries=granite_config.get('max_retries', 3),
            retry_delay=granite_config.get('retry_delay', 2),
            timeout=granite_config.get('timeout', 60)
        )
        
    def _initialize_client(self):
        """Initialize IBM Watson AI client"""
        try:
            credentials = Credentials(
                url=self.config.url,
                api_key=self.config.api_key
            )
            
            self.client = APIClient(credentials)
            
            # Set project or use instance CRN
            if self.config.project_id:
                self.client.set.default_project(self.config.project_id)
                self.logger.info(f"Using project ID: {self.config.project_id}")
            elif self.config.instance_crn:
                # Instance CRN will be used in generate() calls
                self.logger.info(f"Using WML instance CRN for requests")
            else:
                self.logger.warning("No project ID or instance CRN set. API calls may fail.")
            
            # Initialize model inference
            self.model = ModelInference(
                model_id=self.config.model,
                api_client=self.client,
                params={
                    GenParams.MAX_NEW_TOKENS: self.config.max_tokens,
                    GenParams.TEMPERATURE: self.config.temperature,
                    GenParams.TOP_P: self.config.top_p,
                    GenParams.TOP_K: self.config.top_k,
                    GenParams.REPETITION_PENALTY: self.config.repetition_penalty
                }
            )
            
            self.logger.info("IBM Granite client initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize IBM Granite client: {e}")
            raise
            
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Generate text using IBM Granite model
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt for context
            max_tokens: Override default max tokens
            temperature: Override default temperature
            
        Returns:
            Generated text
        """
        self.rate_limiter.wait_if_needed()
        
        # Construct full prompt
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
            
        # Override parameters if provided
        params = {}
        if max_tokens:
            params[GenParams.MAX_NEW_TOKENS] = max_tokens
        if temperature:
            params[GenParams.TEMPERATURE] = temperature
            
        # Retry logic
        for attempt in range(self.config.max_retries):
            try:
                # Prepare generate call parameters
                generate_kwargs = {
                    'prompt': full_prompt,
                }
                
                # Add custom params if provided
                if params:
                    generate_kwargs['params'] = params
                
                response = self.model.generate(**generate_kwargs)
                
                # Extract generated text
                if isinstance(response, dict):
                    return response.get('results', [{}])[0].get('generated_text', '')
                return str(response)
                
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay * (attempt + 1))
                else:
                    self.logger.error(f"All retry attempts failed for prompt")
                    raise
                    
        return ""
        
    def analyze_syllabus(self, syllabus_content: str) -> Dict[str, Any]:
        """
        Analyze syllabus content using Granite
        
        Args:
            syllabus_content: Parsed syllabus text
            
        Returns:
            Analysis results
        """
        system_prompt = """You are an academic curriculum expert. Analyze the syllabus and provide:
1. Learning outcomes quality assessment
2. Bloom's taxonomy coverage
3. Assessment strategy effectiveness
4. Content gaps or redundancies
5. Alignment with modern pedagogical practices

Provide structured analysis in JSON format."""

        prompt = f"Analyze this syllabus:\n\n{syllabus_content}"
        
        response = self.generate(prompt, system_prompt=system_prompt)
        
        # Parse response (implement JSON extraction)
        return {"analysis": response}
        
    def generate_syllabus(
        self,
        course_title: str,
        program_outcomes: List[str],
        keywords: List[str],
        credit_hours: str
    ) -> str:
        """
        Generate syllabus using Granite
        
        Args:
            course_title: Course title
            program_outcomes: List of relevant POs
            keywords: Key topics/skills
            credit_hours: L-T-P format
            
        Returns:
            Generated syllabus
        """
        system_prompt = """You are an expert curriculum designer. Generate a comprehensive syllabus 
following outcome-based education principles and accreditation standards."""

        prompt = f"""Generate a complete syllabus for:
Course: {course_title}
Credits: {credit_hours}
Program Outcomes: {', '.join(program_outcomes)}
Key Topics: {', '.join(keywords)}

Include:
1. Course objectives
2. Course outcomes (4-6 COs)
3. Unit-wise syllabus with hours
4. Teaching methodology
5. Assessment pattern
6. References"""

        return self.generate(prompt, system_prompt=system_prompt)
        
    def optimize_content(self, content: str, optimization_goal: str) -> str:
        """
        Optimize syllabus content
        
        Args:
            content: Content to optimize
            optimization_goal: Specific optimization objective
            
        Returns:
            Optimized content
        """
        system_prompt = f"""You are a curriculum optimization expert. 
Improve the following content with focus on: {optimization_goal}"""

        prompt = f"Content to optimize:\n\n{content}"
        
        return self.generate(prompt, system_prompt=system_prompt)

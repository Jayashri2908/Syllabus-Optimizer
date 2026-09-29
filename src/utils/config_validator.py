"""Configuration validation for SCDO"""
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import yaml


class ConfigValidationError(Exception):
    pass


def validate_config() -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []

    env = os.getenv("ENV", "development").lower()
    if env not in ("development", "staging", "production"):
        errors.append(f"Invalid ENV value: {env}. Must be development, staging, or production")

    if env == "production":
        api_key = os.getenv("API_KEY", "")
        if not api_key or len(api_key) < 16:
            errors.append("API_KEY must be set and at least 16 characters in production")

    openrouter_key = os.getenv("OPENROUTER_API_KEY", "")
    gemini_key = os.getenv("GEMINI_API_KEY", "")

    if not openrouter_key and not gemini_key:
        warnings.append("No AI API keys set. AI features will be unavailable.")

    if openrouter_key and not openrouter_key.startswith("sk-"):
        warnings.append("OPENROUTER_API_KEY does not start with 'sk-'. Verify the key is correct.")

    max_upload = int(os.getenv("MAX_UPLOAD_SIZE", "52428800"))
    if max_upload > 100 * 1024 * 1024:
        warnings.append("MAX_UPLOAD_SIZE exceeds 100MB. This may cause memory issues.")

    config_path = Path(__file__).resolve().parents[2] / "configs" / "ai_models.yaml"
    if config_path.exists():
        with open(config_path) as f:
            ai_config = yaml.safe_load(f)
        if not ai_config.get("openrouter", {}).get("model"):
            warnings.append("OpenRouter model not configured in ai_models.yaml")
    else:
        warnings.append("ai_models.yaml not found")

    if errors:
        raise ConfigValidationError("\n".join(errors))

    return {
        "env": env,
        "is_production": env == "production",
        "has_openrouter": bool(openrouter_key),
        "has_gemini": bool(gemini_key),
        "warnings": warnings,
    }


def log_config_status(config: Dict[str, Any]):
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Environment: {config['env']}")
    logger.info(f"OpenRouter available: {config['has_openrouter']}")
    logger.info(f"Gemini available: {config['has_gemini']}")
    for warning in config["warnings"]:
        logger.warning(f"Config warning: {warning}")

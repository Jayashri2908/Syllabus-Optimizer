import os
import sys
import yaml
import time
import logging
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Setup path to include src
sys.path.append(os.getcwd())

from src.ai.model_manager import ModelManager

# Configure logging to be less verbose for the script
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def ping_models():
    # Load config
    config_path = os.path.join("configs", "ai_models.yaml")
    if not os.path.exists(config_path):
        print(f"Error: {config_path} not found.")
        return

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    print("\n" + "="*60)
    print("AI MODEL PING TEST")
    print("="*60)

    # Initialize ModelManager
    manager = ModelManager(config)
    
    # We want to test each model explicitly, not just through the manager's fallback
    # The manager initializes models it can. Let's see what's available.
    available_models = manager.models
    
    models_to_test = ['openrouter', 'gemini']
    
    results = []

    for model_key in models_to_test:
        enabled = config.get(model_key, {}).get('enabled', True)
        print(f"\nModel: {model_key.upper()}")
        print(f"Status: {'ENABLED' if enabled else 'DISABLED'}")
        
        if not enabled:
            results.append({"model": model_key, "status": "SKIPPED", "reason": "Disabled in config"})
            continue

        if model_key not in available_models:
            print(f"Result: FAILED (Not initialized - check API keys or dependencies)")
            results.append({"model": model_key, "status": "FAILED", "reason": "Initialization failed"})
            continue

        model = available_models[model_key]
        model_info = model.get_model_info()
        print(f"Model Name: {model_info.get('model', 'N/A')}")
        print(f"Pinging...", end=" ", flush=True)

        start_time = time.time()
        try:
            # Simple ping prompt
            response = model.generate(prompt="Say 'pong' and nothing else.", max_tokens=10)
            duration = time.time() - start_time
            print(f"SUCCESS ({duration:.2f}s)")
            print(f"Response: {response.strip()}")
            results.append({"model": model_key, "status": "SUCCESS", "duration": duration, "response": response.strip()})
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            print(f"FAILED ({duration:.2f}s)")
            print(f"Error: {error_msg}")
            results.append({"model": model_key, "status": "FAILED", "duration": duration, "reason": error_msg})

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for res in results:
        status_icon = "[OK]" if res['status'] == 'SUCCESS' else "[FAIL]" if res['status'] == 'FAILED' else "[-]"
        duration_str = f"({res['duration']:.2f}s)" if 'duration' in res else ""
        print(f"{status_icon} {res['model'].upper()}: {res['status']} {duration_str}")
        if res['status'] == 'FAILED':
            print(f"   Reason: {res['reason'][:100]}...")
    print("="*60 + "\n")

if __name__ == "__main__":
    ping_models()

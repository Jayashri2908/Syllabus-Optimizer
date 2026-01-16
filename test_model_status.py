import sys
sys.path.insert(0, 'd:/Syllabus Optimizer')

from dotenv import load_dotenv
from pathlib import Path

# Load .env file
env_path = Path('d:/Syllabus Optimizer/.env')
load_dotenv(env_path)

import os
print("="*60)
print("ENVIRONMENT VARIABLES CHECK")
print("="*60)
print(f"OPENROUTER_API_KEY: {'SET ✅' if os.getenv('OPENROUTER_API_KEY') else 'NOT SET ❌'}")
print(f"GEMINI_API_KEY: {'SET ✅' if os.getenv('GEMINI_API_KEY') else 'NOT SET ❌'}")
print()

print("="*60)
print("MODEL MANAGER STATUS")
print("="*60)

try:
    from src.ai.model_manager import ModelManager
    m = ModelManager()
    
    print(f"\nTask Priority: {m.TASK_MODEL_PRIORITY['generation']}")
    print(f"\nAvailable Models:")
    for name, model in m.models.items():
        info = model.get_model_info()
        print(f"  ✓ {name}: {info['model']}")
    
    print(f"\n{'='*60}")
    print("ACTIVE MODEL FOR GENERATION")
    print("="*60)
    active_model = m.get_model('generation')
    info = active_model.get_model_info()
    print(f"\n🎯 Using: {info['name']}")
    print(f"   Model: {info['model']}")
    print(f"   Cost: {info['cost']}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

"""
Setup and Test Script for Gemini + Granite
Simplified to only check Gemini and Granite models
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ai.model_manager import ModelManager


def print_separator(char="="):
    print("\n" + char * 70 + "\n")


def check_environment_variables():
    """Check which API keys are configured"""
    print_separator()
    print("ENVIRONMENT VARIABLES CHECK")
    print_separator()
    
    api_keys = {
        'GEMINI_API_KEY': 'Google Gemini',
        'IBM_CLOUD_API_KEY': 'IBM Granite',
        'IBM_PROJECT_ID': 'IBM Project ID',
    }
    
    configured = []
    missing = []
    
    for key, name in api_keys.items():
        value = os.getenv(key)
        if value:
            # Show only first/last few characters for security
            masked = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
            print(f"✓ {name:20} : {masked}")
            configured.append(name)
        else:
            print(f"✗ {name:20} : Not set")
            missing.append((name, key))
    
    return configured, missing


def test_model_initialization():
    """Test initializing ModelManager"""
    print_separator()
    print("INITIALIZING AI MODELS")
    print_separator()
    
    try:
        manager = ModelManager()
        return manager
    except Exception as e:
        print(f"❌ Model initialization failed: {e}")
        return None


def test_generation(manager: ModelManager):
    """Test generation with available models"""
    print_separator()
    print("TESTING GENERATION")
    print_separator()
    
    test_prompt = "Write a one-sentence learning outcome for a Machine Learning course at the 'Apply' Bloom's level."
    
    print(f"Test Prompt: {test_prompt}\n")
    
    try:
        result = manager.generate(
            prompt=test_prompt,
            task_type='generation',
            temperature=0.5,
            max_tokens=100
        )
        
        print("✓ Generation successful!")
        print(f"\nResult:\n{result}\n")
        return True
        
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        return False


def print_setup_instructions(missing):
    """Print setup instructions for missing models"""
    if not missing:
        return
    
    print_separator()
    print("SETUP INSTRUCTIONS")
    print_separator()
    
    for name, key in missing:
        if 'Gemini' in name:
            print(f"\n📱 {name} (RECOMMENDED)")
            print("   1. Visit: https://makersuite.google.com/app/apikey")
            print("   2. Click 'Create API Key' (no credit card needed)")
            print(f"   3. Set environment variable:")
            print(f"      PowerShell: $env:{key}='your_api_key'")
            print(f"      CMD:        set {key}=your_api_key")
            print(f"   4. Or add to .env.ibm file: {key}=your_api_key")
            print("\n   Free Tier: 15 requests/min, 1M tokens/day")
            
        elif 'IBM' in name:
            print(f"\n🔷 {name} (Fallback)")
            print("   Already configured in configs/ibm_config.yaml")
            print("   Set IBM_CLOUD_API_KEY and IBM_PROJECT_ID if needed")


def main():
    """Main setup and test function"""
    print("\n" + "="*70)
    print(" " * 15 + "SYLLABUS OPTIMIZER - AI SETUP")
    print("="*70)
    
    # Check environment
    configured, missing = check_environment_variables()
    
    # Initialize models
    manager = test_model_initialization()
    
    if manager:
        # Show available models
        manager.print_status()
        
        # Test generation if models available
        if manager.models:
            test_generation(manager)
        else:
            print("\n⚠️  No models available for testing")
    
    # Show setup instructions
    if missing:
        print_setup_instructions(missing)
    else:
        print_separator()
        print("✅ ALL API KEYS CONFIGURED!")
        print_separator()
    
    # Final recommendations
    print_separator()
    print("RECOMMENDATIONS")
    print_separator()
    
    if not configured:
        print("\n⚠️  No AI models configured yet!")
        print("\n🎯 Quick Start:")
        print("\n1. Get FREE Google Gemini API Key (RECOMMENDED)")
        print("   - Visit: https://makersuite.google.com/app/apikey")
        print("   - Free tier: 15 requests/min, 1M tokens/day")
        print("   - Best quality for free")
        print("   - Setup time: 2 minutes")
        print("\n2. Granite is already configured as fallback")
        
    elif len(configured) == 1:
        print(f"\n✓ You have {configured[0]} configured")
        if 'Gemini' in configured[0]:
            print("\n🎉 Perfect! Gemini is the recommended model.")
            print("   Granite will be used as automatic fallback.")
        else:
            print("\n💡 Recommendation: Add Gemini for best quality")
            print("   - Get free key: https://makersuite.google.com/app/apikey")
    else:
        print(f"\n🎉 Great! You have {len(configured)} models configured:")
        for model in configured:
            print(f"   ✓ {model}")
        print("\n   System will automatically use best model for each task!")
    
    print("\n" + "="*70)
    print("\nNext Steps:")
    print("1. Set GEMINI_API_KEY environment variable (recommended)")
    print("2. Test: python setup_ai_models.py")
    print("3. Start generating: python -m webapp.backend.main")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()

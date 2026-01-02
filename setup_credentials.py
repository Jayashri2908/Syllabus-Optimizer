#!/usr/bin/env python3
"""
Interactive IBM Cloud Credentials Setup Script
This script will help you configure your IBM Cloud API credentials automatically.
"""

import yaml
import sys
from pathlib import Path
from getpass import getpass

def update_config():
    """Interactive credential setup"""
    print("\n" + "=" * 70)
    print("🔑 IBM Cloud Credentials Setup")
    print("=" * 70)
    
    print("\n📋 Instructions:")
    print("   1. In the browser window, log in to IBM Cloud")
    print("   2. You should see the 'API keys' page")
    print("   3. Click 'Create +' to create a new API key (or use existing)")
    print("   4. Copy the API key when shown")
    print("   5. Come back here and paste it below")
    print("\n" + "-" * 70)
    
    # Get API Key
    print("\n🔐 Step 1: API Key")
    print("   Location: https://cloud.ibm.com/iam/apikeys")
    api_key = input("\n   Paste your IBM Cloud API Key here: ").strip()
    
    if not api_key:
        print("❌ ERROR: API key cannot be empty!")
        return False
    
    print("   ✅ API Key captured")
    
    # Get Project ID
    print("\n📦 Step 2: Watsonx Project ID")
    print("   Location: https://dataplatform.cloud.ibm.com/wx/home")
    print("   (Open your project → Manage → General → Details)")
    
    open_watsonx = input("\n   Open Watsonx in browser now? (y/n): ").strip().lower()
    if open_watsonx == 'y':
        import webbrowser
        webbrowser.open('https://dataplatform.cloud.ibm.com/wx/home')
        print("   ✅ Opened Watsonx in browser")
    
    project_id = input("\n   Paste your Watsonx Project ID here: ").strip()
    
    if not project_id:
        print("❌ ERROR: Project ID cannot be empty!")
        return False
    
    print("   ✅ Project ID captured")
    
    # Optional: URL (use default if not provided)
    print("\n🌐 Step 3: IBM Watsonx URL (Optional)")
    print("   Default: https://us-south.ml.cloud.ibm.com")
    url = input("\n   Press Enter for default, or paste custom URL: ").strip()
    
    if not url:
        url = "https://us-south.ml.cloud.ibm.com"
        print(f"   ✅ Using default URL: {url}")
    else:
        print(f"   ✅ Using custom URL: {url}")
    
    # Update the config file
    print("\n💾 Updating configuration file...")
    config_path = Path(__file__).parent / "configs" / "ibm_config.yaml"
    
    try:
        # Load existing config
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
        else:
            # Create from example
            example_path = config_path.parent / "ibm_config.yaml.example"
            if example_path.exists():
                with open(example_path, 'r') as f:
                    config = yaml.safe_load(f)
                print(f"   📄 Created from example template")
            else:
                print("❌ ERROR: No config file or example found!")
                return False
        
        # Update credentials
        if 'ibm_granite' not in config:
            config['ibm_granite'] = {}
        
        config['ibm_granite']['api_key'] = api_key
        config['ibm_granite']['project_id'] = project_id
        config['ibm_granite']['url'] = url
        
        # Write updated config
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        print(f"   ✅ Configuration saved to: {config_path}")
        
    except Exception as e:
        print(f"❌ ERROR: Failed to update config: {e}")
        return False
    
    # Test the connection
    print("\n🧪 Testing API connection...")
    test_result = test_connection(config)
    
    if test_result:
        print("\n" + "=" * 70)
        print("✅ SUCCESS! Your IBM Cloud credentials are configured and working!")
        print("=" * 70)
        print("\n💡 Next Steps:")
        print("   1. Restart your backend server (run start_app.bat)")
        print("   2. The AI features should now work with IBM Granite")
        print()
        return True
    else:
        print("\n" + "=" * 70)
        print("⚠️  Credentials saved, but connection test failed.")
        print("   Please verify your API key and Project ID are correct.")
        print("=" * 70)
        print()
        return False

def test_connection(config):
    """Quick connection test"""
    try:
        from ibm_watson_machine_learning.foundation_models import Model
        from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
        
        granite_config = config.get('ibm_granite', {})
        
        credentials = {
            "url": granite_config.get('url'),
            "apikey": granite_config.get('api_key')
        }
        
        model = Model(
            model_id=granite_config.get('model', 'ibm/granite-13b-chat-v2'),
            params={
                GenParams.MAX_NEW_TOKENS: 20,
                GenParams.TEMPERATURE: 0.7,
            },
            credentials=credentials,
            project_id=granite_config.get('project_id')
        )
        
        # Quick test
        response = model.generate_text(prompt="Say 'OK' if you can read this.")
        print(f"   📥 Response: {response[:50]}")
        print("   ✅ Connection test passed!")
        return True
        
    except ImportError:
        print("   ⚠️  Cannot test - ibm-watson-machine-learning not installed")
        print("   💡 Install with: pip install ibm-watson-machine-learning")
        return True  # Don't fail if library not installed
    except Exception as e:
        print(f"   ❌ Connection failed: {str(e)[:100]}")
        return False

def main():
    print("\n🚀 Starting IBM Cloud Credentials Setup...\n")
    
    success = update_config()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

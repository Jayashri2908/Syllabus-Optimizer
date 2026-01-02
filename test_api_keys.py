#!/usr/bin/env python3
"""
Test script to verify IBM API keys and connectivity
"""
import yaml
import sys
from pathlib import Path

def load_config():
    """Load IBM configuration"""
    config_path = Path(__file__).parent / "configs" / "ibm_config.yaml"
    
    if not config_path.exists():
        print("❌ ERROR: ibm_config.yaml not found!")
        print(f"   Expected at: {config_path}")
        print("\n💡 TIP: Copy ibm_config.yaml.example to ibm_config.yaml and add your credentials")
        return None
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"❌ ERROR: Failed to load config: {e}")
        return None

def check_api_credentials(config):
    """Check if API credentials are configured"""
    if not config:
        return False
    
    print("\n🔍 Checking IBM Granite API Configuration...")
    print("=" * 60)
    
    granite_config = config.get('ibm_granite', {})
    
    # Check API key
    api_key = granite_config.get('api_key', '')
    if not api_key or api_key == 'YOUR_IBM_CLOUD_API_KEY_HERE':
        print("❌ API Key: Not configured (using placeholder)")
        return False
    else:
        # Mask the API key for security
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        print(f"✅ API Key: Configured ({masked_key})")
    
    # Check Project ID
    project_id = granite_config.get('project_id', '')
    if not project_id or project_id == 'YOUR_PROJECT_ID_HERE':
        print("❌ Project ID: Not configured (using placeholder)")
        return False
    else:
        masked_id = project_id[:8] + "..." + project_id[-4:] if len(project_id) > 12 else project_id
        print(f"✅ Project ID: Configured ({masked_id})")
    
    # Check URL
    url = granite_config.get('url', '')
    if url:
        print(f"✅ URL: {url}")
    else:
        print("⚠️  URL: Not configured (will use default)")
    
    # Check model
    model = granite_config.get('model', 'granite-13b-chat-v2')
    print(f"✅ Model: {model}")
    
    return True

def test_api_connection(config):
    """Test actual API connection"""
    print("\n🔌 Testing IBM Watsonx API Connection...")
    print("=" * 60)
    
    try:
        from ibm_watson_machine_learning.foundation_models import Model
        from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
        
        granite_config = config.get('ibm_granite', {})
        
        credentials = {
            "url": granite_config.get('url', 'https://us-south.ml.cloud.ibm.com'),
            "apikey": granite_config.get('api_key')
        }
        
        project_id = granite_config.get('project_id')
        model_id = granite_config.get('model', 'ibm/granite-13b-chat-v2')
        
        print(f"📡 Connecting to IBM Watsonx...")
        print(f"   Model: {model_id}")
        
        # Initialize model
        model = Model(
            model_id=model_id,
            params={
                GenParams.MAX_NEW_TOKENS: 50,
                GenParams.TEMPERATURE: 0.7,
            },
            credentials=credentials,
            project_id=project_id
        )
        
        # Test with a simple prompt
        print(f"📤 Sending test prompt...")
        test_prompt = "What is AI? Answer in one sentence."
        
        response = model.generate_text(prompt=test_prompt)
        
        print(f"✅ API Connection: SUCCESS!")
        print(f"\n📥 Test Response:")
        print(f"   {response[:100]}..." if len(response) > 100 else f"   {response}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("\n💡 Install with: pip install ibm-watson-machine-learning")
        return False
    except Exception as e:
        error_msg = str(e)
        print(f"❌ API Connection: FAILED")
        print(f"\n   Error: {error_msg}")
        
        # Provide helpful error messages
        if "BXNIM0415E" in error_msg or "API key could not be found" in error_msg:
            print("\n💡 SOLUTION:")
            print("   Your API key is invalid or not recognized by IBM Cloud.")
            print("   1. Go to https://cloud.ibm.com/iam/apikeys")
            print("   2. Create a new API key or verify your existing one")
            print("   3. Update configs/ibm_config.yaml with the correct API key")
        elif "project_id" in error_msg.lower():
            print("\n💡 SOLUTION:")
            print("   Your Project ID might be incorrect.")
            print("   1. Go to https://dataplatform.cloud.ibm.com/wx/home")
            print("   2. Open your project")
            print("   3. Go to Manage > General > Details")
            print("   4. Copy the Project ID and update configs/ibm_config.yaml")
        
        return False

def main():
    print("\n" + "=" * 60)
    print("🧪 IBM API Key & Connectivity Test")
    print("=" * 60)
    
    # Load configuration
    config = load_config()
    if not config:
        sys.exit(1)
    
    # Check credentials
    creds_ok = check_api_credentials(config)
    if not creds_ok:
        print("\n" + "=" * 60)
        print("❌ RESULT: API credentials not properly configured")
        print("=" * 60)
        print("\n💡 NEXT STEPS:")
        print("   1. Copy configs/ibm_config.yaml.example to configs/ibm_config.yaml")
        print("   2. Get your IBM Cloud API key from: https://cloud.ibm.com/iam/apikeys")
        print("   3. Get your Project ID from: https://dataplatform.cloud.ibm.com/wx/home")
        print("   4. Update the values in configs/ibm_config.yaml")
        sys.exit(1)
    
    # Test connection
    connection_ok = test_api_connection(config)
    
    print("\n" + "=" * 60)
    if connection_ok:
        print("✅ RESULT: All tests passed! API is working correctly.")
    else:
        print("❌ RESULT: API credentials configured but connection failed.")
        print("           Check the error messages above for solutions.")
    print("=" * 60)
    print()
    
    sys.exit(0 if connection_ok else 1)

if __name__ == "__main__":
    main()

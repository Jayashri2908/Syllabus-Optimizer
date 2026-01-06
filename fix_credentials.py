"""
Fix IBM credentials for Syllabus Optimizer
This script updates the .env.ibm file with the correct environment variable names
"""

import os
from pathlib import Path

# Path to .env.ibm file
env_file = Path(__file__).parent / '.env.ibm'

print("=" * 60)
print("IBM Credentials Fix Script")
print("=" * 60)

# Read current content
if env_file.exists():
    with open(env_file, 'r') as f:
        content = f.read()
    
    print("\n✓ Found .env.ibm file")
    
    # Replace IBM_API_KEY with IBM_CLOUD_API_KEY
    updated_content = content.replace(
        '# API Key for authentication\nIBM_API_KEY=',
        '# API Key for authentication (used by GraniteClient)\nIBM_CLOUD_API_KEY='
    )
    
    # Also keep IBM_API_KEY for compatibility with other parts
    if 'IBM_API_KEY=' in content and 'IBM_CLOUD_API_KEY=' not in updated_content:
        lines = updated_content.split('\n')
        new_lines = []
        for line in lines:
            new_lines.append(line)
            if line.startswith('IBM_API_KEY=') and not line.startswith('IBM_API_KEY=#'):
                # Extract the API key value
                api_key_value = line.split('=', 1)[1]
                # Add IBM_CLOUD_API_KEY right after
                new_lines.insert(len(new_lines)-1, f'IBM_CLOUD_API_KEY={api_key_value}')
        updated_content = '\n'.join(new_lines)
    
    # Add PROJECT_ID section if not exists
    if 'IBM_PROJECT_ID' not in updated_content:
        updated_content += '\n\n# ============================================================\n'
        updated_content += '# IBM watsonx.ai Project ID (Optional but recommended)\n'
        updated_content += '# ============================================================\n\n'
        updated_content += '# NOTE: Your application requires a project ID to work properly\n'
        updated_content += '# To create a project:\n'
        updated_content += '# 1. Go to https://dataplatform.cloud.ibm.com\n'
        updated_content += '# 2. Click "New project"\n'
        updated_content += '# 3. Create a project and copy the Project ID\n'
        updated_content += '# 4. Set it here:\n'
        updated_content += 'IBM_PROJECT_ID=\n'
    
    # Write updated content
    with open(env_file, 'w') as f:
        f.write(updated_content)
    
    print("✓ Updated environment variable names")
    print("\nChanges made:")
    print("  - Added IBM_CLOUD_API_KEY (required by GraniteClient)")
    print("  - Kept IBM_API_KEY for compatibility")
    print("  - Added IBM_PROJECT_ID placeholder")
    
    print("\n" + "=" * 60)
    print("⚠️  ACTION REQUIRED")
    print("=" * 60)
    print("\nYour application needs a watsonx.ai Project ID to work.")
    print("\nOptions:")
    print("\n1. CREATE A PROJECT (Recommended):")
    print("   - Visit: https://dataplatform.cloud.ibm.com")
    print("   - Click 'New project'")
    print("   - Copy the Project ID")
    print("   - Add to .env.ibm: IBM_PROJECT_ID=your-project-id")
    
    print("\n2. USE WITHOUT PROJECT (Limited functionality):")
    print("   - Modify src/ibm/granite_client.py to make project_id optional")
    print("   - This may limit some features")
    
    print("\n" + "=" * 60)
    
else:
    print("\n✗ ERROR: .env.ibm file not found!")
    print("Please make sure the file exists at:")
    print(f"  {env_file.absolute()}")

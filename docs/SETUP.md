# Setup Instructions for SCDO

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- IBM Cloud account with watsonx.ai access
- Git (optional, for version control)

## Step-by-Step Setup

### 1. Navigate to Project Directory

```bash
cd "d:\Syllabus Optimizer"
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
```

**Linux/Mac:**
```bash
python3 -m venv venv
```

### 3. Activate Virtual Environment

**Windows (PowerShell):**
```bash
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```bash
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

You should see `(venv)` prefix in your terminal prompt.

### 4. Upgrade pip

```bash
python -m pip install --upgrade pip
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages including:
- IBM Watson libraries
- FastAPI and Uvicorn
- Document processing libraries (PyPDF2, python-docx)
- NLP libraries (spaCy, NLTK)
- PDF generation (ReportLab)
- And more...

### 6. Download NLP Models (Optional but Recommended)

```bash
python -m spacy download en_core_web_sm
```

### 7. Configure IBM Cloud Credentials

#### Option A: Environment Variables (Recommended)

**Windows (PowerShell):**
```bash
$env:IBM_CLOUD_API_KEY="your_api_key_here"
$env:IBM_PROJECT_ID="your_project_id_here"
```

**Linux/Mac:**
```bash
export IBM_CLOUD_API_KEY="your_api_key_here"
export IBM_PROJECT_ID="your_project_id_here"
```

#### Option B: Configuration File

Edit `configs/ibm_config.yaml`:

```yaml
ibm_granite:
  api_key: "YOUR_IBM_CLOUD_API_KEY_HERE"
  project_id: "YOUR_PROJECT_ID_HERE"
```

**⚠️ Important:** Never commit credentials to version control!

### 8. Create Required Directories

```bash
# Create logs directory
New-Item -ItemType Directory -Path "logs" -Force

# Create output directory
New-Item -ItemType Directory -Path "output" -Force
```

### 9. Verify Installation

Run the demo script to verify everything is working:

```bash
python scripts/sample_syllabus_gen.py
```

If successful, you should see:
- Syllabus generation progress
- PDF exported to `output/` directory
- JSON file with syllabus data

### 10. Start the API Server

```bash
cd webapp/backend
python main.py
```

The API will be available at:
- **API:** http://localhost:8000
- **Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Getting IBM Cloud Credentials

### 1. Create IBM Cloud Account
- Go to https://cloud.ibm.com/
- Sign up for a free account (Lite tier available)

### 2. Set Up watsonx.ai
- Navigate to watsonx.ai service
- Create a new project
- Note your **Project ID**

### 3. Get API Key
- Go to IBM Cloud Dashboard
- Navigate to "Manage" → "Access (IAM)"
- Click "API keys"
- Create a new API key
- **Save it securely** - you won't be able to see it again!

### 4. Configure Granite Model Access
- Ensure you have access to IBM Granite models
- Check available models in your watsonx.ai project
- Default model: `granite-13b-chat-v2`

## Troubleshooting

### Issue: Module not found errors

**Solution:**
```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: IBM API authentication fails

**Solution:**
- Verify API key is correct
- Check project ID matches your watsonx.ai project
- Ensure API key has necessary permissions

### Issue: PDF export fails

**Solution:**
```bash
# Reinstall reportlab
pip install --upgrade reportlab
```

### Issue: File parsing errors

**Solution:**
```bash
# Install additional dependencies
pip install pdfplumber python-docx PyPDF2
```

### Issue: Port 8000 already in use

**Solution:**
```bash
# Use a different port
uvicorn main:app --host 0.0.0.0 --port 8001
```

## Development Setup

### Install Development Dependencies

```bash
pip install pytest pytest-asyncio pytest-cov black flake8 mypy
```

### Run Tests (when available)

```bash
pytest tests/
```

### Code Formatting

```bash
black src/
```

### Linting

```bash
flake8 src/
```

## Next Steps

1. ✅ Complete setup
2. 📝 Review configuration files in `configs/`
3. 🧪 Run demo script to test generation
4. 📚 Read API documentation at http://localhost:8000/docs
5. 🚀 Start building your syllabi!

## Additional Resources

- **IBM watsonx.ai Documentation:** https://www.ibm.com/docs/en/watsonx-as-a-service
- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **Project README:** See `README.md` for usage examples

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs in `logs/` directory
3. Consult project documentation in `docs/`

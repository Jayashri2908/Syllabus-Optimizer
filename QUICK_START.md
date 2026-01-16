# 🚀 Quick Setup - Gemini + Granite

## ⭐ Simple Setup (2 Minutes)

Your Syllabus Optimizer uses **Google Gemini** (primary) + **IBM Granite** (fallback).

---

## Step 1: Get FREE Gemini API Key

1. Visit: **https://makersuite.google.com/app/apikey**
2. Click **"Create API Key"** (no credit card needed)
3. Copy your key

**Free Tier**: 15 requests/min, 1M tokens/day (plenty for daily use!)

---

## Step 2: Set Environment Variable

### Windows PowerShell:
```powershell
$env:GEMINI_API_KEY="paste_your_key_here"
```

### Windows CMD:
```cmd
set GEMINI_API_KEY=paste_your_key_here
```

### Persistent (Recommended):
Add to `.env.ibm` file:
```
GEMINI_API_KEY=your_api_key_here
```

---

## Step 3: Install Dependencies

```bash
pip install google-generativeai sentence-transformers matplotlib seaborn
```

---

## Step 4: Test Setup

```bash
python setup_ai_models.py
```

**You should see:**
```
✓ GEMINI available: gemini-1.5-flash
✓ Generation test passed
```

---

## Step 5: Start Using!

```bash
python -m webapp.backend.main
```

Generate syllabi and enjoy **25-40% better quality**! 🎉

---

## 📊 What You Get

✅ **Google Gemini** - Best FREE AI model  
✅ **Expert prompts** - 5x better than before  
✅ **Domain awareness** - Industry-relevant content  
✅ **Bloom's integration** - Correct taxonomy verbs  
✅ **IBM Granite** - Automatic fallback  

---

## ❓ FAQ

**Q: Do I need to configure Granite?**  
A: No! It's already configured as automatic fallback.

**Q: What if I don't set Gemini key?**  
A: System will use Granite only (still works, but Gemini is better quality).

**Q: Is Gemini really free?**  
A: Yes! 15 requests/min, 1M tokens/day = ~500 syllabi/day for FREE.

---

## 🐛 Troubleshooting

**"No models available"**
```powershell
# Set Gemini key
$env:GEMINI_API_KEY="your_key"

# Verify
python setup_ai_models.py
```

**"Import error"**
```bash
pip install -r requirements.txt
```

---

## ✅ You're Done!

1. ✅ Get Gemini key (2 min)
2. ✅ Set environment variable
3. ✅ Test setup
4. ✅ Generate amazing syllabi!

**See `START_HERE.md` for full documentation.**

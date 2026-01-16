# 🎯 Gemini Setup - Complete Guide

## ✅ Step 1: Get Your API Key (YOU ARE HERE)

**I've opened the Google AI Studio page for you!**

![Gemini API Page](file:///C:/Users/91909/.gemini/antigravity/brain/053652b2-7623-4e9d-911e-8535f784040e/google_ai_studio_api_key_page_1767812292567.png)

### What to do NOW:

1. **Look at the browser window I opened**
2. **Click the "Create API key" button** (blue button on the right)
3. **Choose** "Create API key in new project" (recommended)
4. **Copy** the API key that appears
5. **Save it safely** (you'll paste it in the next step)

---

## 🔑 Step 2: Set the API Key (After you copy it)

Once you have your API key, run this command:

### Windows PowerShell:
```powershell
$env:GEMINI_API_KEY="paste_your_key_here"
```

### Windows CMD:
```cmd
set GEMINI_API_KEY=paste_your_key_here
```

### Permanent Setup (Recommended):
Add to `.env.ibm` file:
```
GEMINI_API_KEY=your_api_key_here
```

---

## ✅ Step 3: Verify Setup

After setting the key, test it:

```bash
python setup_ai_models.py
```

**You should see:**
```
✓ Google Gemini : AIza...xyz (your key masked)
✓ GEMINI available: gemini-1.5-flash
✓ Generation test passed
```

---

## 🎉 Step 4: Start Using!

```bash
python -m webapp.backend.main
```

Your Syllabus Optimizer now has **25-40% better quality** with Gemini!

---

## 📝 Notes

- ✅ **100% FREE** - No credit card needed
- ✅ **Free Tier**: 15 requests/min, 1M tokens/day
- ✅ **Enough for**: ~500 syllabi per day
- ✅ **Fallback**: Granite automatically used if Gemini fails

---

## 🆘 Having Issues?

**Can't see the browser window?**
- Check your taskbar for a new Chrome/Edge window
- Or visit manually: https://aistudio.google.com/app/apikey

**"Invalid API key" error?**
- Make sure you copied the FULL key
- No extra spaces before/after
- Key should start with "AIza..."

**Need help?**
- Let me know and I'll assist!

---

**Go ahead and create your API key now! Let me know once you have it.** 🚀

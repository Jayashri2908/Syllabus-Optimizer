# 🚀 OpenRouter + MiMo Setup Guide

Get **FREE** access to Xiaomi's MiMo-V2-Flash AI model and 300+ other models through OpenRouter!

## Why OpenRouter + MiMo?

✅ **100% FREE** during beta (until ~Jan 2026)  
✅ **No credit card** required  
✅ **256K context window** - handles very large syllabi  
✅ **Fast reasoning** and coding capabilities  
✅ **One API key** for 300+ models (MiMo, GPT, Claude, etc.)  
✅ **Simple setup** - takes 2 minutes

---

## 🎯 Quick Setup

### Step 1: Get Your Free API Key

1. Visit **[https://openrouter.ai](https://openrouter.ai)**
2. Click **"Sign Up"** (use Google/GitHub or email)
3. Go to **"API Keys"** in your dashboard
4. Click **"Create Key"**
5. Copy your API key

### Step 2: Set Environment Variable

Choose your shell:

**PowerShell:**
```powershell
$env:OPENROUTER_API_KEY='your_api_key_here'
```

**CMD:**
```cmd
set OPENROUTER_API_KEY=your_api_key_here
```

**Permanent (Windows):**
1. Press `Win + X` → System
2. Advanced System Settings → Environment Variables
3. Add new **User Variable**:
   - Name: `OPENROUTER_API_KEY`
   - Value: `your_api_key_here`

### Step 3: Done! 🎉

Run your Syllabus Optimizer and it will automatically use MiMo!

---

## 🔄 Model Priority

The system automatically tries models in this order:

1. **MiMo-V2-Flash** (via OpenRouter) - PRIMARY
2. **Gemini** (if you have `GEMINI_API_KEY` set) - FALLBACK 1
3. **Granite** (IBM-based) - FALLBACK 2

If OpenRouter fails or quota is exceeded, it automatically falls back to the next available model.

---

## 💡 Available Models via OpenRouter

Your OpenRouter API key gives you access to:

| Model | Provider | Cost | Use Case |
|-------|----------|------|----------|
| `xiaomi/mimo-v2-flash` | Xiaomi | FREE (beta) | **Default - Fast, accurate** |
| `openai/gpt-3.5-turbo` | OpenAI | $0.50/$1.50/M | General purpose |
| `anthropic/claude-3-haiku` | Anthropic | $0.25/$1.25/M | Fast responses |
| `meta-llama/llama-3-8b` | Meta | FREE | Open source |
| `google/gemma-2-9b` | Google | FREE | Lightweight |

To change models, edit `configs/ai_models.yaml`:
```yaml
openrouter:
  model: 'xiaomi/mimo-v2-flash'  # Change this
```

Full model list: [https://openrouter.ai/models](https://openrouter.ai/models)

---

## 🆘 Troubleshooting

### Error: "OPENROUTER not available"
- ✅ Check that you set `OPENROUTER_API_KEY` environment variable
- ✅ Restart your terminal/command prompt
- ✅ Verify the key is correct (no extra spaces)

### Error: "API key invalid"
- ✅ Make sure you copied the full API key
- ✅ Regenerate the key on [openrouter.ai](https://openrouter.ai)

### MiMo not being used?
- ✅ Check backend logs for "✓ OPENROUTER available"
- ✅ If "✗ OPENROUTER not available", the env variable isn't set
- ✅ System will automatically fall back to Gemini/Granite

### Want to use a different model?
Edit `configs/ai_models.yaml` and change the `model` field under `openrouter`.

---

## 📊 Pricing & Limits

**MiMo-V2-Flash (Current):**
- **FREE** during beta (until ~January 2026)
- After beta: $0.1/M input tokens, $0.3/M output tokens
- Very affordable compared to GPT-4

**OpenRouter Free Models:**
- Several models are permanently FREE
- Check [openrouter.ai/models](https://openrouter.ai/models) for current free options

---

## 🔗 Useful Links

- **OpenRouter Dashboard**: [https://openrouter.ai/keys](https://openrouter.ai/keys)
- **Model Explorer**: [https://openrouter.ai/models](https://openrouter.ai/models)
- **Pricing**: [https://openrouter.ai/pricing](https://openrouter.ai/pricing)
- **API Docs**: [https://openrouter.ai/docs](https://openrouter.ai/docs)

---

## ℹ️ How It Works

OpenRouter provides a **unified API** that connects to multiple AI providers. Instead of managing separate API keys for OpenAI, Anthropic, Google, etc., you use one OpenRouter key to access all of them.

The Syllabus Optimizer uses OpenRouter's **OpenAI-compatible API**, so integration is simple and reliable.

**Your API Key → OpenRouter → MiMo/Other Models → Your Syllabus**

---

Need help? Check the main [README.md](README.md) or raise an issue!

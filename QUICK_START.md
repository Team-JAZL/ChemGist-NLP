# ⚡ ChemGist Integration - Quick Start (60 seconds)

## What's New?
Your fine-tuned chemistry model is now integrated with the chatbot frontend. When you ask a question, it uses your actual trained model instead of hardcoded responses.

## Start the Chatbot (3 steps)

### Step 1: Open Terminal
Navigate to your project folder:
```powershell
cd "C:\Users\user\OneDrive\Desktop\App Projects\ChemGist - NLP\ChemGist-NLP"
```

### Step 2: Start the Server
```powershell
python api.py
```

**First time?** This downloads the base model (~4GB). Takes 2-5 minutes. Subsequent runs: instant.

### Step 3: Open in Browser
Once you see `✓✓✓ MODEL FULLY LOADED AND READY ✓✓✓`:
```
http://localhost:5000
```

## Try These Questions

The model will now answer questions using your fine-tuned weights:

```
1. "What is the molecular weight of water?"
2. "Provide information about Ammonia (SMILES: N)"
3. "What is the chemical formula for ethanol?"
4. "Explain the structure of aspirin"
5. "What properties does methane have?"
```

## Architecture

```
Browser (frontend.html)
    ↓ (WebSocket/HTTP)
Flask API (api.py)
    ↓
Tokenizer (tokenizer.json)
    ↓
Fine-tuned Model (adapter_model.safetensors)
    ↓
Base Model (Phi-3-mini)
    ↓
Generated Answer
    ↑ (back to browser)
```

## Key Files Created/Modified

| File | What It Does |
|------|-------------|
| **api.py** | ✨ NEW - Flask server + model loader |
| **frontend.html** | 🔧 UPDATED - Now calls real API instead of mock |
| **run_server.py** | ✨ NEW - Simple launcher |
| **CHATBOT_SETUP.md** | 📖 NEW - Full documentation |

## Verification

Check if working:
```powershell
curl http://localhost:5000/health
```

Should return:
```json
{"status":"healthy","model_loaded":true,"device":"cuda:0","timestamp":"..."}
```

## Next Steps

1. ✅ Start the server: `python api.py`
2. ✅ Open browser: `http://localhost:5000`
3. ✅ Ask chemistry questions
4. 🔄 Model learns from each interaction
5. 📊 View chat history (stored in localStorage)

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Connection error" | Is `api.py` running? |
| "Model not loaded" | Wait a few minutes on first run |
| "Port 5000 in use" | Kill other process or change port in api.py |
| Very slow responses | Normal on CPU, check GPU with `nvidia-smi` |

---

🎉 **You now have a fully functional AI chemistry chatbot!**

For detailed docs, see: `CHATBOT_SETUP.md`

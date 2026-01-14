# Local-LLM
A simple real-time chat interface that runs locally using Ollama + FastAPI.  

## Prerequisites
- **Windows / macOS / Linux**
- Python 3.10+
- Enough disk space: ~3–10 GB for the model + Python packages
- Internet connection (only needed for first-time Ollama + model download)

## Installation & Running

### Install Ollama (the LLM server)
1. Go to the official website:  
   https://ollama.com/download

2. Download and run the installer for your OS (`OllamaSetup.exe` on Windows)

3. After installation:
   - On Windows: You should see a blue llama icon in the system tray (bottom-right)
   - On macOS/Linux: Ollama starts automatically in the background

4. Open a terminal / Command Prompt / PowerShell and verify:

   ```bash
   ollama --version
   ```

### Start the Ollama Server
Open a dedicated terminal and run:

```bash
run ollama run llama3.2
```


### Run the Chat Application
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

```bash
(Or python main.py)
```

## Open the Chat in Your Browser
Go to: http://localhost:8000/

You should now see a nice dark chat interface. Type something and press Enter.

## Troubleshooting Quick Checklist
* Connection error → Is ollama serve running? Test with curl http://localhost:11434
* Model not found → Run ollama list — make sure llama3.2:3b (or your chosen model) appears
* Command 'ollama' not found → Reinstall from https://ollama.com/download
* Slow generation → Use smaller model (1b/3b) or close other heavy apps
* Want another model? → Just ollama pull <modelname> and change OLLAMA_MODEL env var or code default
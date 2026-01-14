from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests
import json
import os
from typing import AsyncGenerator

app = FastAPI(title="Local Ollama Chat with Streaming")

# Mount static folder for HTML/CSS/JS
app.mount("/static", StaticFiles(directory="static"), name="static")

class Prompt(BaseModel):
    prompt: str
    model: str = None  # optional, can override via env or query

def get_ollama_config():
    return {
        "host": os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        "model": os.getenv("OLLAMA_MODEL", "llama3.2:latest")  # or deepseek-r1, qwen2.5, etc.
    }

@app.get("/")
async def serve_ui():
    """Serve the nice chat interface"""
    return FileResponse("static/index.html")

@app.post("/api/chat-stream")
async def chat_stream(prompt: Prompt) -> StreamingResponse:
    """
    Stream tokens from Ollama in real-time using SSE
    Frontend sees typewriter effect
    """
    config = get_ollama_config()
    model = prompt.model or config["model"]
    host = config["host"]

    payload = {
        "model": model,
        "prompt": prompt.prompt,
        "stream": True,
        # Optional tuning - feel free to customize
        "options": {
            "temperature": 0.75,
            "top_p": 0.9
        }
    }

    def generate() -> AsyncGenerator[str, None]:
        try:
            with requests.post(
                f"{host}/api/generate",
                json=payload,
                stream=True,
                timeout=None  # local → no need for short timeout
            ) as response:
                response.raise_for_status()

                for line in response.iter_lines():
                    if not line:
                        continue

                    try:
                        chunk = json.loads(line.decode("utf-8"))
                        
                        if "response" in chunk and chunk["response"]:
                            yield f"data: {json.dumps({'token': chunk['response']})}\n\n"
                        
                        if chunk.get("done", False):
                            yield "data: [DONE]\n\n"
                            break
                            
                    except json.JSONDecodeError:
                        continue  # skip malformed lines (rare)
                    except Exception as e:
                        yield f"data: {json.dumps({'error': str(e)})}\n\n"
                        break

        except requests.RequestException as e:
            yield f"data: {json.dumps({'error': f'Ollama connection failed: {str(e)}'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': f'Unexpected error: {str(e)}'})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
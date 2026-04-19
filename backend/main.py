import json
import os

import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import requests


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not set")

genai.configure(api_key=GEMINI_API_KEY)
#model = genai.GenerativeModel("gemma-4-31b-it")

app = FastAPI(title="LLM Chat API")

# Allow requests from the React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Request model ────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []   # [{"role": "user"|"assistant", "content": "..."}]
    session_id: str = "default"

# Tools

def geocode_city(name: str):
    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": name,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    response = requests.get(url, params=params, timeout=5)

    if response.status_code != 200:
        return {"error": "Geocoding request failed"}

    data = response.json()

    if not data.get("results"):
        return {"error": f"City '{name}' not found"}

    result = data["results"][0]

    return {
        "name": result["name"],
        "latitude": result["latitude"],
        "longitude": result["longitude"],
        "country": result.get("country"),
        "admin1": result.get("admin1")  # region
    }
    
def get_current_weather(latitude: float, longitude: float):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": True,
        "timezone": "auto"
    }

    response = requests.get(url, params=params, timeout=5)

    if response.status_code != 200:
        return {"error": "Weather fetch failed"}

    data = response.json()
    current = data.get("current_weather", {})

    return {
        "temperature": current.get("temperature"),
        "windspeed": current.get("windspeed"),
        "time": current.get("time")
    }

tools = [
    {
        "function_declarations": [
            {
                "name": "geocode_city",
                "description": "Convert a city name into latitude and longitude MUST be called before weather lookup if only a city name is provided.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "City name, e.g. Oulu"
                        }
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "get_current_weather",
                "description": "Get current weather from coordinates",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "latitude": {"type": "number"},
                        "longitude": {"type": "number"}
                    },
                    "required": ["latitude", "longitude"]
                }
            }
        ]
    }
]


model = genai.GenerativeModel("gemma-4-31b-it", tools=tools)

# ─── Endpoints ────────────────────────────────────────────────────────────────
    
@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):

    def generate():
        # Convert history to Gemini format
        contents = []
        for msg in request.history:
            contents.append({
                "role": msg["role"],
                "parts": [{"text": msg["content"]}]
            })

        contents.append({
            "role": "user",
            "parts": [{"text": request.message}]
        })

        while True:
            response = model.generate_content(contents, stream=True)

            function_call = None

            for chunk in response:
                candidate = chunk.candidates[0]
                parts = candidate.content.parts

                for part in parts:
                    # ✅ TEXT STREAMING
                    if hasattr(part, "text") and part.text:
                        event = json.dumps({
                            "type": "text",
                            "content": part.text
                        })
                        yield f"data: {event}\n\n"

                    # ✅ FUNCTION CALL DETECTION
                    if hasattr(part, "function_call") and part.function_call:
                        function_call = part.function_call

            # 🔁 If model requested a tool → execute it
            if function_call:
                name = function_call.name
                args = dict(function_call.args)

                if name == "geocode_city":
                    result = geocode_city(**args)
                elif name == "get_current_weather":
                    result = get_current_weather(**args)
                else:
                    raise HTTPException(400, f"Unknown function: {name}")

                # Add model's function call message
                contents.append({
                    "role": "model",
                    "parts": [{
                        "function_call": {
                            "name": name,
                            "args": args
                        }
                    }]
                })

                # Add tool response
                contents.append({
                    "role": "user",
                    "parts": [{
                        "function_response": {
                            "name": name,
                            "response": result
                        }
                    }]
                })

                # 🔁 Continue loop → model will now generate final answer
                continue

            # ✅ DONE (no function call)
            usage = response.usage_metadata
            done_event = json.dumps({
                "type": "done",
                "usage": {
                    "input_tokens": usage.prompt_token_count,
                    "output_tokens": usage.candidates_token_count,
                },
            })
            yield f"data: {done_event}\n\n"
            break

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
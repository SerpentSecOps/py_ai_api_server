# Writing Applications for the LLM API Server

This API server exposes a RESTful interface for local LLM (Large Language Model) inference using **FastAPI** and **llama-cpp-python**. You can write applications in any language that can make HTTP requests (Python, JavaScript, cURL, etc.).

---

## 1. Start the Server

* Use the **GUI** (`control_panel.py`) to start the server and load a model.
* The default server address is: `http://127.0.0.1:8000` (configured in `llm_config.ini`).

---

## 2. API Endpoints

### Health Check

* **Endpoint:** `GET /health`
* **Purpose:** Check if the server is running and whether a model is loaded.
* **Response Example:**

```json
{  
  "status": "ok",  
  "model_loaded": true  
}
```

### Text Generation

* **Endpoint:** `POST /api/v1/generate`
* **Purpose:** Generate text completions from the loaded model.
* **Request Body (JSON):**

```json
{  
  "prompt": "Your prompt here",  
  "max_tokens": 50,  
  "temperature": 0.7,  
  "top_p": 0.95  
}
```

* **Parameters:**

  * `prompt` *(string)*: The input text.
  * `max_tokens` *(int, optional)*: Maximum tokens to generate.
  * `temperature` *(float, optional)*: Sampling temperature.
  * `top_p` *(float, optional)*: Nucleus sampling parameter.

* **Response Example:**

```json
{  
  "choices": [    
    {      
      "text": " generated text...",      
      "index": 0,      
      "logprobs": null,      
      "finish_reason": "length"    
    }  
  ],  
  "usage": {    
    "prompt_tokens": 5,    
    "completion_tokens": 50,    
    "total_tokens": 55  
  }  
}
```

* **Error Example (if model not loaded):**

```json
{  
  "error": "Model is not currently loaded."  
}
```

---

## 3. Example Clients

### Python

See `api_test.py` for a working example. Minimal version:

```python
import requests

BASE_URL = "http://127.0.0.1:8000"

# Health check
r = requests.get(f"{BASE_URL}/health")
print(r.json())

# Text generation
payload = {
    "prompt": "The capital of France is",
    "max_tokens": 50,
    "temperature": 0.7,
    "top_p": 0.95
}

r = requests.post(f"{BASE_URL}/api/v1/generate", json=payload)
print(r.json())
```

### JavaScript (Node.js)

```javascript
import fetch from "node-fetch";

const BASE_URL = "http://127.0.0.1:8000";

// Health check
const health = await fetch(`${BASE_URL}/health`);
console.log(await health.json());

// Text generation
const response = await fetch(`${BASE_URL}/api/v1/generate`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    prompt: "The capital of France is",
    max_tokens: 50,
    temperature: 0.7,
    top_p: 0.95
  })
});

console.log(await response.json());
```

### cURL

```bash
# Health check
curl http://127.0.0.1:8000/health

# Text generation
curl -X POST http://127.0.0.1:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "The capital of France is",
    "max_tokens": 50,
    "temperature": 0.7,
    "top_p": 0.95
  }'
```

---

## 4. Customization

* Change server host/port in **`llm_config.ini`**.
* Add authentication or more endpoints by extending the **FastAPI app** in `main.py`.

---

## 5. Troubleshooting

* If you get a **503 error**, load a model using the GUI.
* Check logs in the GUI or in the log file specified in `llm_config.ini`.
* For more details, see the code in:

  * `main.py`
  * `model_loader.py`
  * `api_test.py`

---

✅ Ready to build apps in Python, JavaScript, or directly via cURL!

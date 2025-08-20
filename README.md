Writing Applications for the LLM API Server
This API server exposes a RESTful interface for local LLM (Large Language Model) inference using FastAPI and llama-cpp-python. You can write apps in any language that can make HTTP requests (Python, JavaScript, etc.).

1. Start the Server
Use the GUI (control_panel.py) to start the server and load a model.
The default server address is http://127.0.0.1:8000 (see llm_config.ini).
2. API Endpoints
Health Check
Endpoint: GET /health
Purpose: Check if the server is running and if a model is loaded.
Response Example:

{  "status": "ok",  "model_loaded": true}
Text Generation
Endpoint: POST /api/v1/generate

Purpose: Generate text completions from the loaded model.

Request Body (JSON):


{  "prompt": "Your prompt here",  "max_tokens": 50,  "temperature": 0.7,  "top_p": 0.95}
prompt (string): The input text.
max_tokens (int, optional): Maximum tokens to generate.
temperature (float, optional): Sampling temperature.
top_p (float, optional): Nucleus sampling parameter.
Response Example:


{  "choices": [    {      "text": " generated text...",      "index": 0,      "logprobs": null,      "finish_reason": "length"    }  ],  "usage": {    "prompt_tokens": 5,    "completion_tokens": 50,    "total_tokens": 55  }}
Error Example (if model not loaded):


{  "error": "Model is not currently loaded."}
3. Example Python Client
See api_test.py for a working example. Here’s a minimal version:


import requestsBASE_URL = "http://127.0.0.1:8000"# Health checkr = requests.get(f"{BASE_URL}/health")print(r.json())# Text generationpayload = {    "prompt": "The capital of France is",    "max_tokens": 50,    "temperature": 0.7,    "top_p": 0.95}r = requests.post(f"{BASE_URL}/api/v1/generate", json=payload)print(r.json())
4. Customization
Change server host/port in llm_config.ini.
Add authentication or more endpoints by extending the FastAPI app in main.py.
5. Troubleshooting
If you get a 503 error, load a model using the GUI.
Check logs in the GUI or the log file specified in llm_config.ini.
For more details, see the code in main.py, model_loader.py, and api_test.py. Let me know if you want a template for another language or more advanced usage!

import requests
import json

# The base URL for your running API server
BASE_URL = "http://127.0.0.1:8000"

def test_health_check():
    """Tests the /health endpoint to see if the server is running."""
    print("--- Testing Health Check ---")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check successful!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Health check failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Error: Could not connect to the server at {BASE_URL}.")
        print("Please ensure the main application is running and the server has been started.")
    print("\n" + "="*30 + "\n")

def test_generation():
    """Tests the /api/v1/generate endpoint with a sample prompt."""
    print("--- Testing Text Generation ---")
    
    url = f"{BASE_URL}/api/v1/generate"
    
    # The payload for the request. You can change the prompt and parameters.
    payload = {
        "prompt": "The capital of France is",
        "max_tokens": 50,
        "temperature": 0.7,
        "top_p": 0.95
    }

    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            print("✅ Generation request successful!")
            response_data = response.json()
            # Pretty-print the JSON response
            print("Response:")
            print(json.dumps(response_data, indent=2))
            
            # Extract and print the generated text
            if 'choices' in response_data and len(response_data['choices']) > 0:
                generated_text = response_data['choices'][0]['text']
                print("\n--- Generated Text ---")
                print(payload["prompt"] + generated_text)
                print("----------------------")

        elif response.status_code == 503:
             print("❌ Generation failed: The model is not loaded on the server.")
             print("Please use the GUI to load a model before running this test.")
        else:
            print(f"❌ Generation failed with status code: {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Error: Could not connect to the server at {BASE_URL}.")
        print("Please ensure the main application is running and the server has been started.")
    print("\n" + "="*30 + "\n")


if __name__ == "__main__":
    print("Running API Server Tests...")
    print("Ensure the main application is running, the server is started, and a model is loaded.")
    print("-" * 30)
    test_health_check()
    test_generation()
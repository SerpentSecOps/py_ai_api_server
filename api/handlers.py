# This file is kept for structural purposes.
# In this refactored version, the primary API logic is contained within `main.py`
# for simplicity. If the API grows, you can move the logic for different
# endpoints into handler functions within this file to keep `main.py` clean.

class APIRequestHandler:
    def __init__(self, app_state):
        self.app_state = app_state
        
    async def handle_generate(self, request: dict):
        if not self.app_state.is_model_loaded:
            return {"error": "Model not loaded"}, 503
        
        response = self.app_state.model_loader.create_completion(request)
        return response
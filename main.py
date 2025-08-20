import tkinter as tk
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import threading
import queue
import sys
import os
from gui.control_panel import ControlPanelGUI
from config.settings import ConfigManager, ConfigError

# Determine the base directory of the running application
# This makes sure that paths work correctly even when the script is run from another directory.
APP_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class AppState:
    """A simple class to hold the application's state."""
    def __init__(self):
        self.config_manager = None
        self.model_loader = None
        self.is_model_loaded = False
        self.is_server_running = False
        self.gui_log_queue = queue.Queue()
        self.server_instance = None # To hold the Uvicorn server instance

def main():
    """Main function to initialize and run the application."""
    app_state = AppState()

    # Initialize configuration using a dynamic path
    try:
        config_path = os.path.join(APP_BASE_DIR, 'llm_config.ini')
        app_state.config_manager = ConfigManager(config_path=config_path)
    except ConfigError as e:
        # If config fails, we can't proceed. Show error in a simple Tk window.
        root = tk.Tk()
        root.title("Configuration Error")
        label = tk.Label(root, text=f"Failed to load configuration:\n{e}\n\nPlease fix llm_config.ini and restart.", padx=20, pady=20)
        label.pack()
        root.mainloop()
        sys.exit(1)
        
    # --- FastAPI Server Setup ---
    app = FastAPI(
        title="LLM API Server",
        description="An API to serve local LLM models using llama-cpp-python.",
        version="1.0.0"
    )

    # Add CORS middleware to allow all origins, which is useful for web-based GUIs.
    # This directly addresses the CORS issues you were facing.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allows all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
    )

    @app.post("/api/v1/generate")
    async def generate(request: dict):
        """
        API endpoint to handle text generation requests.
        It uses the loaded model to create a completion.
        """
        if not app_state.is_model_loaded or app_state.model_loader is None:
            return {"error": "Model is not currently loaded."}, 503
        
        try:
            # The actual generation is handled by the model loader
            response = app_state.model_loader.create_completion(request)
            return response
        except Exception as e:
            app_state.gui_log_queue.put(f"API Error: {e}")
            return {"error": f"An error occurred during generation: {e}"}, 500

    @app.get("/health")
    async def health_check():
        """Health check endpoint to verify server status."""
        return {"status": "ok", "model_loaded": app_state.is_model_loaded}

    def run_server():
        """Target function to run the Uvicorn server in a separate thread."""
        config = uvicorn.Config(
            app,
            host=app_state.config_manager.server_config.host,
            port=app_state.config_manager.server_config.port
        )
        app_state.server_instance = uvicorn.Server(config)
        app_state.server_instance.run()
        # After server stops, update state
        app_state.is_server_running = False
        app_state.gui_log_queue.put("Server has stopped.")


    # --- GUI Setup and Main Loop ---
    # The GUI runs in the main thread.
    gui = ControlPanelGUI(app_state, run_server)
    gui.mainloop()

if __name__ == "__main__":
    main()
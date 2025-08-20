from llama_cpp import Llama
import os

class ModelLoader:
    """Handles the loading of the Llama.cpp model and text generation."""
    def __init__(self, config_manager, logger_func):
        self.config = config_manager.model_config
        self.logger = logger_func
        
        if not self.config.model_path or not os.path.exists(self.config.model_path):
            raise FileNotFoundError(f"Model path is invalid or not set. Please select a valid model file. Path: '{self.config.model_path}'")
            
        self.model = self._load_model()

    def _load_model(self):
        """Initializes and returns the Llama.cpp model object."""
        self.logger("Initializing Llama.cpp model...")
        self.logger(f"Model Path: {self.config.model_path}")
        self.logger(f"GPU Layers: {self.config.n_gpu_layers}")
        
        try:
            llm = Llama(
                model_path=self.config.model_path,
                lora_path=self.config.lora_path if self.config.lora_path else None,
                n_ctx=self.config.max_tokens,
                n_gpu_layers=self.config.n_gpu_layers,
                flash_attn=self.config.flash_attention,
                verbose=True
            )
            return llm
        except Exception as e:
            self.logger(f"Fatal error during model loading: {e}")
            raise
    
    def get_layer_count(self):
        """Gets the layer count from the loaded model's metadata."""
        if not self.model or not hasattr(self.model, 'metadata'):
            return 0
        
        # Find the block_count key in the metadata dictionary
        for key, value in self.model.metadata.items():
            if key.endswith('.block_count'):
                return int(value)
        return 0

    @staticmethod
    def get_model_max_layers(model_path: str):
        """
        Reliably gets the model's layer count by initializing it minimally
        and reading the metadata dictionary provided by llama-cpp-python.
        """
        if not model_path or not os.path.exists(model_path):
            return None
        
        llm = None
        try:
            # Load with minimal settings just to parse metadata
            llm = Llama(model_path=model_path, n_ctx=1, n_gpu_layers=0, verbose=False)
            
            # The metadata is stored in a dictionary on the Llama object
            if hasattr(llm, 'metadata'):
                for key, value in llm.metadata.items():
                    if key.endswith('.block_count'):
                        return int(value)
            return None
        except Exception as e:
            print(f"Error reading model metadata: {e}")
            return None
        finally:
            # Ensure the temporary model object is released
            if llm:
                del llm


    def create_completion(self, data):
        """
        Creates a model completion for a given prompt and parameters.
        'data' is expected to be a dictionary from the API request.
        """
        if not self.model:
            return {"error": "Model is not loaded."}
        
        prompt = data.get("prompt", "")
        max_tokens = data.get("max_tokens", self.config.max_tokens)
        temperature = data.get("temperature", self.config.temperature)
        top_p = data.get("top_p", self.config.top_p)
        stream = data.get("stream", self.config.streaming)

        if stream:
            return {"error": "Streaming is not implemented in this synchronous endpoint."}

        self.logger(f"Creating completion for prompt: '{prompt[:50]}...'")
        
        output = self.model(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stop=None,
            echo=False
        )

        self.logger("Completion generated successfully.")
        
        return {
            "choices": [{
                "text": output["choices"][0]["text"],
                "index": 0,
                "logprobs": None,
                "finish_reason": "length" 
            }],
            "usage": output["usage"]
        }
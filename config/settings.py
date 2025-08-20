import configparser
import os

class ConfigError(Exception):
    """Custom exception for configuration errors."""
    pass

class ServerConfig:
    """Holds server-related configuration."""
    def __init__(self, config):
        self.host = config.get('host', '127.0.0.1')
        self.port = config.getint('port', 8000)
        self.api_keys = [key.strip() for key in config.get('api_keys', '').split(',') if key]
        self.log_level = config.get('log_level', 'INFO')
        self.log_file = config.get('log_file', 'llm_server.log')
        self.use_auth = config.getboolean('use_auth', False)
        self.batch_size = config.getint('batch_size', 4)

class ModelConfig:
    """Holds model-related configuration."""
    def __init__(self, config):
        self.model_path = config.get('model_path')
        if not self.model_path or self.model_path == '/path/to/your/model.gguf':
            pass 
        elif not os.path.exists(self.model_path):
            raise ConfigError(f"Model path '{self.model_path}' in config file does not exist.")
        self.lora_path = config.get('lora_path', None)
        self.model_type = config.get('model_type', 'llama')
        self.max_tokens = config.getint('max_tokens', 2048)
        self.temperature = config.getfloat('temperature', 0.7)
        self.top_p = config.getfloat('top_p', 0.95)
        self.n_gpu_layers = config.getint('n_gpu_layers', 0)
        self.streaming = config.getboolean('streaming', False)
        self.flash_attention = config.getboolean('flash_attention', False)

class ConfigManager:
    """Reads and manages configuration from the .ini file."""
    def __init__(self, config_path):
        self.config_path = config_path
        if not self.config_path or not os.path.exists(self.config_path):
            raise ConfigError(f"Configuration file not found at path: {self.config_path}")
        
        self.config = configparser.ConfigParser()
        self.config.read(self.config_path)
        
        self._validate_sections()
        
        self.server_config = ServerConfig(self.config['server'])
        self.model_config = ModelConfig(self.config['model'])

    def _validate_sections(self):
        required_sections = ['server', 'model']
        for section in required_sections:
            if section not in self.config:
                raise ConfigError(f"Missing required section in config file: '[{section}]'")

    def save_config_value(self, section, key, value):
        """Saves a single value to the llm_config.ini file."""
        try:
            self.config.set(section, key, str(value))
            with open(self.config_path, 'w') as configfile:
                self.config.write(configfile)
        except Exception as e:
            raise ConfigError(f"Failed to save config value for {section}.{key}: {e}")
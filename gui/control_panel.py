import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import queue
import threading
import time
import sys
import os

class ControlPanelGUI(tk.Tk):
    """The main GUI for the application, built with Tkinter."""
    def __init__(self, app_state, server_start_func):
        super().__init__()
        self.app_state = app_state
        self.server_start_func = server_start_func
        self.server_thread = None
        self.ui_queue = queue.Queue() # Queue for UI updates from other threads

        self.title("LLM API Control Panel")
        self.geometry("900x700")

        self.style = ttk.Style(self)
        self.style.theme_use('clam')

        self.create_widgets()
        
        self.after(100, self.process_ui_queue)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Initial check for model layers if path is valid
        if self.app_state.config_manager.model_config.model_path and os.path.exists(self.app_state.config_manager.model_config.model_path):
            self.detect_model_layers(self.app_state.config_manager.model_config.model_path)


    def create_widgets(self):
        """Create and layout all the GUI widgets in a more organized fashion."""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.rowconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)

        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=0, column=0, sticky="ew", pady=5)
        controls_frame.columnconfigure(1, weight=1)

        server_group = ttk.LabelFrame(controls_frame, text="Server Controls", padding="10")
        server_group.grid(row=0, column=0, padx=5, pady=5, sticky="ns")
        
        self.start_server_button = ttk.Button(server_group, text="Start Server", command=self.start_server)
        self.start_server_button.pack(pady=5, fill=tk.X)

        self.stop_server_button = ttk.Button(server_group, text="Stop Server", command=self.stop_server, state=tk.DISABLED)
        self.stop_server_button.pack(pady=5, fill=tk.X)

        model_group = ttk.LabelFrame(controls_frame, text="Model Controls", padding="10")
        model_group.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        model_group.columnconfigure(0, weight=1)

        model_path_frame = ttk.Frame(model_group)
        model_path_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=5)
        model_path_frame.columnconfigure(1, weight=1)
        
        self.model_path_var = tk.StringVar(value=self.app_state.config_manager.model_config.model_path)
        ttk.Label(model_path_frame, text="Model Path:").grid(row=0, column=0, padx=5)
        ttk.Entry(model_path_frame, textvariable=self.model_path_var, state='readonly').grid(row=0, column=1, sticky="ew", padx=5)
        self.select_model_button = ttk.Button(model_path_frame, text="Select Model", command=self.select_model)
        self.select_model_button.grid(row=0, column=2, padx=5)

        gpu_slider_frame = ttk.Frame(model_group)
        gpu_slider_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)
        gpu_slider_frame.columnconfigure(1, weight=1)

        self.gpu_layers_var = tk.IntVar(value=self.app_state.config_manager.model_config.n_gpu_layers)
        ttk.Label(gpu_slider_frame, text="GPU Layers:").grid(row=0, column=0, padx=5)
        self.gpu_slider = ttk.Scale(gpu_slider_frame, from_=0, to=128, orient=tk.HORIZONTAL, variable=self.gpu_layers_var, command=self.on_gpu_slider_change)
        self.gpu_slider.grid(row=0, column=1, sticky="ew", padx=5)
        self.gpu_layers_label = ttk.Label(gpu_slider_frame, text=f"{self.gpu_layers_var.get()}", width=4)
        self.gpu_layers_label.grid(row=0, column=2, padx=5)

        button_frame = ttk.Frame(model_group)
        button_frame.grid(row=2, column=0, columnspan=2, pady=5)

        self.load_model_button = ttk.Button(button_frame, text="Load Model", command=self.load_model, state=tk.DISABLED)
        self.load_model_button.pack(side=tk.LEFT, padx=5)

        self.unload_model_button = ttk.Button(button_frame, text="Unload Model", command=self.unload_model, state=tk.DISABLED)
        self.unload_model_button.pack(side=tk.LEFT, padx=5)

        log_frame = ttk.LabelFrame(main_frame, text="Application Logs", padding="10")
        log_frame.grid(row=1, column=0, sticky="nsew", pady=5)
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)

        self.log_text = scrolledtext.ScrolledText(log_frame, state='disabled', wrap=tk.WORD, bg="#2b2b2b", fg="white", font=("Consolas", 10))
        self.log_text.grid(row=0, column=0, sticky="nsew")

    def on_gpu_slider_change(self, value):
        """Handles the GPU layer slider value change."""
        layers = int(float(value))
        self.gpu_layers_label.config(text=f"{layers}")
        # Debounce saving to config to avoid writing on every pixel change
        if hasattr(self, '_slider_job'):
            self.after_cancel(self._slider_job)
        self._slider_job = self.after(500, self.save_gpu_layers, layers)

    def save_gpu_layers(self, layers):
        self.app_state.config_manager.model_config.n_gpu_layers = layers
        self.app_state.config_manager.save_config_value('model', 'n_gpu_layers', layers)
        self.log(f"GPU layer setting saved: {layers}")
        if self.app_state.is_model_loaded:
            self.log("Unload and reload the model to apply new GPU layer count.")

    def select_model(self):
        filepath = filedialog.askopenfilename(title="Select a GGUF Model File", filetypes=(("GGUF files", "*.gguf"), ("All files", "*.*")))
        if filepath:
            self.log(f"New model path selected: {filepath}")
            self.model_path_var.set(filepath)
            try:
                self.app_state.config_manager.save_config_value('model', 'model_path', filepath)
                self.app_state.config_manager.model_config.model_path = filepath
                self.log("Model path updated. Detecting max GPU layers...")
                # Start a thread to detect the model's layers
                threading.Thread(target=self.detect_model_layers, args=(filepath,), daemon=True).start()
            except Exception as e:
                self.log(f"Error saving new model path: {e}")
                messagebox.showerror("Error", f"Could not save new model path to config file.\n{e}")

    def detect_model_layers(self, model_path):
        from core.model_loader import ModelLoader
        try:
            max_layers = ModelLoader.get_model_max_layers(model_path)
            if max_layers is not None:
                self.ui_queue.put(('update_slider', max_layers))
            else:
                self.log("Could not determine model layer count from GGUF metadata.")
        except Exception as e:
            self.log(f"Failed to detect model layers: {e}")

    def log(self, message):
        self.ui_queue.put(('log', f"[{time.strftime('%H:%M:%S')}] {message}"))

    def process_ui_queue(self):
        try:
            while True:
                msg_type, data = self.ui_queue.get_nowait()
                if msg_type == 'log':
                    if "Server has stopped" in data:
                        self.start_server_button.config(state=tk.NORMAL)
                        self.stop_server_button.config(state=tk.DISABLED)
                    self.log_text.config(state='normal')
                    self.log_text.insert(tk.END, data + '\n')
                    self.log_text.config(state='disabled')
                    self.log_text.see(tk.END)
                elif msg_type == 'update_slider':
                    max_layers = data
                    self.log(f"Detected {max_layers} layers in model. Updating slider.")
                    self.gpu_slider.config(to=max_layers)
                    if self.gpu_layers_var.get() > max_layers:
                        self.gpu_layers_var.set(max_layers)
                    self.gpu_layers_label.config(text=f"{self.gpu_layers_var.get()}")

        except queue.Empty:
            pass
        finally:
            self.after(100, self.process_ui_queue)

    def start_server(self):
        self.log("Starting server...")
        self.server_thread = threading.Thread(target=self.server_start_func, daemon=True)
        self.server_thread.start()
        
        self.app_state.is_server_running = True
        self.start_server_button.config(state=tk.DISABLED)
        self.stop_server_button.config(state=tk.NORMAL)
        self.load_model_button.config(state=tk.NORMAL)
        host = self.app_state.config_manager.server_config.host
        port = self.app_state.config_manager.server_config.port
        self.log(f"Server starting, health check at http://{host}:{port}/health")

    def stop_server(self):
        if self.app_state.server_instance:
            self.log("Stopping server...")
            self.app_state.server_instance.should_exit = True
            self.stop_server_button.config(state=tk.DISABLED)
        else:
            self.log("Server instance not found. Cannot stop.")

    def load_model(self):
        self.log("Model loading process started...")
        self.load_model_button.config(state=tk.DISABLED)

        def load_model_thread():
            try:
                from core.model_loader import ModelLoader
                self.app_state.model_loader = ModelLoader(self.app_state.config_manager, self.log)
                self.app_state.is_model_loaded = True
                self.log("✅ Model loaded successfully.")
                self.unload_model_button.config(state=tk.NORMAL)
                # Update slider again on successful load to be sure
                max_layers = self.app_state.model_loader.get_layer_count()
                if max_layers:
                    self.ui_queue.put(('update_slider', max_layers))
            except Exception as e:
                self.log(f"❌ Error loading model: {e}")
                messagebox.showerror("Model Load Error", f"Failed to load the model. Please check the path and file integrity.\n\nError: {e}")
            finally:
                if not self.app_state.is_model_loaded:
                    self.load_model_button.config(state=tk.NORMAL)

        threading.Thread(target=load_model_thread, daemon=True).start()

    def unload_model(self):
        self.log("Unloading model...")
        self.app_state.model_loader = None
        self.app_state.is_model_loaded = False
        import gc
        gc.collect()
        self.log("Model unloaded.")
        self.load_model_button.config(state=tk.NORMAL)
        self.unload_model_button.config(state=tk.DISABLED)
        
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit? This will stop the server and exit the application."):
            if self.app_state.server_instance:
                self.app_state.server_instance.should_exit = True
            self.destroy()
            sys.exit(0)
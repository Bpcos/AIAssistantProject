import os
from PyQt6.QtCore import QThread, pyqtSignal, QUrl
from PyQt6.QtMultimedia import QMediaPlayer

class WorkerThread(QThread):
    finished = pyqtSignal(str)
    
    def __init__(self, model, user_input):
        super().__init__()
        self.model = model
        self.user_input = user_input

    def run(self):
        response = self.model.chat(self.user_input)
        self.finished.emit(response)

class AppController:
    def __init__(self):
        self.view = None
        self.model = None
        # Default starting character folder name
        self.current_char = "CyberBot" 
        self.char_base_path = os.path.join(os.getcwd(), "Characters")

    def set_view(self, view):
        self.view = view
        # Connect the media player signal to know when video stops
        self.view.media_player.mediaStatusChanged.connect(self.on_media_status_changed)
        self.load_character_data()

    def set_model(self, model):
        self.model = model

    def change_character(self, char_name):
        self.current_char = char_name
        self.load_character_data()

    def load_character_data(self):
        """
        Loads the config.txt prompt and sets the idle image.
        """
        char_dir = os.path.join(self.char_base_path, self.current_char)
        
        # 1. Load Idle Image
        idle_path = os.path.join(char_dir, "idle.png")
        if os.path.exists(idle_path):
            self.view.set_idle_image(idle_path)
        else:
            # Fallback if image is missing, just to prevent crashes
            print(f"Warning: No idle.png found in {char_dir}")

        # 2. Load System Prompt from config.txt
        config_path = os.path.join(char_dir, "config.txt")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding='utf-8') as f:
                    new_prompt = f.read().strip() # Strip whitespace
                
                # FIX: Only update if the file actually contains text
                if new_prompt and self.model:
                    self.model.update_system_instruction(new_prompt)
                elif not new_prompt:
                    print(f"Warning: {config_path} is empty. Using previous prompt.")
            except Exception as e:
                print(f"Error reading config: {e}")

    def handle_user_input(self, text):
        # 1. Trigger Action Video
        char_dir = os.path.join(self.char_base_path, self.current_char)
        video_path = os.path.join(char_dir, "action.mp4")
        
        if os.path.exists(video_path):
            self.view.play_video(video_path)
        
        # 2. Run Model in background
        self.worker = WorkerThread(self.model, text)
        self.worker.finished.connect(self.handle_ai_response)
        self.worker.start()

    def handle_ai_response(self, response):
        self.view.update_chat(response)
        # Note: We let the video finish playing naturally. 
        # When it ends, on_media_status_changed handles the switch back.

    def on_media_status_changed(self, status):
        """Called when video player state changes"""
        # QMediaPlayer.MediaStatus.EndOfMedia is usually value 7 or 6 depending on Qt version
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            # Revert to idle image
            char_dir = os.path.join(self.char_base_path, self.current_char)
            idle_path = os.path.join(char_dir, "idle.png")
            self.view.set_idle_image(idle_path)
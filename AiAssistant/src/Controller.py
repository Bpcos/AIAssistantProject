import os
from PyQt6.QtCore import QThread, pyqtSignal

class WorkerThread(QThread):
    """Thread to run LLM API so GUI doesn't freeze"""
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
        self.current_char = "CyberBot" # Default
        self.char_path = os.path.join(os.getcwd(), "characters")

    def set_view(self, view):
        self.view = view
        self.update_character_assets()

    def set_model(self, model):
        self.model = model

    def change_character(self, char_name):
        self.current_char = char_name
        self.update_character_assets()

    def update_character_assets(self):
        # Load idle animation immediately
        idle_path = os.path.join(self.char_path, self.current_char, "idle.gif")
        self.view.set_animation(idle_path)

    def handle_user_input(self, text):
        # 1. Change animation to "Thinking"
        think_path = os.path.join(self.char_path, self.current_char, "thinking.gif")
        self.view.set_animation(think_path)

        # 2. Run Model in background thread
        self.worker = WorkerThread(self.model, text)
        self.worker.finished.connect(self.handle_ai_response)
        self.worker.start()

    def handle_ai_response(self, response):
        # 3. Update Chat
        self.view.update_chat(response)

        # 4. Determine Animation based on Response Content
        # Check for code blocks to trigger "Coding" animation
        if "```" in response or "def " in response or "import " in response:
            anim_file = "coding.gif"
        else:
            # Default to "Speaking" then back to "Idle"
            # (For simplicity here, we just set to speaking/idle)
            anim_file = "speaking.gif" # ideally play for X seconds then go idle
        
        anim_path = os.path.join(self.char_path, self.current_char, anim_file)
        if not os.path.exists(anim_path):
            anim_path = os.path.join(self.char_path, self.current_char, "idle.gif") # Fallback
            
        self.view.set_animation(anim_path)
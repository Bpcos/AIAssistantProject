import os
import glob
import re # For extracting action text
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtMultimedia import QMediaPlayer
from src.Tools import ToolKit 

class WorkerThread(QThread):
    chat_finished = pyqtSignal(str) # Emits text response
    video_ready = pyqtSignal(str)   # Emits path to generated video
    
    def __init__(self, model, user_input, use_veo, idle_image_path):
        super().__init__()
        self.model = model
        self.user_input = user_input
        self.use_veo = use_veo
        self.idle_path = idle_image_path

    def run(self):
        # 1. Get Text Response
        response_text = self.model.chat(self.user_input)
        self.chat_finished.emit(response_text)
        
        # 2. If Veo is enabled, generate video
        if self.use_veo and self.idle_path:
            # Parse prompt: Use action if found, else dialogue
            veo_prompt = self.construct_veo_prompt(response_text)
            
            video_path, error = self.model.generate_veo_video(veo_prompt, self.idle_path)
            
            if video_path:
                self.video_ready.emit(video_path)
            else:
                print(error) # Print error to console

    def construct_veo_prompt(self, text):
        """
        Logic: If text contains *actions*, use them. 
        Else, use the first sentence as dialogue.
        """
        # Look for text between asterisks e.g. *waves hand*
        actions = re.findall(r'\*(.*?)\*', text)
        
        if actions:
            # Use the first action found
            action_desc = actions[0]
            return f"Cinematic shot. The character performs this action: {action_desc}. High quality, 4k, fluid motion."
        else:
            # Use the first sentence for dialogue lip-sync style context
            # (Note: Veo doesn't do perfect lip sync yet, but it creates the 'vibe')
            first_sentence = text.split('.')[0]
            if len(first_sentence) > 100: first_sentence = first_sentence[:100]
            return f"Cinematic shot. The character is speaking conversationally. Context: {first_sentence}. Maintain eye contact, subtle movement."

class AppController:
    def __init__(self):
        self.view = None
        self.model = None
        self.current_char = "CyberBot" 
        self.char_base_path = os.path.join(os.getcwd(), "Characters")
        self.worker = None

    def set_view(self, view):
        self.view = view
        self.view.media_player.mediaStatusChanged.connect(self.on_media_status_changed)
        
        chars = self.scan_characters()
        self.view.populate_char_selector(chars)
        
        if self.current_char in chars:
            self.view.set_current_char(self.current_char)
        elif chars:
            self.current_char = chars[0]
            self.view.set_current_char(self.current_char)
            
        self.load_character_data()

    def scan_characters(self):
        if not os.path.exists(self.char_base_path):
            try: os.makedirs(self.char_base_path)
            except OSError: return []
        character_list = [
            name for name in os.listdir(self.char_base_path)
            if os.path.isdir(os.path.join(self.char_base_path, name))
        ]
        return sorted(character_list)

    def set_model(self, model):
        self.model = model

    def change_character(self, char_name):
        if not char_name: return
        self.current_char = char_name
        self.load_character_data()

    def load_character_data(self):
        char_dir = os.path.join(self.char_base_path, self.current_char)
        
        idle_path = os.path.join(char_dir, "idle.png")
        if os.path.exists(idle_path):
            self.view.set_idle_image(idle_path)
        
        base_prompt = "You are a helpful assistant."
        config_path = os.path.join(char_dir, "config.txt")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding='utf-8') as f:
                base_prompt = f.read().strip()

        anim_prompt = self.generate_animation_prompt(char_dir)
        final_system_prompt = f"{base_prompt}\n\n{anim_prompt}"
        
        if self.model:
            self.model.update_system_instruction(final_system_prompt)

    def generate_animation_prompt(self, char_dir):
        # (Same as before)
        mp4_files = glob.glob(os.path.join(char_dir, "*.mp4"))
        available_videos = [os.path.splitext(os.path.basename(f))[0] for f in mp4_files]
        if not available_videos: return ""

        descriptions = {}
        desc_path = os.path.join(char_dir, "animations.txt")
        if os.path.exists(desc_path):
            try:
                with open(desc_path, "r", encoding='utf-8') as f:
                    for line in f:
                        if ":" in line:
                            key, val = line.split(":", 1)
                            descriptions[key.strip().lower()] = val.strip()
            except Exception: pass

        prompt = "AVAILABLE ANIMATIONS (Use 'set_animation' tool):\n"
        for video in available_videos:
            desc = descriptions.get(video.lower(), "General purpose animation.")
            prompt += f"- '{video}': {desc}\n"
        return prompt

    def handle_user_input(self, text, use_veo=False):
        # Reset tool state
        ToolKit.selected_animation = None 
        
        # Get current idle image path for Veo
        char_dir = os.path.join(self.char_base_path, self.current_char)
        idle_path = os.path.join(char_dir, "idle.png")

        # Start Worker
        self.worker = WorkerThread(self.model, text, use_veo, idle_path)
        self.worker.chat_finished.connect(self.handle_text_response)
        self.worker.video_ready.connect(self.handle_generated_video)
        self.worker.start()

    def handle_text_response(self, response):
        self.view.update_chat(response)
        
        # If Veo is NOT enabled, run the standard animation logic immediately
        if not self.view.veo_checkbox.isChecked():
            self.play_standard_animation()

    def handle_generated_video(self, video_path):
        # This is called when Veo finishes (could be 10-20 seconds later)
        self.view.play_video(video_path)

    def play_standard_animation(self):
        """The original logic for playing pre-canned MP4s"""
        char_dir = os.path.join(self.char_base_path, self.current_char)
        anim_name = ToolKit.selected_animation
        video_path = None

        if anim_name:
            potential_path = os.path.join(char_dir, f"{anim_name}.mp4")
            if os.path.exists(potential_path):
                video_path = potential_path

        if not video_path:
            default_path = os.path.join(char_dir, "default.mp4")
            if os.path.exists(default_path):
                video_path = default_path
            
        if video_path:
            self.view.play_video(video_path)

    def on_media_status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            char_dir = os.path.join(self.char_base_path, self.current_char)
            idle_path = os.path.join(char_dir, "idle.png")
            self.view.set_idle_image(idle_path)
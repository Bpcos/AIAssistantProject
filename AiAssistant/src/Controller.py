import os
import glob
import re  # Added for parsing actions
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtMultimedia import QMediaPlayer
from src.Tools import ToolKit 

class WorkerThread(QThread):
    chat_finished = pyqtSignal(str) # Emits text response
    audio_ready = pyqtSignal(str)   # Emits path to generated audio (TTS)
    video_ready = pyqtSignal(str)   # Emits path to generated video (Veo)
    
    def __init__(self, model, user_input, use_veo, idle_image_path):
        super().__init__()
        self.model = model
        self.user_input = user_input
        self.use_veo = use_veo
        self.idle_path = idle_image_path

    def run(self):
        # 1. Get Text Response (Always happens first)
        response_text = self.model.chat(self.user_input)
        self.chat_finished.emit(response_text)
        
        # 2. Logic Split: Choose Veo Video OR Standalone TTS
        if self.use_veo and self.idle_path:
            # --- VEO MODE ---
            # Extract visual actions (*text*) to guide the video generation
            veo_prompt = self.construct_veo_prompt(response_text)
            video_path, error = self.model.generate_veo_video(veo_prompt, self.idle_path)
            
            if video_path:
                self.video_ready.emit(video_path)
            elif error:
                print(error)
        else:
            # --- STANDARD MODE ---
            # Veo is off. The Model.py generate_speech function already strips 
            # asterisks automatically, so we pass the full text.
            audio_path = self.model.generate_speech(response_text)
            if audio_path:
                self.audio_ready.emit(audio_path)

    def construct_veo_prompt(self, text):
        """
        Parses the model response to create a specific video generation prompt.
        If actions are found inside *asterisks*, they become the primary directive.
        """
        # 1. extract content between *asterisks* (non-greedy)
        actions = re.findall(r'\*(.*?)\*', text)
        
        if actions:
            # Combine all found actions into one visual description
            visual_description = " ".join(actions)
            # Prompt specifically for the action
            prompt = (f"Cinematic shot. The character performs the following action: "
                      f"{visual_description}. High quality, detailed movement, consistent identity.")
            print(f"DEBUG: Extracted Action Prompt -> {prompt}")
            return prompt
        
        else:
            # Fallback: No specific action found, generate conversational video
            first_sentence = text.split('.')[0]
            if len(first_sentence) > 100: first_sentence = first_sentence[:100]
            
            prompt = (f"Cinematic shot. The character is speaking conversationally. "
                      f"Context: {first_sentence}. Maintain eye contact, subtle movement.")
            print(f"DEBUG: Conversational Prompt -> {prompt}")
            return prompt

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

        # --- UPDATED INSTRUCTION ---
        # We explicitly instruct the model how to format actions for the video generator.
        action_instruction = (
            "IMPORTANT VISUAL INSTRUCTIONS:\n"
            "If the user asks you to perform a physical action or spell, "
            "describe the visual action vividly between asterisks "
            "(e.g., *I raise my hands and blue flames erupt from my palms*). "
            "This description is used to generate the video visualization of you. "
            "Keep the spoken response separate."
        )

        anim_prompt = self.generate_animation_prompt(char_dir)
        
        # Combine everything
        final_system_prompt = f"{base_prompt}\n\n{action_instruction}\n\n{anim_prompt}"
        
        if self.model:
            self.model.update_system_instruction(final_system_prompt)

    def generate_animation_prompt(self, char_dir):
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

        prompt = "AVAILABLE PRE-RENDERED ANIMATIONS (Use 'set_animation' tool only if these fit exactly):\n"
        for video in available_videos:
            desc = descriptions.get(video.lower(), "General purpose animation.")
            prompt += f"- '{video}': {desc}\n"
        return prompt

    def handle_user_input(self, text, use_veo=False):
        ToolKit.selected_animation = None 
        char_dir = os.path.join(self.char_base_path, self.current_char)
        idle_path = os.path.join(char_dir, "idle.png")

        self.worker = WorkerThread(self.model, text, use_veo, idle_path)
        self.worker.chat_finished.connect(self.handle_text_response)
        self.worker.audio_ready.connect(self.handle_audio_response)
        self.worker.video_ready.connect(self.handle_generated_video)
        self.worker.start()

    def handle_text_response(self, response):
        self.view.update_chat(response)

    def handle_audio_response(self, audio_path):
        """Called only if Veo is disabled"""
        self.view.play_audio(audio_path)

    def handle_generated_video(self, video_path):
        """Called when Veo finishes (includes embedded audio)"""
        self.view.play_video(video_path)

    def on_media_status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            char_dir = os.path.join(self.char_base_path, self.current_char)
            idle_path = os.path.join(char_dir, "idle.png")
            self.view.set_idle_image(idle_path)
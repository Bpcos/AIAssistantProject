import google.generativeai as genai_legacy # Legacy SDK for Chat/Tools
from google import genai # New SDK for Veo/Audio
from google.genai import types
from src.Tools import ToolKit
import time
import os
import requests 
import base64
import re
import struct

class AIModel:
    def __init__(self, api_key, system_instruction, veo_api_key=None):
        # Configure Legacy Chat (Gemini 2.5 Flash) for Logic/Text
        genai_legacy.configure(api_key=api_key)
        self.api_key = api_key
        self.veo_api_key = veo_api_key or api_key 
        self.tools = ToolKit.tools_list
        self.init_model(system_instruction)

    def init_model(self, prompt):
        if not prompt or not prompt.strip():
            prompt = "You are a helpful assistant."

        # Use Legacy SDK for Chat/Tools to maintain stability with Controller
        self.model = genai_legacy.GenerativeModel(
            model_name='gemini-2.5-flash',
            tools=self.tools,
            system_instruction=prompt
        )
        self.chat_session = self.model.start_chat(enable_automatic_function_calling=True)

    def update_system_instruction(self, new_prompt):
        self.init_model(new_prompt)

    def chat(self, user_input):
        try:
            response = self.chat_session.send_message(user_input)
            if response.candidates and response.candidates[0].content.parts:
                return response.text
            else:
                return "(Action executed)"
        except ValueError:
            return "(Action executed)"
        except Exception as e:
            return f"Error communicating with Gemini: {str(e)}"

    def save_pcm_as_wav(self, filename, pcm_bytes, sample_rate=24000):
        """
        Wraps Raw PCM data with a valid RIFF WAV header.
        Gemini 2.5 TTS output is typically 24kHz, 16-bit, Mono.
        """
        try:
            with open(filename, 'wb') as f:
                # WAV Header Construction
                # 1. RIFF Chunk Descriptor
                f.write(b'RIFF') 
                # Chunk Size (FileSize - 8 bytes) = 36 + data_length
                f.write(struct.pack('<I', 36 + len(pcm_bytes))) 
                f.write(b'WAVE') 
                
                # 2. "fmt " Sub-chunk
                f.write(b'fmt ') 
                f.write(struct.pack('<I', 16)) # Subchunk1Size (16 for PCM)
                f.write(struct.pack('<H', 1))  # AudioFormat (1 for PCM)
                f.write(struct.pack('<H', 1))  # NumChannels (1 for Mono)
                f.write(struct.pack('<I', sample_rate)) # SampleRate
                
                # ByteRate = SampleRate * NumChannels * BitsPerSample/8
                byte_rate = sample_rate * 1 * 2 
                f.write(struct.pack('<I', byte_rate))
                
                # BlockAlign = NumChannels * BitsPerSample/8
                f.write(struct.pack('<H', 2)) 
                # BitsPerSample
                f.write(struct.pack('<H', 16)) 
                
                # 3. "data" Sub-chunk
                f.write(b'data') 
                f.write(struct.pack('<I', len(pcm_bytes)))
                f.write(pcm_bytes)
                
            print(f"WAV saved successfully: {filename}")
            return True
        except Exception as e:
            print(f"Error saving WAV: {e}")
            return False

    def generate_speech(self, text_to_speak):
        """
        Generates audio using Gemini 2.5 TTS model.
        Returns path to a WAV file.
        """
        if not text_to_speak or len(text_to_speak) < 2:
            return None

        # Clean text to remove asterisks actions e.g. *laughs*
        clean_text = re.sub(r'\*.*?\*', '', text_to_speak).strip()
        if not clean_text: return None

        print(f"Generating TTS (gemini-2.5-flash-preview-tts) for: {clean_text[:50]}...")
        
        try:
            client = genai.Client(api_key=self.veo_api_key)
            
            # Request AUDIO. Note: We do NOT specify mime_type="audio/mp3" 
            # because the model returns Raw PCM by default.
            response = client.models.generate_content(
                model='gemini-2.5-flash-preview-tts', 
                contents=clean_text,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name="Puck" 
                            )
                        )
                    )
                )
            )

            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    data = part.inline_data.data
                    
                    # Handle data types (SDK v0.1+ can return raw bytes or base64 string)
                    if isinstance(data, str):
                        audio_bytes = base64.b64decode(data)
                    else:
                        audio_bytes = data

                    # Save as .wav using the helper to add headers
                    filename = "temp_tts_output.wav"
                    if self.save_pcm_as_wav(filename, audio_bytes, sample_rate=24000):
                        return filename
                    
            print("No audio data found in TTS response.")
            return None

        except Exception as e:
            print(f"Gemini TTS Error: {e}")
            return None

    def generate_veo_video(self, prompt_text, image_path):
        """
        Generates a video using Veo 3 (via New GenAI SDK).
        """
        if not self.veo_api_key:
            return None, "Error: VEO_API_KEY not set."

        print(f"Generating Veo 3 video for: {prompt_text}")

        try:
            client = genai.Client(api_key=self.veo_api_key)

            if not os.path.exists(image_path):
                return None, f"Image not found: {image_path}"
            
            with open(image_path, "rb") as f:
                raw_bytes = f.read()

            image_payload = {"image_bytes": raw_bytes, "mime_type": "image/png"}

            config = types.GenerateVideosConfig(
                aspect_ratio="9:16",
                last_frame=image_payload 
            )

            operation = client.models.generate_videos(
                model="veo-3.1-generate-preview", 
                prompt=prompt_text,
                image=image_payload, 
                config=config        
            )
            
            print("Veo 3 Operation started...")

            while not operation.done:
                time.sleep(5) 
                operation = client.operations.get(operation)
                print("Veo 3 Status: Processing...")

            if not operation.response.generated_videos:
                return None, "No video generated in response."

            video_result = operation.response.generated_videos[0]
            output_filename = "temp_veo_gen.mp4"
            
            try:
                if hasattr(video_result.video, 'uri') and video_result.video.uri:
                    video_uri = video_result.video.uri
                    if "key=" not in video_uri:
                        separator = "&" if "?" in video_uri else "?"
                        download_url = f"{video_uri}{separator}key={self.veo_api_key}"
                    else:
                        download_url = video_uri
                        
                    resp = requests.get(download_url)
                    if resp.status_code == 200:
                        with open(output_filename, "wb") as f:
                            f.write(resp.content)
                    else:
                        return None, f"Download Error {resp.status_code}: {resp.text}"

                elif hasattr(video_result.video, 'name') and video_result.video.name:
                    file_bytes = client.files.download(name=video_result.video.name)
                    with open(output_filename, "wb") as f:
                        f.write(file_bytes)
                else:
                    return None, "Could not find valid download URI or Name."

            except Exception as download_err:
                return None, f"Download Exception: {str(download_err)}"

            return output_filename, None

        except Exception as e:
            return None, f"Veo 3 Generation Failed: {str(e)}"
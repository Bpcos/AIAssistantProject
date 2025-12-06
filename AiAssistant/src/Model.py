import google.generativeai as genai_legacy # Legacy SDK for Chat/Tools
from google import genai # New SDK for Veo 3
from google.genai import types
from src.Tools import ToolKit
import time
import os
import requests 

class AIModel:
    def __init__(self, api_key, system_instruction, veo_api_key=None):
        # Configure Legacy Chat (Gemini 2.5 Flash)
        genai_legacy.configure(api_key=api_key)
        self.api_key = api_key
        self.veo_api_key = veo_api_key 
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
            
            # FIX: Safely check if the response has text content.
            # If the model runs a tool but says nothing, accessing .text directly throws a ValueError.
            if response.candidates and response.candidates[0].content.parts:
                return response.text
            else:
                return "(Action executed)" # Fallback response for silent actions

        except ValueError:
            # Catch the specific "Invalid operation" if .text is accessed on empty content
            return "(Action executed)"
        except Exception as e:
            return f"Error communicating with Gemini: {str(e)}"

    def generate_veo_video(self, prompt_text, image_path):
        """
        Generates a video using Veo 3 (via New GenAI SDK).
        """
        if not self.veo_api_key:
            return None, "Error: VEO_API_KEY not set."

        print(f"Generating Veo 3 video for: {prompt_text}")

        try:
            # 1. Initialize New Client
            client = genai.Client(api_key=self.veo_api_key)

            # 2. Prepare Image Input
            if not os.path.exists(image_path):
                return None, f"Image not found: {image_path}"
            
            with open(image_path, "rb") as f:
                raw_bytes = f.read()

            # Image Payload (Used for both Start and End frames)
            image_payload = {
                "image_bytes": raw_bytes, 
                "mime_type": "image/png"
            }

            # 3. Configure Veo 3
            # - aspect_ratio="9:16" for Portrait (Mobile/App style)
            # - last_frame=image_payload forces the video to Loop (Start == End)
            config = types.GenerateVideosConfig(
                aspect_ratio="9:16",
                last_frame=image_payload 
            )

            # 4. Start Generation Operation
            operation = client.models.generate_videos(
                model="veo-3.1-generate-preview", 
                prompt=prompt_text,
                image=image_payload, # Start Frame
                config=config        # Config with End Frame & Ratio
            )
            
            print("Veo 3 Operation started...")

            # 5. Poll for Completion
            while not operation.done:
                time.sleep(5) 
                operation = client.operations.get(operation)
                print("Veo 3 Status: Processing...")

            # 6. Retrieve Result
            if not operation.response.generated_videos:
                return None, "No video generated in response."

            video_result = operation.response.generated_videos[0]
            output_filename = "temp_veo_gen.mp4"
            
            # 7. Manual Download Logic
            try:
                # CASE A: Result has a Direct URI (Most common for Veo)
                if hasattr(video_result.video, 'uri') and video_result.video.uri:
                    video_uri = video_result.video.uri
                    print(f"Downloading video from URI...")
                    
                    # Append API Key if not present (Required for authentication)
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

                # CASE B: Result is a File API Reference
                elif hasattr(video_result.video, 'name') and video_result.video.name:
                    print(f"Downloading video via Client API...")
                    file_bytes = client.files.download(name=video_result.video.name)
                    with open(output_filename, "wb") as f:
                        f.write(file_bytes)

                else:
                    return None, "Could not find valid download URI or Name."

            except Exception as download_err:
                import traceback
                traceback.print_exc()
                return None, f"Download Exception: {str(download_err)}"

            print(f"Veo 3 Video Saved: {output_filename}")
            return output_filename, None

        except Exception as e:
            import traceback
            traceback.print_exc()
            return None, f"Veo 3 Generation Failed: {str(e)}"
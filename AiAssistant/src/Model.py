import google.generativeai as genai
from src.Tools import ToolKit
import requests
import json
import time
import base64
import os

class AIModel:
    def __init__(self, api_key, system_instruction, veo_api_key=None):
        genai.configure(api_key=api_key)
        self.api_key = api_key
        self.veo_api_key = veo_api_key # Dedicated key for Video
        self.tools = ToolKit.tools_list
        self.init_model(system_instruction)

    def init_model(self, prompt):
        if not prompt or not prompt.strip():
            prompt = "You are a helpful assistant."

        self.model = genai.GenerativeModel(
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
            return response.text
        except Exception as e:
            return f"Error communicating with Gemini: {str(e)}"

        
    def generate_veo_video(self, prompt_text, image_path):
        """
        Generates a video using Veo (via REST API) using the image as the first frame.
        """
        if not self.veo_api_key:
            return None, "Error: VEO_API_KEY not set."

        print(f"Generating Veo video for: {prompt_text}")

        # 1. Encode Image
        try:
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode("utf-8")
        except Exception as e:
            return None, f"Error reading idle image: {e}"

        # 2. Prepare API Request
        url = f"https://generativelanguage.googleapis.com/v1beta/models/veo-2.0-generate-001:predictLongRunning?key={self.veo_api_key}"
        headers = {'Content-Type': 'application/json'}
        
        payload = {
            "instances": [
                {
                    "prompt": prompt_text,
                    "image": {
                        "bytesBase64Encoded": image_data,
                        "mimeType": "image/png"
                    }
                }
            ]
        }

        # 3. Start Operation
        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code != 200:
                return None, f"API Error: {response.text}"
            
            operation_name = response.json().get('name')
            print(f"Veo Operation Started: {operation_name}")
        except Exception as e:
            return None, f"Request Failed: {e}"

        # 4. Poll for Completion
        video_uri = None
        for _ in range(60): # Increased timeout just in case
            time.sleep(2)
            
            poll_url = f"https://generativelanguage.googleapis.com/v1beta/{operation_name}?key={self.veo_api_key}"
            poll_resp = requests.get(poll_url)
            poll_data = poll_resp.json()
            
            if poll_data.get('done'):
                if 'error' in poll_data:
                    return None, f"Gen Failed: {poll_data['error']}"
                
                try:
                    # FIX: Adjusted parsing to match Veo 2.0 structure
                    # Structure: response -> generateVideoResponse -> generatedSamples -> [0] -> video -> uri
                    result_payload = poll_data.get('response', {})
                    
                    if 'generateVideoResponse' in result_payload:
                        samples = result_payload['generateVideoResponse'].get('generatedSamples', [])
                        if samples:
                            video_uri = samples[0]['video']['uri']
                            break
                    
                    # Fallback for alternative structures
                    elif 'generatedVideos' in result_payload:
                        video_uri = result_payload['generatedVideos'][0]['video']['uri']
                        break
                        
                    else:
                        print("DEBUG JSON:", poll_data)
                        return None, "Unknown JSON structure in response"
                        
                except KeyError as e:
                     print("DEBUG JSON:", poll_data)
                     return None, f"Parsing Error: {e}"

        if not video_uri:
            return None, "Timeout waiting for video generation."

        # 5. Download Video
        try:
            # FIX: The file URI requires authentication. Append the API Key.
            if "?key=" not in video_uri and "&key=" not in video_uri:
                download_url = f"{video_uri}&key={self.veo_api_key}"
            else:
                download_url = video_uri

            print(f"Downloading from: {download_url}")
            video_data = requests.get(download_url).content
            
            output_filename = "temp_veo_gen.mp4"
            with open(output_filename, "wb") as f:
                f.write(video_data)
                
            return output_filename, None
        except Exception as e:
            return None, f"Download failed: {e}"

  
    
import google.generativeai as genai
from src.Tools import ToolKit

class AIModel:
    def __init__(self, api_key, system_instruction):
        genai.configure(api_key=api_key)
        self.api_key = api_key # Store for re-init if needed
        self.tools = ToolKit.tools_list
        
        # Initial Setup
        self.init_model(system_instruction)

    def init_model(self, prompt):
        self.model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            tools=self.tools,
            system_instruction=prompt
        )
        self.chat_session = self.model.start_chat(enable_automatic_function_calling=True)

    def update_system_instruction(self, new_prompt):
        """Re-initializes the model with a new character persona"""
        # Gemini API doesn't allow changing system prompt on existing object easily,
        # so we re-instantiate the model. 
        # Note: This resets conversation history (Memory).
        self.init_model(new_prompt)

    def chat(self, user_input):
        try:
            response = self.chat_session.send_message(user_input)
            return response.text
        except Exception as e:
            return f"Error communicating with Gemini: {str(e)}"

  
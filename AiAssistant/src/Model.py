    
import json
import google.generativeai as genai
from src.Tools import ToolKit

class AIModel:
    def __init__(self, api_key, system_instruction):
        # 1. Configure API
        # The correct library 'google.generativeai' has the 'configure' method
        genai.configure(api_key=api_key)
        
        # 2. Initialize Model with Tools
        # We pass the actual python functions here.
        self.model = genai.GenerativeModel(
            model_name='gemini-2.5-flash', # "flash" is fast and free-tier eligible
            tools=ToolKit.tools_list,
            system_instruction=system_instruction
        )
        
        # 3. Start a Chat Session
        # enable_automatic_function_calling=True satisfies the "Action Executor" requirement
        # by automatically running the code when the model requests it.
        self.chat_session = self.model.start_chat(enable_automatic_function_calling=True)

    def chat(self, user_input):
        """
        Sends message to Gemini, it executes tools if needed, and returns the text.
        """
        try:
            response = self.chat_session.send_message(user_input)
            return response.text
        except Exception as e:
            return f"Error communicating with Gemini: {str(e)}"

  
import sys
import os
from dotenv import load_dotenv  # Import this
from PyQt6.QtWidgets import QApplication
from src.Model import AIModel
from src.View import AIView
from src.Controller import AppController

# 1. Load the .env file
load_dotenv() 

# 2. Get the key safely
API_KEY = os.getenv("GEMINI_API_KEY")

def main():
    app = QApplication(sys.argv)
    
    # Check if key is missing
    if not API_KEY:
        print("CRITICAL ERROR: GEMINI_API_KEY not found in environment or .env file.")
        sys.exit(1)

    # Initialize MVC components
    controller = AppController()
    
    # ... (Rest of your code remains the same)
    system_prompt = """
    You are an intelligent animated assistant. 
    1. If the user asks for system info, use the get_system_info tool.
    2. If the user asks to save something, use the create_file tool.
    3. If the user asks for math, use the calculate tool.
    4. If the user asks to open an app (like calculator or notepad), use the open_application tool.
    
    Be concise and helpful. 
    If you open an app, simply say "Opening [App Name]" and trigger the tool.
    """
    
    model = AIModel(api_key=API_KEY, system_instruction=system_prompt)
    view = AIView(controller)

    controller.set_model(model)
    controller.set_view(view)

    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
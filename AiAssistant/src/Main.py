import sys
import os
from PyQt6.QtWidgets import QApplication
from src.Model import AIModel
from src.View import AIView
from src.Controller import AppController

# API KEY SETUP
# Ideally, load this from an environment variable for safety
API_KEY = "sk-proj-..." 

def main():
    app = QApplication(sys.argv)

    # Initialize MVC components
    controller = AppController()
    
    # Load prompt from the character's config file in a real app
    # Here is the Prompt Engineering requirement:
    system_prompt = """
    You are an intelligent animated assistant. 
    1. If the user asks for system info, use the get_system_info tool.
    2. If the user asks to save something, use the create_file tool.
    3. If the user asks for math, use the calculate tool.
    Be concise and helpful.
    """
    
    model = AIModel(api_key=API_KEY, character_prompt=system_prompt)
    view = AIView(controller)

    # Wire them up
    controller.set_model(model)
    controller.set_view(view)

    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

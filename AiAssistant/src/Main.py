import sys
import os
from dotenv import load_dotenv 
from PyQt6.QtWidgets import QApplication
from src.Model import AIModel
from src.View import AIView
from src.Controller import AppController

load_dotenv() 

API_KEY = os.getenv("GEMINI_API_KEY")
VEO_API_KEY = os.getenv("VEO_API_KEY") # Load the Veo key

def main():
    app = QApplication(sys.argv)
    
    if not API_KEY:
        print("CRITICAL ERROR: GEMINI_API_KEY not found.")
        sys.exit(1)

    # Initialize MVC
    controller = AppController()
    
    system_prompt = "You are a helpful assistant."
    
    # Pass both keys to the model
    model = AIModel(api_key=API_KEY, veo_api_key=VEO_API_KEY, system_instruction=system_prompt)
    view = AIView(controller)

    controller.set_model(model)
    controller.set_view(view)

    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
import platform
import os
import subprocess 

class ToolKit:
    
    # Default fallback
    selected_animation = "default"

    def set_animation(animation_name: str):
        """
        Selects the video animation to play. 
        Args:
            animation_name: The name of the animation file (without .mp4 extension).
        """
        # We accept whatever the AI sends. Validation happens in Controller.
        # We strip whitespace and lowercase it to be safe.
        clean_name = animation_name.strip().lower()
        ToolKit.selected_animation = clean_name
        return f"Animation requested: {clean_name}"

    def get_system_info():
        return f"{platform.system()} {platform.release()} ({platform.machine()})"

    def create_file(filename: str, content: str):
        try:
            with open(filename, 'w') as f:
                f.write(content)
            return f"Successfully created file: {filename}"
        except Exception as e:
            return f"Error creating file: {str(e)}"

    def calculate(expression: str):
        try:
            allowed_chars = "0123456789+-*/(). "
            if any(c not in allowed_chars for c in expression):
                return "Error: Unsafe characters detected."
            print (expression)
            return str(eval(expression))
        except Exception as e:
            return f"Math Error: {str(e)}"

    def open_application(app_name: str):
        system = platform.system()
        app_map = {
            "calculator": "calc", "calc": "calc",
            "notepad": "notepad", "paint": "mspaint",
            "cmd": "cmd", "explorer": "explorer"
        }
        target = app_map.get(app_name.lower(), app_name)
        try:
            if system == "Windows":
                subprocess.Popen(target, shell=True)
            elif system == "Darwin": 
                subprocess.Popen(["open", "-a", target])
            elif system == "Linux":
                subprocess.Popen([target])
            return f"Attempting to open {app_name}..."
        except Exception as e:
            return f"Failed to open {app_name}. Error: {e}"

    tools_list = [get_system_info, create_file, calculate, open_application, set_animation]
import platform
import os
import subprocess # Needed to launch apps

class ToolKit:
    """
    A collection of tools that the Gemini model can execute.
    """

    def get_system_info():
        """
        Returns information about the current operating system, release, and machine architecture.
        Use this when the user asks for system specs or computer details.
        """
        return f"{platform.system()} {platform.release()} ({platform.machine()})"

    def create_file(filename: str, content: str):
        """
        Creates a new text file with the specified content.
        Args:
            filename: The name of the file to create (e.g., 'notes.txt').
            content: The text content to write into the file.
        """
        try:
            with open(filename, 'w') as f:
                f.write(content)
            return f"Successfully created file: {filename}"
        except Exception as e:
            return f"Error creating file: {str(e)}"

    def calculate(expression: str):
        """
        Evaluates a mathematical expression safely.
        Args:
            expression: A string containing the math to solve (e.g., '2 + 2 * 5').
        """
        try:
            allowed_chars = "0123456789+-*/(). "
            if any(c not in allowed_chars for c in expression):
                return "Error: Unsafe characters detected."
            return str(eval(expression))
        except Exception as e:
            return f"Math Error: {str(e)}"

    def open_application(app_name: str):
        """
        Opens a local application on the computer.
        Args:
            app_name: The name of the application (e.g., 'notepad', 'calc', 'chrome').
        """
        system = platform.system()
        
        # Common mapping for Windows commands
        # You can add more apps to this dictionary!
        app_map = {
            "calculator": "calc",
            "calc": "calc",
            "notepad": "notepad",
            "paint": "mspaint",
            "cmd": "cmd",
            "explorer": "explorer"
        }
        
        target = app_map.get(app_name.lower(), app_name)

        try:
            if system == "Windows":
                subprocess.Popen(target, shell=True)
            elif system == "Darwin": # macOS
                subprocess.Popen(["open", "-a", target])
            elif system == "Linux":
                subprocess.Popen([target])
            return f"Attempting to open {app_name}..."
        except Exception as e:
            return f"Failed to open {app_name}. Error: {e}"

    # IMPORTANT: Add the new function to this list!
    tools_list = [get_system_info, create_file, calculate, open_application]
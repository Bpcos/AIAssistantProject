import platform
import os

class ToolKit:
    """
    A collection of tools that the Gemini model can execute.
    The docstrings are CRITICAL here; Gemini reads them to understand the tool.
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

    # List of functions to pass to the model
    tools_list = [get_system_info, create_file, calculate]
#This is a requirement for the Prompt Engineering course, 
#This will add little functions that the LLM can call to perform specific tasks.
import os
import platform
import datetime

class ToolKit:
    """
    The library of specific python commands the model can execute.
    """
    
    @staticmethod
    def get_system_info():
        """Returns OS, Version, and Machine info."""
        return f"{platform.system()} {platform.release()} ({platform.machine()})"

    @staticmethod
    def create_file(filename, content):
        """Creates a file with specific content."""
        try:
            with open(filename, 'w') as f:
                f.write(content)
            return f"Successfully created {filename}."
        except Exception as e:
            return f"Error creating file: {str(e)}"

    @staticmethod
    def calculate(expression):
        """Safe math evaluation."""
        try:
            # specific safety check to prevent code injection
            allowed_chars = "0123456789+-*/(). "
            if any(c not in allowed_chars for c in expression):
                return "Error: Unsafe characters in math expression."
            return str(eval(expression))
        except Exception as e:
            return f"Math Error: {str(e)}"

    # Define your list of available tools for the LLM
    # This is the schema sent to OpenAI
    definitions = [
        {
            "type": "function",
            "function": {
                "name": "get_system_info",
                "description": "Get the current computer's operating system information",
                "parameters": {"type": "object", "properties": {}, "required": []}
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_file",
                "description": "Create a new text file with specific content",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string"},
                        "content": {"type": "string"}
                    },
                    "required": ["filename", "content"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "calculate",
                "description": "Perform a mathematical calculation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string", "description": "The math expression e.g. 2 + 2"}
                    },
                    "required": ["expression"]
                }
            }
        }
    ]
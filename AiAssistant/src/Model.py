import json
from openai import OpenAI
from src.tools import ToolKit

class AIModel:
    def __init__(self, api_key, character_prompt):
        self.client = OpenAI(api_key=api_key)
        self.history = [
            {"role": "system", "content": character_prompt}
        ]
        self.tools = ToolKit.definitions

    def chat(self, user_input):
        """
        Sends message to LLM, handles tool calls, returns final text and state.
        """
        self.history.append({"role": "user", "content": user_input})
        
        # 1. Send request to LLM
        response = self.client.chat.completions.create(
            model="gpt-4o-mini", # or gpt-3.5-turbo
            messages=self.history,
            tools=self.tools,
            tool_choice="auto" 
        )
        
        msg = response.choices[0].message
        
        # 2. Check if LLM wants to run a specific command (Action Interpreter)
        if msg.tool_calls:
            self.history.append(msg) # Add the tool request to history
            
            # Execute the command
            for tool_call in msg.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                # Map string name to actual function
                result = "Error: Function not found"
                if func_name == "get_system_info":
                    result = ToolKit.get_system_info()
                elif func_name == "create_file":
                    result = ToolKit.create_file(args['filename'], args['content'])
                elif func_name == "calculate":
                    result = ToolKit.calculate(args['expression'])
                
                # Feed result back to LLM
                self.history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": func_name,
                    "content": result
                })
            
            # Get final answer after tool execution
            final_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=self.history
            )
            final_msg = final_response.choices[0].message.content
        else:
            final_msg = msg.content

        self.history.append({"role": "assistant", "content": final_msg})
        return final_msg
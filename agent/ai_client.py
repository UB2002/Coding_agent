import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

class AIClient:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in .env file")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def generate_plan(self, task):
        prompt = f"""
        You are an AI agent that automates tasks on a local computer. Given a task, provide a concise plan as a numbered list of executable steps. Each step must be either:
        - A command to run in the terminal (e.g., 'python script.py').
        - A file creation instruction (e.g., 'Create a file "script.py" with content: <code>').
        Do not include descriptive steps like 'Choose a language' or 'Open an editor'. Use Python for coding tasks unless specified otherwise.
        Task: {task}
        Example:
        Task: Generate and run a Python script to print 'Hello, World!'
        Plan:
        1. Create a file "hello.py" with content: print('Hello, World!')
        2. Run the command: python hello.py
        Now, provide the plan for the given task.
        """
        response = self.model.generate_content(prompt)
        
        response_text = response.text.strip()

        # Extract code from the response
        code_start = response_text.find("```") + 3  # Find the start of the code block
        code_end = response_text.find("```", code_start)  # Find the end of the code block
        code = response_text[code_start:code_end].strip()  # Extract and strip the code

        # Write the code to a JSON file
        with open("plan.json", "w") as f:
            json.dump({"code": code}, f)
        return response.text.strip()

    def refine_plan(self, task, previous_plan, error_reason):
        prompt = f"""
        The task '{task}' failed with the plan:
        {previous_plan}
        Reason for failure: {error_reason}
        Provide a refined plan as a numbered list of executable steps. Each step must be either:
        - A terminal command (e.g., 'python script.py').
        - A file creation instruction (e.g., 'Create a file "script.py" with content: <code>').
        Do not include descriptive steps like 'Choose a language' or 'Open an editor'. Fix the issue based on the error reason.
        """
        response = self.model.generate_content(prompt)
        return response.text.strip()
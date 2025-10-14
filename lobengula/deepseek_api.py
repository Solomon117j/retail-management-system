import os
import openai
from typing import Optional

class DeepseekAPI:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("Deepseek API key not found. Please set DEEPSEEK_API_KEY environment variable.")
        openai.api_key = self.api_key
        openai.api_base = "https://api.deepseek.com"
        self.model = "deepseek-chat"

    def chat(self, messages):
        """
        Send chat messages to Deepseek API and get response.

        Args:
            messages (list): List of message dicts with 'role' and 'content'

        Returns:
            str: The assistant's reply text
        """
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error communicating with Deepseek API: {str(e)}"


if __name__ == "__main__":
    # Simple test of DeepseekAPI
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("Please set DEEPSEEK_API_KEY environment variable to test DeepseekAPI.")
    else:
        deepseek = DeepseekAPI(api_key)
        test_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, Deepseek!"}
        ]
        reply = deepseek.chat(test_messages)
        print("Deepseek API reply:", reply)

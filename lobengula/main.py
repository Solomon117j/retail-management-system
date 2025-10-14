import os
import subprocess
import sys
from typing import List, Optional
from deepseek_api import DeepseekAPI




class AIAgent:
    """AI Agent with file system and Python execution capabilities."""

    def __init__(self):
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.deepseek_client = None
        if self.deepseek_api_key:
            try:
                self.deepseek_client = DeepseekAPI(self.deepseek_api_key)
            except Exception as e:
                print(f"Warning: Failed to initialize DeepseekAPI client: {e}")

    def scan_directory(self, directory_path: str) -> List[str]:
        """
        Scan and list all files in the given directory.

        Args:
            directory_path (str): Path to the directory to scan

        Returns:
            List[str]: List of file paths in the directory
        """
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Directory '{directory_path}' does not exist")

        if not os.path.isdir(directory_path):
            raise NotADirectoryError(f"'{directory_path}' is not a directory")

        files = []
        for root, dirs, filenames in os.walk(directory_path):
            for filename in filenames:
                files.append(os.path.join(root, filename))

        return files

    def read_file(self, file_path: str) -> str:
        """
        Read the contents of a file.

        Args:
            file_path (str): Path to the file to read

        Returns:
            str: Contents of the file
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{file_path}' does not exist")

        if not os.path.isfile(file_path):
            raise IsADirectoryError(f"'{file_path}' is a directory, not a file")

        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        return content

    def overwrite_file(self, file_path: str, content: str) -> None:
        """
        Overwrite the contents of a file with new content.

        Args:
            file_path (str): Path to the file to overwrite
            content (str): New content to write to the file
        """
        # Create directory if it doesn't exist
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)

    def execute_python_file(self, file_path: str) -> str:
        """
        Execute a Python file using the Python interpreter and capture output.

        Args:
            file_path (str): Path to the Python file to execute

        Returns:
            str: Output from executing the Python file
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{file_path}' does not exist")

        if not os.path.isfile(file_path):
            raise IsADirectoryError(f"'{file_path}' is a directory, not a file")

        if not file_path.endswith('.py'):
            raise ValueError(f"File '{file_path}' is not a Python file (.py extension required)")

        try:
            result = subprocess.run(
                [sys.executable, file_path],
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )

            output = ""
            if result.stdout:
                output += f"STDOUT:\n{result.stdout}"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}"

            if result.returncode != 0:
                output += f"\nProcess exited with code: {result.returncode}"

            return output.strip()

        except subprocess.TimeoutExpired:
            return "Execution timed out after 30 seconds"
        except Exception as e:
            return f"Error executing file: {str(e)}"

    def chat_with_deepseek(self, message: str) -> str:
        """
        Send a message to Deepseek AI and get a response.

        Args:
            message (str): The user message to send

        Returns:
            str: The AI response or error message
        """
        if not self.deepseek_client:
            return "Deepseek API client is not initialized. Please set DEEPSEEK_API_KEY environment variable."

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message}
        ]
        return self.deepseek_client.chat(messages)




def main():
    """Main function to run the Lobengula chatbot."""
    agent = AIAgent()

    print("Welcome to Lobengula - File System Assistant!")
    print("You can use commands like:")
    print("- 'scan <directory>' to list files")
    print("- 'read <file>' to read file contents")
    print("- 'write <file> <content>' to write to a file")
    print("- 'execute <python_file>' to run Python code")
    print("- 'deepseek <message>' to chat with Deepseek AI")
    print("- Type 'quit' to exit")
    print()

    while True:
        try:
            user_input = input("You: ").strip()

            if user_input.lower() == 'quit':
                print("Goodbye!")
                break

            # Handle commands without arguments
            if user_input == 'scan':
                print("Usage: scan <directory>")
            elif user_input == 'read':
                print("Usage: read <file>")
            elif user_input == 'write':
                print("Usage: write <file> <content>")
            elif user_input == 'execute':
                print("Usage: execute <python_file>")
            elif user_input == 'deepseek':
                print("Usage: deepseek <message>")
            # Handle special commands
            if user_input.startswith('scan '):
                directory = user_input[5:].strip()
                try:
                    files = agent.scan_directory(directory)
                    print(f"Files in {directory}: {len(files)}")
                    for file in files[:10]:  # Show first 10 files
                        print(f"  - {file}")
                    if len(files) > 10:
                        print(f"  ... and {len(files) - 10} more")
                except Exception as e:
                    print(f"Error: {e}")

            elif user_input.startswith('read '):
                file_path = user_input[5:].strip()
                try:
                    content = agent.read_file(file_path)
                    print(f"Content of {file_path}:")
                    print(content[:500])  # Show first 500 characters
                    if len(content) > 500:
                        print("... (truncated)")
                except Exception as e:
                    print(f"Error: {e}")

            elif user_input.startswith('write '):
                parts = user_input[6:].split(' ', 1)
                if len(parts) == 2:
                    file_path, content = parts
                    try:
                        agent.overwrite_file(file_path.strip(), content.strip())
                        print(f"Successfully wrote to {file_path}")
                    except Exception as e:
                        print(f"Error: {e}")
                else:
                    print("Usage: write <file> <content>")

            elif user_input.startswith('execute '):
                file_path = user_input[8:].strip()
                try:
                    output = agent.execute_python_file(file_path)
                    print(f"Output from {file_path}:")
                    print(output)
                except Exception as e:
                    print(f"Error: {e}")

            elif user_input.startswith('deepseek '):
                message = user_input[9:].strip()
                try:
                    response = agent.chat_with_deepseek(message)
                    print(f"Deepseek AI: {response}")
                except Exception as e:
                    print(f"Error: {e}")

            else:
                print("Unknown command. Available commands: scan, read, write, execute, deepseek, quit")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()

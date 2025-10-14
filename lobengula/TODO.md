# Deepseek API Integration TODO

## Completed Tasks
- [x] Create `lobengula/deepseek_api.py` with `DeepseekAPI` class for handling API calls
- [x] Add import for `DeepseekAPI` in `lobengula/main.py`
- [x] Add loading of `DEEPSEEK_API_KEY` from environment variables in `lobengula/main.py`
- [x] Initialize Deepseek API client in `lobengula/main.py` if API key is available
- [x] Add `deepseek <message>` command in the main loop for chatting with Deepseek AI
- [x] Update help text to include the new deepseek command

## Usage Instructions
1. Set your Deepseek API key in the environment variable `DEEPSEEK_API_KEY` (e.g., in `.env` file)
2. Run `python main.py` from the lobengula directory
3. Use the command `deepseek <your message>` to chat with Deepseek AI
4. Alternatively, you can run `python deepseek_api.py` directly for testing

## Notes
- Deepseek API uses OpenAI-compatible interface, so existing `openai` library is reused
- The API client is initialized with Deepseek's base URL: `https://api.deepseek.com`
- Default model used is `deepseek-chat`
- Error handling is included for API key missing or API call failures

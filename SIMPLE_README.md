# ChatGPT API - Simple Version

A barebones FastAPI application to send prompts to ChatGPT via OpenAI's API.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Key

Create a `.env` file in the root directory:
```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

Get your API key from: https://platform.openai.com/api-keys

### 3. Start the Server
```bash
python -m app.main
```

The server will start at: http://localhost:8000

## API Endpoints

### Interactive Documentation (SwaggerUI)
Visit: http://localhost:8000/docs

### POST /api/prompt

Send a prompt to ChatGPT and get a response.

**Request:**
```json
{
  "prompt": "What is Python?",
  "model": "gpt-3.5-turbo",
  "max_tokens": 1000
}
```

Note: `model` and `max_tokens` are optional parameters. If not specified, defaults to `gpt-3.5-turbo` and `1000` respectively.

**Response:**
```json
{
  "response": "Python is a high-level programming language...",
  "model": "gpt-3.5-turbo",
  "tokens_used": 150
}
```

**Example with curl:**
```bash
curl -X POST http://localhost:8000/api/prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Tell me a joke"}'
```

**Example with curl using GPT-4:**
```bash
curl -X POST http://localhost:8000/api/prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain quantum computing", "model": "gpt-4"}'
```

### GET /api/health

Check API health and configuration status.

**Response:**
```json
{
  "status": "healthy",
  "openai_api_key": "configured"
}
```

### GET /

Root endpoint with API information.

## Available Models

- `gpt-3.5-turbo` (default) - Fast and affordable
- `gpt-4` - More capable, higher cost
- `gpt-4-turbo` - Latest model

## Testing in SwaggerUI

1. Go to http://localhost:8000/docs
2. Click on "POST /api/prompt"
3. Click "Try it out"
4. Enter your prompt in the request body
5. Click "Execute"
6. See the response below

## Error Handling

If the API key is not configured:
```json
{
  "detail": "OpenAI API key not configured. Please set OPENAI_API_KEY in .env file"
}
```

If there's an OpenAI API error:
```json
{
  "detail": "OpenAI API error: [error message]"
}
```

## What Was Removed

This is a simplified version. The following features were removed to focus on core functionality:

- ❌ Difficulty estimation
- ❌ Automatic model routing
- ❌ Budget tracking
- ❌ Database operations
- ❌ Statistics tracking
- ❌ Escalation logic
- ❌ Complex retry logic

## What Remains

- ✅ Simple API to send prompts to ChatGPT
- ✅ Support for multiple OpenAI models
- ✅ SwaggerUI for easy testing
- ✅ Basic error handling
- ✅ Token usage tracking

## Troubleshooting

**Server won't start:**
- Make sure dependencies are installed: `pip install -r requirements.txt`
- Check that port 8000 is not in use

**API key errors:**
- Verify your API key is correct in `.env`
- Make sure the key starts with `sk-`
- Check your OpenAI account has credits

**OpenAI API errors:**
- Check your internet connection
- Verify your OpenAI account status
- Check OpenAI's status page: https://status.openai.com/

## Next Steps

To add back features:
- Check the git history for the full-featured version
- See the other services in `app/services/` for examples
- Database models are in `app/models/database.py`

## License

MIT License - see LICENSE file for details

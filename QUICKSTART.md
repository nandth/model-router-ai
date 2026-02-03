# Quick Start Guide

Get the Model Router AI service up and running in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- pip package manager
- OpenAI API key (get from https://platform.openai.com/api-keys)

## Installation

### 1. Clone and Install
```bash
git clone https://github.com/nandth/model-router-ai.git
cd model-router-ai
pip install -r requirements.txt
```

### 2. Configure OpenAI API Key
```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```bash
OPENAI_API_KEY=sk-your-actual-key-here
MONTHLY_BUDGET_LIMIT=100.0
```

**Don't have an API key?** You can still run the demo to see the routing logic in action!

## Running the Demo

See the routing system in action (no API key required):

```bash
python demo.py
```

This demonstrates:
- ✅ Difficulty estimation (easy/medium/hard)
- ✅ Model selection (GPT-3.5 / GPT-4 / GPT-4 Turbo)
- ✅ Cost estimation
- ✅ Escalation logic

## Starting the API Server

```bash
python -m app.main
```

The API server will start at `http://localhost:8000`

**Interactive Documentation:**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Testing the API

### 1. Health Check
```bash
curl http://localhost:8000/api/health
```
**Response:** `{"status":"healthy"}`

### 2. Check Budget Status
```bash
curl http://localhost:8000/api/budget
```
Shows: monthly limit, spent, remaining, request count

### 3. View Statistics
```bash
curl http://localhost:8000/api/stats
```
Shows: total requests, costs, latency, success rates

### 4. Route a Prompt (requires OpenAI API key)
```bash
curl -X POST http://localhost:8000/api/prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is Python?", "max_tokens": 100}'
```

**Response includes:**
- Selected model (gpt-3.5-turbo, gpt-4, or gpt-4-turbo)
- Difficulty score and level
- Token usage and cost
- Latency in milliseconds
- Whether escalation occurred

## Running Tests

```bash
pytest tests/ -v
```

All tests should pass, demonstrating the routing logic works correctly.

## What's Next?

1. **Explore the API**: Use the Swagger UI at http://localhost:8000/docs to interactively test all endpoints
2. **Adjust Budget**: Set your monthly budget limit in `.env`
3. **Understand the Code**: 
   - `app/services/difficulty_estimator.py` - How difficulty is calculated
   - `app/services/routing_policy.py` - How models are selected
   - `app/services/llm_client.py` - How OpenAI is called with retry logic
4. **Customize**: Adjust difficulty thresholds, modify routing logic, or add new features

## How It Works

```
┌─────────────────┐
│  Your Prompt    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  Difficulty Estimator   │  Analyzes: length, keywords, structure
│  Score: 0.0 - 1.0       │  Level: easy / medium / hard
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│   Routing Policy        │  Selects model:
│   - Easy → GPT-3.5      │  • gpt-3.5-turbo (cheap)
│   - Medium → GPT-4      │  • gpt-4 (balanced)
│   - Hard → GPT-4 Turbo  │  • gpt-4-turbo (powerful)
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│    OpenAI Client        │  Features:
│    - API call           │  • Auto-retry (up to 3x)
│    - Retry on failure   │  • Exponential backoff
│    - Check confidence   │  • Smart escalation
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Response + Metadata    │  Returns:
│  - Model used           │  • Generated text
│  - Tokens & cost        │  • Performance metrics
│  - Latency              │  • Cost tracking
└─────────────────────────┘
```

## Common Issues

**Issue**: `ModuleNotFoundError: No module named 'anthropic'`
- **Solution**: Update dependencies: `pip install -r requirements.txt`

**Issue**: "OpenAI API key not configured"
- **Solution**: Add `OPENAI_API_KEY` to `.env` file with a valid key from https://platform.openai.com/api-keys

**Issue**: "Monthly budget limit exceeded"
- **Solution**: Increase `MONTHLY_BUDGET_LIMIT` in `.env` or wait for next month

**Issue**: "Failed after 3 retries"
- **Solution**: Check your OpenAI API key is valid, check network connection, and verify OpenAI API status

## Pro Tips

- **Test without API keys first**: Run `python demo.py` to understand the routing logic
- **Monitor costs**: Use `GET /api/budget` to track spending in real-time
- **Start small**: Set a low budget limit initially while testing
- **Use interactive docs**: The Swagger UI at `/docs` makes testing easy
- **Check logs**: The SQLite database stores all request history for analysis

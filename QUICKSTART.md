# Quick Start Guide

Get the Model Router AI service up and running in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- pip package manager
- (Optional) OpenAI API key
- (Optional) Anthropic API key

**Note**: The service can run without API keys for testing the routing logic, but actual LLM calls require valid API keys.

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/nandth/model-router-ai.git
   cd model-router-ai
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment** (optional for testing)
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your API keys:
   ```bash
   OPENAI_API_KEY=sk-your-openai-key-here
   ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
   MONTHLY_BUDGET_LIMIT=100.0
   ```

## Running the Demo

See the routing system in action without API keys:

```bash
python demo.py
```

This demonstrates:
- ✅ Difficulty estimation (easy/medium/hard)
- ✅ Model selection (cheap/mid/high tier)
- ✅ Cost estimation
- ✅ Escalation logic

## Starting the Server

```bash
python -m app.main
```

The API server will start at `http://localhost:8000`

## Testing the API

### Health Check
```bash
curl http://localhost:8000/api/health
# Response: {"status":"healthy"}
```

### Check Budget
```bash
curl http://localhost:8000/api/budget
# Shows: monthly limit, spent, remaining, request count
```

### View Statistics
```bash
curl http://localhost:8000/api/stats
# Shows: requests, costs, latency, success rates
```

### Route a Prompt (requires API keys)
```bash
curl -X POST http://localhost:8000/api/prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is Python?", "max_tokens": 100}'
```

## Running Tests

```bash
pytest tests/ -v
```

All tests should pass (15/15).

## Interactive API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide interactive documentation where you can test all endpoints directly in your browser.

## What's Next?

1. **Add API Keys**: Configure `.env` with your OpenAI/Anthropic keys to make real LLM calls
2. **Adjust Budget**: Set your monthly budget limit in `.env`
3. **Explore the Code**: 
   - `app/services/difficulty_estimator.py` - How difficulty is calculated
   - `app/services/routing_policy.py` - How models are selected
   - `app/services/llm_client.py` - How LLMs are called with retry logic
4. **Customize**: Add new models, adjust difficulty thresholds, modify routing logic

## Architecture Overview

```
┌─────────────────┐
│  API Request    │
│  (POST /prompt) │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  Difficulty Estimator   │
│  - Analyze length       │
│  - Check keywords       │
│  - Assess structure     │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│   Routing Policy        │
│   - Select model tier   │
│   - Check budget        │
│   - Estimate cost       │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│    LLM Client           │
│    - Call API           │
│    - Retry on failure   │
│    - Detect low conf.   │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Escalation Logic       │
│  (if needed)            │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Database Logger        │
│  - Track cost           │
│  - Record latency       │
│  - Update budget        │
└─────────────────────────┘
```

## Support

For more detailed information, see:
- **README.md** - Complete documentation
- **USAGE.md** - Detailed usage examples
- **demo.py** - Working demonstration

## Common Issues

**Issue**: "OpenAI API key not configured"
- **Solution**: Add `OPENAI_API_KEY` to `.env` file

**Issue**: "Monthly budget limit exceeded"
- **Solution**: Increase `MONTHLY_BUDGET_LIMIT` in `.env` or wait for next month

**Issue**: "Failed after 3 retries"
- **Solution**: Check API key validity, network connection, and API status

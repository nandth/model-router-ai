# Model Router AI

A backend service that intelligently routes text prompts to different LLM APIs based on estimated difficulty and cost constraints.

## Features

- **Intelligent Difficulty Estimation**: Analyzes prompt length, keywords, and structure to estimate complexity
- **Smart Model Routing**: Routes requests to cheap, mid-tier, or high-capability models based on difficulty
- **Budget Management**: Tracks spending and enforces monthly budget limits
- **Retry Logic**: Automatically retries failed requests with exponential backoff
- **Smart Escalation**: Escalates to stronger models when confidence is low
- **Performance Tracking**: Logs latency, token usage, and costs per request
- **Database Persistence**: Stores all request metadata in SQLite

## Architecture

### Components

1. **Difficulty Estimator** (`app/services/difficulty_estimator.py`)
   - Analyzes prompt length (short/medium/long)
   - Identifies complex/simple keywords
   - Evaluates structural complexity (questions, lists, code blocks)
   - Returns difficulty score (0.0-1.0) and level (easy/medium/hard)

2. **Routing Policy** (`app/services/routing_policy.py`)
   - Defines model tiers: cheap (GPT-3.5), mid (GPT-4/Claude-2), high (GPT-4 Turbo/Claude-3)
   - Routes based on difficulty: easy→cheap, medium→mid, hard→high
   - Supports escalation to stronger models when needed

3. **LLM Client** (`app/services/llm_client.py`)
   - Interfaces with OpenAI and Anthropic APIs
   - Implements retry logic with exponential backoff (up to 3 attempts)
   - Detects low-confidence responses for escalation

4. **Budget Service** (`app/services/budget_service.py`)
   - Tracks monthly spending against configurable limits
   - Blocks requests when budget is exceeded
   - Provides real-time budget status

5. **Router Service** (`app/services/router_service.py`)
   - Orchestrates the entire routing flow
   - Logs all requests with metadata
   - Generates usage statistics

## Installation

1. Clone the repository:
```bash
git clone https://github.com/nandth/model-router-ai.git
cd model-router-ai
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys and settings
```

4. Run the server:
```bash
python -m app.main
# Or with uvicorn:
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### POST /api/prompt
Route a prompt to the appropriate LLM model.

**Request:**
```json
{
  "prompt": "Explain quantum computing in simple terms",
  "max_tokens": 1000
}
```

**Response:**
```json
{
  "success": true,
  "response": "Quantum computing is...",
  "model_used": "gpt-3.5-turbo",
  "difficulty_score": 0.35,
  "difficulty_level": "medium",
  "tokens_used": 150,
  "cost": 0.00023,
  "latency_ms": 1250.5,
  "escalated": false,
  "retry_count": 0
}
```

### GET /api/budget
Check current monthly budget status.

**Response:**
```json
{
  "year": 2024,
  "month": 1,
  "monthly_limit": 100.0,
  "total_spent": 12.45,
  "remaining": 87.55,
  "percentage_used": 12.45,
  "request_count": 250
}
```

### GET /api/stats
Get usage statistics.

**Response:**
```json
{
  "total_requests": 250,
  "successful_requests": 245,
  "failed_requests": 5,
  "success_rate": 98.0,
  "total_cost": 12.45,
  "avg_latency_ms": 1150.2,
  "total_tokens": 125000,
  "escalation_rate": 8.5
}
```

### GET /api/health
Health check endpoint.

## Configuration

Edit `.env` to configure:

- `OPENAI_API_KEY`: Your OpenAI API key
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `MONTHLY_BUDGET_LIMIT`: Maximum monthly spending in USD (default: 100.0)
- `DATABASE_URL`: Database connection string (default: sqlite:///./model_router.db)

## Model Tiers

### Cheap (Easy Tasks)
- **gpt-3.5-turbo**: $0.0005/1K input, $0.0015/1K output
- Use for: Simple questions, basic summarization, straightforward tasks

### Mid (Medium Tasks)
- **gpt-4**: $0.03/1K input, $0.06/1K output
- **claude-2**: $0.008/1K input, $0.024/1K output
- Use for: Analysis, comparisons, moderate complexity

### High (Hard Tasks)
- **gpt-4-turbo**: $0.01/1K input, $0.03/1K output
- **claude-3-opus**: $0.015/1K input, $0.075/1K output
- Use for: Complex reasoning, technical implementation, detailed analysis

## Difficulty Estimation

The system estimates difficulty using three weighted factors:

1. **Length (40%)**: Longer prompts generally indicate more complex tasks
2. **Keywords (40%)**: Presence of complex/simple keywords
3. **Structure (20%)**: Multiple questions, lists, code blocks

## Retry & Escalation Logic

1. **Retry**: Failed requests are automatically retried up to 3 times with exponential backoff
2. **Escalation**: If the initial response shows low confidence (short response, uncertainty phrases), the system automatically escalates to a stronger model

## Database Schema

### request_logs
- Tracks all requests with timestamps, models, costs, latency
- Stores prompt, response, difficulty scores
- Records success/failure, retry count, escalation status

### monthly_budgets
- Tracks spending per month
- Enforces budget limits
- Counts requests per month

## Development

Run tests:
```bash
pytest tests/
```

Run with auto-reload:
```bash
uvicorn app.main:app --reload
```

## License

MIT License - see LICENSE file for details
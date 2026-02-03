# Model Router AI

A backend service that intelligently routes text prompts to different OpenAI models based on estimated difficulty and cost constraints.

## Features

- **Intelligent Difficulty Estimation**: Analyzes prompt length, keywords, and structure to estimate complexity
- **Smart Model Routing**: Routes requests to GPT-3.5, GPT-4, or GPT-4 Turbo based on difficulty
- **Budget Management**: Tracks spending and enforces monthly budget limits
- **Retry Logic**: Automatically retries failed requests with exponential backoff
- **Smart Escalation**: Escalates to stronger models when confidence is low
- **Performance Tracking**: Logs latency, token usage, and costs per request
- **Database Persistence**: Stores all request metadata in SQLite

## Quick Start

1. **Clone and install:**
   ```bash
   git clone https://github.com/nandth/model-router-ai.git
   cd model-router-ai
   pip install -r requirements.txt
   ```

2. **Configure your API key:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. **Run the demo (no API key needed):**
   ```bash
   python demo.py
   ```

4. **Start the API server:**
   ```bash
   python -m app.main
   # API available at http://localhost:8000
   ```

## Architecture

### Components

1. **Difficulty Estimator** (`app/services/difficulty_estimator.py`)
   - Analyzes prompt length (short/medium/long)
   - Identifies complex/simple keywords
   - Evaluates structural complexity (questions, lists, code blocks)
   - Returns difficulty score (0.0-1.0) and level (easy/medium/hard)

2. **Routing Policy** (`app/services/routing_policy.py`)
   - Defines model tiers: cheap (GPT-3.5), mid (GPT-4), high (GPT-4 Turbo)
   - Routes based on difficulty: easy→cheap, medium→mid, hard→high
   - Supports escalation to stronger models when needed

3. **LLM Client** (`app/services/llm_client.py`)
   - Interfaces with OpenAI API
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

3. Set up your OpenAI API key:
```bash
cp .env.example .env
```
Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=your_key_here
MONTHLY_BUDGET_LIMIT=100.0
```

4. Run the server:
```bash
python -m app.main
```

The API will be available at `http://localhost:8000`

**Interactive Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

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

- `OPENAI_API_KEY`: Your OpenAI API key (get from https://platform.openai.com/api-keys)
- `MONTHLY_BUDGET_LIMIT`: Maximum monthly spending in USD (default: 100.0)
- `DATABASE_URL`: Database connection string (default: sqlite:///./model_router.db)

## OpenAI Model Tiers

### Cheap (Easy Tasks)
- **gpt-3.5-turbo**: $0.0005/1K input, $0.0015/1K output
- Use for: Simple questions, basic summarization, straightforward tasks

### Mid (Medium Tasks)
- **gpt-4**: $0.03/1K input, $0.06/1K output
- Use for: Analysis, comparisons, moderate complexity

### High (Hard Tasks)
- **gpt-4-turbo**: $0.01/1K input, $0.03/1K output
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

## Things to Add

Here are some ideas for future enhancements to make this project even better:

### Core Functionality
- **Support for streaming responses**: Add SSE (Server-Sent Events) for real-time token streaming
- **Response caching**: Cache common queries to reduce API costs and latency
- **Prompt templates**: Pre-defined templates for common use cases (summarization, translation, etc.)
- **Multi-turn conversations**: Support for maintaining conversation context across multiple requests
- **Custom model selection**: Allow users to override automatic model selection for specific requests

### Intelligence & Performance
- **Advanced difficulty estimation**: Use embeddings or a lightweight classifier model for better accuracy
- **A/B testing framework**: Compare different models on same prompts to optimize routing decisions
- **Learning from feedback**: Track user satisfaction and adjust routing based on historical performance
- **Response quality scoring**: Implement automated quality assessment to improve escalation logic
- **Load balancing**: Distribute requests across multiple API keys to increase throughput

### Monitoring & Operations
- **Prometheus metrics**: Export metrics for monitoring with Grafana dashboards
- **Request/response logging**: Detailed logging with filtering and search capabilities
- **Alert system**: Email/Slack notifications for budget thresholds and failures
- **Cost optimization reports**: Weekly/monthly reports showing cost breakdowns and savings
- **Performance analytics dashboard**: Real-time dashboard showing latency, success rates, and model usage

### Integration & APIs
- **Webhook support**: POST results to external URLs for async workflows
- **Batch processing API**: Submit multiple prompts and process them efficiently
- **SDK/client libraries**: Python, JavaScript, and Go client libraries
- **CLI tool**: Command-line interface for quick testing and automation
- **Integration with LangChain/LlamaIndex**: Enable use as a router in popular LLM frameworks

### Security & Reliability
- **Rate limiting**: Per-user and global rate limits to prevent abuse
- **API key management**: Multi-user support with per-key quotas and permissions
- **Request validation**: Input sanitization and validation to prevent misuse
- **Fallback models**: Automatic fallback to alternative models if primary fails
- **Circuit breaker pattern**: Prevent cascading failures with smart request throttling

### Cost Management
- **Dynamic budgeting**: Different budgets per user, team, or project
- **Cost prediction**: Estimate costs before making requests
- **Budget alerts**: Proactive notifications before hitting limits
- **Usage quotas**: Token-based limits per user or time period
- **Cost optimization suggestions**: Recommendations for reducing costs based on usage patterns

### Testing & Quality
- **Integration tests**: Full end-to-end tests with mock API responses
- **Performance benchmarks**: Automated benchmarking of routing decisions
- **Synthetic data generation**: Generate test prompts across difficulty levels
- **Chaos engineering**: Test system resilience under various failure scenarios

### Documentation & Developer Experience
- **Video tutorials**: Walkthrough videos for common use cases
- **Architecture diagrams**: Visual documentation of system flow
- **API examples in multiple languages**: curl, Python, JavaScript, Go examples
- **Docker support**: Containerized deployment with docker-compose
- **Helm charts**: Kubernetes deployment templates

### Advanced Features
- **Multi-model ensembling**: Combine responses from multiple models for critical queries
- **Cost-quality tradeoffs**: Allow users to specify preference (fast/cheap vs. slow/accurate)
- **Custom difficulty scoring**: Let users define their own difficulty estimation logic
- **Plugin system**: Support for custom pre/post-processing plugins
- **Model fine-tuning integration**: Use historical data to fine-tune routing decisions

Pick the features that best align with your use case and start building! Each addition makes the router more powerful and useful.

## License

MIT License - see LICENSE file for details
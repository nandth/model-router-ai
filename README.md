# Model Router AI

An exploration of cost-aware LLM orchestration, multi-stage routing, and escalation strategies in a controlled environment.

## Executive Summary

- **Problem**: LLM API costs vary by orders of magnitude; most requests don't need the most capable (expensive) models
- **Solution**: Heuristic-based routing that analyzes prompt features (code presence, complexity, stakes) and routes to tiered providers
- **Key technique**: Two-stage execution with self-evaluation—initial responses include confidence scores; low-confidence responses trigger escalation
- **Stack**: FastAPI backend, React frontend, OpenAI models across three capability tiers
- **Scope**: Demonstration of orchestration patterns; not production-grade, but architecturally coherent
- **Value**: Shows understanding of cost-quality tradeoffs, failure handling, and system decomposition in LLM systems

## Features

### Backend (FastAPI + Python)
- **Prompt feature extraction**: Code presence, question complexity, technical stakes detection
- **Tiered model routing**: Routes to low-cost, mid-tier, or high-capability models based on heuristic scoring
- **Self-evaluation with escalation**: Models assess confidence; uncertain responses trigger re-execution at higher tier
- **Streaming support**: Server-Sent Events (SSE) for token-by-token delivery
- **Rate limiting**: Per-IP request throttling
- **Input sanitization**: Validates prompts while preserving code formatting
- **Request logging**: SQLite-based persistence of routing decisions and metadata
- **Hard triggers**: Keyword-based escalation for high-stakes domains (security, medical, legal)
- **Multiple endpoints**: Standard, streaming, raw text, and analysis-only modes

### Frontend (React + Vite)
- **React 19 UI**: Responsive interface with TailwindCSS styling
- **Real-time feedback**: Displays routing decisions and analysis results
- **Animated components**: GSAP and Motion for transitions

## Tech Stack

### Backend
- FastAPI (API framework)
- Uvicorn (ASGI server)
- Pydantic (data validation)
- SQLAlchemy (minimal ORM usage.. for logging) 
- OpenAI SDK
- Tenacity (retry logic with exponential backoff)

### Frontend
- React 19 + Vite
- TailwindCSS
- GSAP (animations)
- React Router

### Development
- Pytest (testing)
- ESLint (linting)

## Quick Start

### Backend Setup

```bash
git clone https://github.com/nandth/model-router-ai.git
cd model-router-ai
pip install -r requirements.txt

# Configure API key
echo "OPENAI_API_KEY=your_key_here" > .env

# Start server
python -m app.main
# API available at http://localhost:8080
```

### Frontend Setup

```bash
cd client
npm install
npm run dev
# Frontend available at http://localhost:5173
```

## Architecture

The system is intentionally decomposed to isolate routing policy from execution and infrastructure concerns.

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend                            │
│         • Prompt input and result display                   │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/SSE
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                          │
│  • POST /api/prompt          (standard request)             │
│  • POST /api/prompt/stream   (SSE streaming)                │
│  • POST /api/analyze         (analysis only)                │
│  • GET  /api/health          (health check)                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                 Routing Executor                             │
│  • Orchestrates multi-stage execution                       │
│  • Manages self-evaluation and escalation                   │
└────┬──────────────┬──────────────┬──────────────────────────┘
     │              │              │
     ▼              ▼              ▼
┌─────────┐  ┌─────────────┐  ┌──────────────┐
│  Model  │  │   Prompt    │  │ Rate Limiter │
│ Router  │  │  Features   │  │   & Input    │
│         │  │  Extractor  │  │ Sanitizer    │
└─────────┘  └─────────────┘  └──────────────┘
     │              │
     │              ▼
     │         ┌─────────────────────┐
     │         │  Request Logger     │
     │         │  (SQLite)           │
     │         └─────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│         OpenAI API                   │
│   • Low-cost tier                   │
│   • Mid-tier reasoning              │
│   • High-capability tier            │
└─────────────────────────────────────┘
```

### Components

**Model Router** (`app/services/model_router.py`)
- Extracts prompt features (code presence, complexity markers, domain-specific keywords)
- Computes heuristic score (0-100) based on weighted feature set
- Maps score to capability tier
- Applies hard triggers for high-stakes domains

**Routing Executor** (`app/services/routing_executor.py`)
- Two-stage execution: initial response with self-evaluation, optional escalation
- Parses confidence scores from model output
- Re-executes at higher tier if confidence below threshold

**Prompt Features** (`app/services/prompt_features.py`)
- Regex-based feature extraction
- Keyword matching for high-stakes detection
- Weighted scoring function

**Rate Limiter, Input Sanitizer, Request Logger**
- Standard API protection layers
- SQLite persistence for request metadata

## Routing Pipeline

### Tier Definitions

**Low-cost tier** (Score: 0-40)
- Use case: Simple questions, general information
- Self-evaluation: Enabled (escalates if uncertain)

**Mid-tier reasoning** (Score: 41-70)
- Use case: Complex analysis, multi-step reasoning
- Self-evaluation: Enabled (escalates if uncertain)

**High-capability tier** (Score: 71-100)
- Use case: Technical implementation, critical decisions
- Self-evaluation: Disabled (already highest tier)

### Execution Flow

1. **Feature extraction**: Analyze prompt for code blocks, complexity markers, high-stakes keywords
2. **Score calculation**: Weighted sum of features → 0-100 score
3. **Hard triggers**: Keywords (security, medical, legal) force escalation to high-capability tier
4. **Tier selection**: Map score to tier
5. **Stage A execution**: Send to selected model with self-evaluation prompt
6. **Confidence parsing**: Extract confidence score from response
7. **Stage B escalation** (conditional): If confidence < 0.7, re-execute at next tier
8. **Return**: Final response with routing metadata

### Hard Triggers

The system escalates to high-capability tier when detecting:
- Security terms (SQL injection, XSS, authentication)
- Medical/health queries
- Legal or compliance questions
- Financial analysis
- Production deployment concerns

## API Endpoints

### POST /api/prompt

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
  "model_used": "low-cost-tier",
  "tokens_used": 150,
  "tier": "low-cost",
  "latency_ms": 1250.5,
  "routing": {
    "initial_tier": "low-cost",
    "final_tier": "low-cost",
    "score": 35,
    "hard_triggers": [],
    "escalated": false,
    "stage_a_confidence": 0.92,
    "stage_a_escalate": false
  }
}
```

### POST /api/prompt/stream

Streams tokens via Server-Sent Events (SSE). Events: `meta`, `delta`, `usage`, `done`, `error`.

```bash
curl -N -X POST http://localhost:8080/api/prompt/stream \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is Python?", "max_tokens": 100}'
```

### POST /api/prompt/raw

Accepts raw text without JSON envelope.

```bash
curl -X POST http://localhost:8080/api/prompt/raw \
  -H "Content-Type: text/plain" \
  --data-binary @code_snippet.txt
```

### POST /api/analyze

Returns routing analysis without executing the prompt (useful for debugging).

```json
{
  "features": {
    "has_code": true,
    "has_complex_question": false,
    "has_security_stakes": false,
    "word_count": 25
  },
  "score": 45,
  "routing": {
    "initial_tier": "mid-tier",
    "would_use_self_eval": true
  }
}
```

## Design Tradeoffs & Limitations

### Self-Evaluation Reliability
- **Approach**: Models assess their own confidence via structured prompts
- **Limitation**: No ground truth validation; confidence scores are model-generated estimates, not calibrated probabilities
- **Risk**: Over-confident incorrect responses or under-confident correct responses can occur
- **Mitigation**: Hard triggers bypass self-evaluation for high-stakes domains

### Streaming vs Self-Evaluation
- **Tradeoff**: Streaming requires buffering the full response to extract confidence scores, negating real-time benefits
- **Decision**: Streaming endpoint disables self-evaluation to preserve token-by-token delivery
- **Implication**: Users choose between real-time feedback (streaming) or quality control (standard with escalation)

### Heuristic Scoring vs ML Classifiers
- **Why heuristics**: Regex + keyword matching is deterministic, debuggable, and requires no training data or model deployment
- **Limitation**: Brittle; misses nuanced complexity (e.g., "simple" questions requiring deep reasoning)
- **Alternative not pursued**: Embedding-based classifiers would require labeled data, ongoing retraining, and higher latency
- **Verdict**: Heuristics sufficient for demonstration; production system would likely need hybrid approach

### Hard Triggers
- **Limitation**: Keyword-based detection prone to false positives (e.g., "security" in benign context) and false negatives (adversarial phrasing)
- **Risk**: Over-escalation increases costs; under-escalation risks low-quality responses on critical prompts

### Cost Optimization
- **Assumption**: Tier pricing differences justify routing overhead
- **Not measured**: Actual cost savings require production traffic analysis
- **Blind spot**: Escalation from low-cost to high-capability may cost more than starting at mid-tier

### Scope
- **Not production-ready**: No authentication, no multi-tenancy, no cost budgeting, no fallback providers
- **Intended use**: Demonstration of orchestration patterns, not a deployable service

## Configuration

Environment variables (`.env` file):
```bash
OPENAI_API_KEY=your_key_here
DATABASE_URL=sqlite:///./model_router.db  # Optional
RATE_LIMIT_PROMPT_MAX_REQUESTS=30          # Optional
```

Rate limiting: Per-IP, configurable per endpoint (default: 30/min standard, 10/min streaming).

Input constraints: 50k character max prompt length (configurable).

## Project Structure

```
model-router-ai/
├── app/
│   ├── models/database.py          # SQLAlchemy models
│   ├── routers/
│   │   ├── api.py                  # API endpoints
│   │   └── schemas.py              # Pydantic models
│   ├── services/
│   │   ├── model_router.py         # Routing logic
│   │   ├── routing_executor.py     # Multi-stage execution
│   │   ├── prompt_features.py      # Feature extraction
│   │   ├── rate_limiter.py         # Rate limiting
│   │   ├── input_sanitizer.py      # Input validation
│   │   └── request_logger.py       # Request logging
│   └── main.py
├── client/                          # React frontend
├── server/
│   ├── demo.py                      # Demo script (no API key needed)
│   └── tests/                       # Pytest tests
└── requirements.txt
```

## Testing

Backend:
```bash
pytest server/tests/ -v
python server/demo.py  # Run demo
```

API:
```bash
curl http://localhost:8080/api/health
curl -X POST http://localhost:8080/api/prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is Python?"}'
```

Interactive docs: `http://localhost:8080/docs`

## What This Demonstrates

- **Cost-aware orchestration**: Tiered model selection based on prompt analysis
- **Failure handling**: Self-evaluation and automatic escalation
- **System decomposition**: Cleanly separated routing, execution, and infrastructure concerns
- **Tradeoff awareness**: Explicit documentation of limitations and design choices

## What This Is Not

- Not production-ready (no auth, no multi-tenancy, no cost budgeting, no provider fallbacks)
- Not a deployed service (demonstration code)
- Not claiming optimal routing (heuristics are brittle, cost savings unmeasured)

## License

MIT License - see LICENSE file for details

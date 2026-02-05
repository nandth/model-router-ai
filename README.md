# Model Router AI

A full-stack application with intelligent prompt routing that analyzes text prompts and routes them to the most appropriate OpenAI models based on complexity, cost optimization, and self-evaluation capabilities.

## Features

### Backend (FastAPI + Python)
- **Advanced Prompt Analysis**: Extracts features including code presence, question complexity, technical stakes
- **Smart Model Routing**: Automatically routes to GPT-3.5, GPT-4, or GPT-4 Turbo based on analysis
- **Self-Evaluation & Escalation**: Models evaluate their own confidence and escalate when uncertain
- **Streaming Support**: Server-Sent Events (SSE) for real-time token streaming
- **Rate Limiting**: Configurable per-IP rate limits to prevent abuse
- **Input Sanitization**: Validates and sanitizes prompts while preserving code formatting
- **Request Logging**: Comprehensive logging of all requests with metadata
- **Hard Triggers**: Automatic escalation for high-stakes prompts (security, medical, legal)
- **Multiple Endpoints**: Standard, streaming, raw text, and analysis-only endpoints

### Frontend (React + Vite)
- **Modern React 19 UI**: Beautiful, responsive interface with animations
- **Real-time Results**: Live feedback on prompt analysis and routing decisions
- **Interactive Design**: GSAP and Motion animations for smooth user experience
- **TailwindCSS Styling**: Modern, customizable design system
- **Glass Morphism Effects**: Custom visual components with gradient backgrounds

## Tech Stack

### Backend
- **FastAPI**: Modern, high-performance web framework for building APIs
- **Uvicorn**: Lightning-fast ASGI server
- **Pydantic**: Data validation using Python type hints
- **SQLAlchemy**: SQL toolkit and ORM for database operations
- **OpenAI SDK**: Official OpenAI Python client
- **Tenacity**: Robust retry library with exponential backoff
- **Python-dotenv**: Environment variable management

### Frontend
- **React 19**: Latest React with improved performance and features
- **Vite**: Next-generation frontend build tool
- **TailwindCSS 4**: Utility-first CSS framework
- **React Router**: Client-side routing
- **GSAP**: Professional-grade animation library
- **Motion**: Declarative animations for React
- **Lucide React**: Beautiful, consistent icon library
- **OGL**: Lightweight WebGL library for visual effects

### Development Tools
- **Pytest**: Testing framework
- **ESLint**: JavaScript/TypeScript linting
- **TypeScript**: Type-safe frontend development

## Quick Start

### Backend Setup

1. **Clone and install:**
   ```bash
   git clone https://github.com/nandth/model-router-ai.git
   cd model-router-ai
   pip install -r requirements.txt
   ```

2. **Configure your API key:**
   ```bash
   # Create .env file with your OpenAI API key
   echo "OPENAI_API_KEY=your_key_here" > .env
   ```

3. **Run the demo (no API key needed):**
   ```bash
   python server/demo.py
   ```

4. **Start the API server:**
   ```bash
   python -m app.main
   # API available at http://localhost:8080
   ```

### Frontend Setup

1. **Install dependencies:**
   ```bash
   cd client
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   # Frontend available at http://localhost:5173
   ```

3. **Build for production:**
   ```bash
   npm run build
   npm run preview
   ```

## Architecture

### System Overview
```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend (Vite)                     │
│         • React 19 + TailwindCSS + GSAP animations          │
│         • Interactive prompt input and result display        │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/SSE
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                          │
│                    (app/main.py)                             │
│         • CORS enabled for frontend integration             │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   API Router Layer                           │
│                (app/routers/api.py)                          │
│  • POST /api/prompt          (standard request)             │
│  • POST /api/prompt/stream   (SSE streaming)                │
│  • POST /api/prompt/raw      (raw text input)               │
│  • POST /api/analyze         (analysis only)                │
│  • GET  /api/health          (health check)                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                 Routing Executor                             │
│           (app/services/routing_executor.py)                 │
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
     │              │              │
     │              ▼              ▼
     │         ┌─────────────────────┐
     │         │  Request Logger     │
     │         │  • SQLite storage   │
     │         └─────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│         OpenAI API Client            │
│   • GPT-3.5 Turbo (cheap)           │
│   • GPT-4 (mid)                     │
│   • GPT-4 Turbo (best)              │
│   • Streaming support               │
└─────────────────────────────────────┘
```

### Components

1. **Model Router** (`app/services/model_router.py`)
   - Extracts prompt features (code, complexity, stakes)
   - Computes difficulty/risk score (0-100)
   - Routes to appropriate tier (cheap/mid/best)
   - Evaluates hard triggers for automatic escalation
   - Self-evaluation logic for confidence assessment

2. **Routing Executor** (`app/services/routing_executor.py`)
   - Executes multi-stage routing pipeline
   - Stage A: Initial model with self-evaluation
   - Stage B: Escalation to better model if needed
   - Handles both standard and streaming responses

3. **Prompt Features** (`app/services/prompt_features.py`)
   - Extracts features: code presence, complexity indicators
   - Identifies high-stakes keywords (security, medical, legal)
   - Analyzes question types and technical depth
   - Computes weighted difficulty score

4. **Rate Limiter** (`app/services/rate_limiter.py`)
   - In-memory sliding window rate limiting
   - Configurable per-endpoint limits
   - Per-IP tracking to prevent abuse
   - Returns 429 status when limits exceeded

5. **Input Sanitizer** (`app/services/input_sanitizer.py`)
   - Validates prompt length and content
   - Removes control characters while preserving code formatting
   - Normalizes line endings across platforms
   - Prevents empty or malformed prompts

6. **Request Logger** (`app/services/request_logger.py`)
   - SQLite database persistence
   - Tracks all requests with metadata
   - Stores routing decisions and performance metrics
   - Enables usage analytics and debugging

## Installation

### Prerequisites
- Python 3.8 or higher
- Node.js 18+ and npm
- OpenAI API key (get from https://platform.openai.com/api-keys)

### Backend Installation

1. Clone the repository:
```bash
git clone https://github.com/nandth/model-router-ai.git
cd model-router-ai
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Create .env file in the root directory
OPENAI_API_KEY=your_key_here
DATABASE_URL=sqlite:///./model_router.db

# Optional rate limiting configuration
RATE_LIMIT_PROMPT_MAX_REQUESTS=30
RATE_LIMIT_STREAM_MAX_REQUESTS=10
RATE_LIMIT_ANALYZE_MAX_REQUESTS=60
```

4. Run the backend server:
```bash
python -m app.main
```

The API will be available at `http://localhost:8080`

### Frontend Installation

1. Navigate to client directory:
```bash
cd client
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

4. Build for production:
```bash
npm run build
```

**Interactive API Documentation:**
- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

## API Endpoints

### POST /api/prompt
Route a prompt to the appropriate LLM model with intelligent selection.

**Request:**
```json
{
  "prompt": "Explain quantum computing in simple terms",
  "model": "gpt-3.5-turbo",
  "max_tokens": 1000,
  "route_mode": "auto"
}
```

**Response:**
```json
{
  "success": true,
  "response": "Quantum computing is...",
  "model_used": "gpt-3.5-turbo",
  "tokens_used": 150,
  "tier": "cheap",
  "latency_ms": 1250.5,
  "routing": {
    "initial_tier": "cheap",
    "final_tier": "cheap",
    "score": 35,
    "hard_triggers": [],
    "escalated": false,
    "stage_a_confidence": 0.92,
    "stage_a_escalate": false
  }
}
```

### POST /api/prompt/stream
Stream tokens in real-time using Server-Sent Events (SSE).

**Server-Sent Events:**
- `meta`: Routing and model information
- `delta`: Incremental text chunks
- `usage`: Token usage statistics
- `done`: Final metadata
- `error`: Error details if failed

**Example:**
```bash
curl -N -X POST http://localhost:8080/api/prompt/stream \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is Python?", "max_tokens": 100}'
```

### POST /api/prompt/raw
Send raw text without JSON formatting (useful for pasting code).

**Request:**
```bash
curl -X POST http://localhost:8080/api/prompt/raw \
  -H "Content-Type: text/plain" \
  --data-binary @code_snippet.txt
```

### POST /api/analyze
Analyze a prompt without executing it (for debugging routing logic).

**Response:**
```json
{
  "features": {
    "has_code": true,
    "has_complex_question": false,
    "has_security_stakes": false,
    "word_count": 25
  },
  "score": 45,
  "score_breakdown": {
    "base_score": 30,
    "code_bonus": 15
  },
  "hard_triggers": {
    "triggered": false,
    "reasons": []
  },
  "routing": {
    "initial_tier": "mid",
    "initial_model": "gpt-4",
    "would_use_self_eval": true
  }
}
```

### GET /api/health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "openai_api_key": "configured",
  "routing_enabled": true
}
```

## Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional - Database
DATABASE_URL=sqlite:///./model_router.db

# Optional - Rate Limiting (requests per minute)
RATE_LIMIT_PROMPT_MAX_REQUESTS=30      # Standard prompt endpoint
RATE_LIMIT_STREAM_MAX_REQUESTS=10      # Streaming endpoint
RATE_LIMIT_ANALYZE_MAX_REQUESTS=60     # Analysis endpoint

# Optional - Server Configuration
HOST=0.0.0.0
PORT=8080
```

### Rate Limiting

The application includes per-IP rate limiting to prevent abuse:

- **Standard Prompts**: 30 requests/minute (default)
- **Streaming**: 10 requests/minute (default)
- **Analysis**: 60 requests/minute (default)

Rate limits can be adjusted via environment variables or disabled by setting values to very high numbers.

### Input Constraints

- **Maximum prompt length**: 50,000 characters (configurable)
- **Maximum tokens per response**: 4,000 (configurable)
- **Supported content**: Plain text, code snippets, markdown

## Model Tiers and Routing

### Tier Definitions

#### Cheap Tier (Score: 0-40)
- **Model**: gpt-3.5-turbo
- **Cost**: $0.0005/1K input, $0.0015/1K output
- **Use for**: Simple questions, basic information, straightforward tasks
- **Self-evaluation**: Enabled (can escalate if uncertain)

#### Mid Tier (Score: 41-70)
- **Model**: gpt-4
- **Cost**: $0.03/1K input, $0.06/1K output
- **Use for**: Complex analysis, comparisons, multi-step reasoning
- **Self-evaluation**: Enabled (can escalate if uncertain)

#### Best Tier (Score: 71-100)
- **Model**: gpt-4-turbo
- **Cost**: $0.01/1K input, $0.03/1K output
- **Use for**: Expert-level tasks, technical implementation, critical decisions
- **Self-evaluation**: Disabled (already best model)

### Routing Logic

1. **Feature Extraction**: Analyze prompt for code, complexity, stakes
2. **Score Calculation**: Compute weighted score (0-100)
3. **Hard Triggers**: Check for high-stakes keywords (security, medical, legal)
4. **Tier Selection**: Choose model based on score and triggers
5. **Execution**: Send to selected model with self-evaluation
6. **Escalation**: If confidence low, retry with better model

### Hard Triggers (Automatic Escalation to Best)

The system automatically escalates to the best model when detecting:
- Security-related prompts (SQL injection, XSS, authentication)
- Medical/health-related queries
- Legal advice or compliance questions
- Financial analysis or risk assessment
- Production deployment or infrastructure
- Data privacy concerns

## Self-Evaluation and Escalation

The system uses a two-stage approach for optimal cost/quality balance:

### Stage A: Initial Response with Self-Evaluation
1. Route prompt to initial model (cheap or mid tier)
2. Request includes self-evaluation instructions
3. Model evaluates its own confidence (0.0-1.0)
4. Model recommends escalation if uncertain

### Stage B: Escalation (if needed)
1. Parse self-evaluation from Stage A response
2. If confidence < threshold or escalation recommended
3. Re-run prompt with next higher tier model
4. Return Stage B response to user

### Benefits
- **Cost Optimization**: Only use expensive models when needed
- **Quality Assurance**: Detect and fix low-confidence responses
- **Transparency**: Routing metadata shows escalation decisions
- **No User Intervention**: Fully automatic quality control

### Streaming Mode
Note: Streaming responses bypass self-evaluation since they require buffering the full response. Use standard endpoints for self-evaluation features.

## Project Structure

```
model-router-ai/
├── app/                          # Backend FastAPI application
│   ├── models/                   # Database models
│   │   └── database.py          # SQLAlchemy models & setup
│   ├── routers/                 # API routes
│   │   ├── api.py              # Main API endpoints
│   │   └── schemas.py          # Pydantic request/response models
│   ├── services/                # Business logic
│   │   ├── model_router.py     # Core routing logic
│   │   ├── routing_executor.py # Multi-stage execution
│   │   ├── prompt_features.py  # Feature extraction
│   │   ├── rate_limiter.py     # Rate limiting
│   │   ├── input_sanitizer.py  # Input validation
│   │   └── request_logger.py   # Request logging
│   └── main.py                  # FastAPI app initialization
├── client/                       # Frontend React application
│   ├── src/
│   │   ├── components/          # React components
│   │   │   ├── CircularText.jsx
│   │   │   ├── GlassSurface.jsx
│   │   │   ├── Grainient.jsx   # Gradient background
│   │   │   └── TextType.jsx
│   │   ├── pages/               # Page components
│   │   │   ├── Homepage.jsx    # Landing page
│   │   │   ├── LoadingScreen.jsx
│   │   │   └── Resultpage.jsx  # Results display
│   │   ├── routes/              # Routing configuration
│   │   ├── App.jsx              # Main app component
│   │   └── main.jsx             # Entry point
│   ├── package.json             # Frontend dependencies
│   ├── vite.config.js           # Vite configuration
│   └── vercel.json              # Vercel deployment config
├── server/                       # Server utilities
│   ├── demo.py                  # Demo script
│   ├── test_api.sh             # API testing script
│   └── tests/                   # Backend tests
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── QUICKSTART.md               # Quick start guide
├── USAGE.md                    # Usage examples
└── IMPLEMENTATION_SUMMARY.md   # Technical details
```

## Development

### Backend Development

Run tests:
```bash
pytest server/tests/ -v
```

Run with auto-reload:
```bash
uvicorn app.main:app --reload --port 8080
```

Run demo script:
```bash
python server/demo.py
```

### Frontend Development

Start development server with hot reload:
```bash
cd client
npm run dev
```

Lint code:
```bash
npm run lint
```

Build for production:
```bash
npm run build
npm run preview
```

### Testing the API

Manual testing with curl:
```bash
# Health check
curl http://localhost:8080/api/health

# Send a prompt
curl -X POST http://localhost:8080/api/prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is Python?", "max_tokens": 100}'

# Analyze without executing
curl -X POST http://localhost:8080/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write a secure authentication function"}'
```

Or use the provided test script:
```bash
bash server/test_api.sh
```

## Deployment

### Frontend (Vercel)
The frontend is configured for Vercel deployment with the included `vercel.json`:

```bash
cd client
npm run build
# Deploy to Vercel
vercel --prod
```

### Backend (Any Platform)
The backend can be deployed to any platform supporting Python (Railway, Render, Fly.io, etc.):

```bash
# Ensure dependencies are installed
pip install -r requirements.txt

# Run with production server
python -m app.main
```

Environment variables needed:
- `OPENAI_API_KEY`: Your OpenAI API key
- `DATABASE_URL`: Database connection string (optional, defaults to SQLite)

## Key Features Implemented

### ✅ Intelligent Routing
- Feature-based prompt analysis
- Multi-tier model selection (cheap/mid/best)
- Hard trigger detection for critical prompts
- Weighted scoring system (0-100)

### ✅ Self-Evaluation System
- Models assess their own confidence
- Automatic escalation when uncertain
- Two-stage execution pipeline
- Cost-optimized quality control

### ✅ Streaming Support
- Real-time token streaming via SSE
- Progressive response display
- Usage statistics during streaming
- Error handling in streams

### ✅ Security & Validation
- Input sanitization
- Rate limiting per IP
- Control character filtering
- Prompt length validation

### ✅ Developer Experience
- Comprehensive API documentation
- Multiple request formats (JSON, raw text)
- Analysis endpoint for debugging
- Interactive Swagger UI
- Health check endpoint

### ✅ Modern Frontend
- React 19 with animations
- Real-time result display
- Beautiful glass morphism design
- Responsive layout

## Future Enhancements

Here are some ideas for future development:

### Core Functionality
- **Response caching**: Cache common queries to reduce API costs and latency
- **Multi-turn conversations**: Support for maintaining conversation context across multiple requests
- **Custom difficulty scoring**: Allow users to define their own difficulty estimation logic
- **Batch processing API**: Submit multiple prompts and process them efficiently

### Intelligence & Performance
- **ML-based difficulty estimation**: Use embeddings or a lightweight classifier model for better accuracy
- **A/B testing framework**: Compare different models on same prompts to optimize routing decisions
- **Learning from feedback**: Track user satisfaction and adjust routing based on historical performance
- **Advanced caching strategies**: Redis-based caching for distributed deployments

### Monitoring & Operations
- **Prometheus metrics**: Export metrics for monitoring with Grafana dashboards
- **Detailed logging**: Structured logging with filtering and search capabilities
- **Alert system**: Email/Slack notifications for budget thresholds and failures
- **Cost analytics dashboard**: Real-time dashboard showing latency, success rates, and model usage

### Integration & APIs
- **Webhook support**: POST results to external URLs for async workflows
- **SDK/client libraries**: Python, JavaScript, and Go client libraries
- **CLI tool**: Command-line interface for quick testing and automation
- **LangChain integration**: Enable use as a router in popular LLM frameworks

### Security & Reliability
- **Redis-based rate limiting**: Distributed rate limiting for multi-instance deployments
- **API key management**: Multi-user support with per-key quotas and permissions
- **Circuit breaker pattern**: Prevent cascading failures with smart request throttling
- **Fallback models**: Automatic fallback to alternative providers if primary fails

### Cost Management
- **Budget tracking**: Track spending against configurable limits
- **Dynamic budgeting**: Different budgets per user, team, or project
- **Cost prediction**: Estimate costs before making requests
- **Usage quotas**: Token-based limits per user or time period

### Testing & Quality
- **Integration tests**: Full end-to-end tests with mock API responses
- **Performance benchmarks**: Automated benchmarking of routing decisions
- **Load testing**: Test system performance under high load

### Deployment
- **Docker support**: Containerized deployment with docker-compose
- **Kubernetes charts**: Helm charts for K8s deployment
- **Multi-region support**: Deploy across multiple regions for lower latency

## License

MIT License - see LICENSE file for details
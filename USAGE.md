# Usage Examples

## Basic Usage

### 1. Start the Server

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start the server
python -m app.main
# Or with uvicorn:
uvicorn app.main:app --reload
```

Server will be available at `http://localhost:8000`

### 2. Route a Simple Prompt

```bash
curl -X POST http://localhost:8000/api/prompt \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is Python?",
    "max_tokens": 100
  }'
```

Response:
```json
{
  "success": true,
  "response": "Python is a high-level programming language...",
  "model_used": "gpt-3.5-turbo",
  "difficulty_score": 0.22,
  "difficulty_level": "easy",
  "tokens_used": 85,
  "cost": 0.0001,
  "latency_ms": 1250.5,
  "escalated": false,
  "retry_count": 0
}
```

### 3. Route a Complex Prompt

```bash
curl -X POST http://localhost:8000/api/prompt \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Provide a comprehensive technical analysis of distributed consensus algorithms. Design a detailed implementation with step-by-step reasoning and mathematical proof.",
    "max_tokens": 2000
  }'
```

Response:
```json
{
  "success": true,
  "response": "Distributed consensus algorithms...",
  "model_used": "gpt-4-turbo",
  "difficulty_score": 0.75,
  "difficulty_level": "hard",
  "tokens_used": 1850,
  "cost": 0.0425,
  "latency_ms": 3200.0,
  "escalated": false,
  "retry_count": 0
}
```

### 4. Check Budget Status

```bash
curl http://localhost:8000/api/budget
```

Response:
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

### 5. View Statistics

```bash
curl http://localhost:8000/api/stats
```

Response:
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

## Python Client Example

```python
import requests

class ModelRouterClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def route_prompt(self, prompt, max_tokens=1000):
        """Route a prompt to the appropriate model."""
        response = requests.post(
            f"{self.base_url}/api/prompt",
            json={"prompt": prompt, "max_tokens": max_tokens}
        )
        return response.json()
    
    def get_budget(self):
        """Get current budget status."""
        response = requests.get(f"{self.base_url}/api/budget")
        return response.json()
    
    def get_stats(self):
        """Get usage statistics."""
        response = requests.get(f"{self.base_url}/api/stats")
        return response.json()

# Usage
client = ModelRouterClient()

# Simple question
result = client.route_prompt("What is machine learning?")
print(f"Model: {result['model_used']}")
print(f"Cost: ${result['cost']:.4f}")
print(f"Response: {result['response'][:100]}...")

# Complex analysis
result = client.route_prompt(
    "Analyze the trade-offs between microservices and monolithic architectures",
    max_tokens=1500
)
print(f"Model: {result['model_used']}")
print(f"Difficulty: {result['difficulty_level']}")

# Check budget
budget = client.get_budget()
print(f"Remaining budget: ${budget['remaining']:.2f}")
```

## Escalation Example

The system automatically escalates to stronger models when it detects low confidence:

```python
# Initial response from cheap model shows uncertainty
response1 = client.route_prompt("I'm not sure about this complex topic")
# System detects "I'm not sure" and escalates

# Second attempt with stronger model
# The escalated flag will be True
print(f"Escalated: {response1['escalated']}")  # True
```

## Budget Enforcement Example

When monthly budget is exceeded, requests are blocked:

```python
result = client.route_prompt("Test prompt")

if not result['success']:
    if 'budget' in result.get('error', ''):
        print("Budget exceeded!")
        budget = client.get_budget()
        print(f"Current spending: ${budget['total_spent']}")
        print(f"Monthly limit: ${budget['monthly_limit']}")
```

## Demo Script

Run the included demo script to see the system in action:

```bash
python demo.py
```

This will demonstrate:
- Difficulty estimation for various prompts
- Model selection based on difficulty
- Cost estimation
- Escalation paths
- Budget tracking features

## Testing

Run the test suite:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_difficulty_estimator.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## API Documentation

FastAPI provides automatic interactive API documentation:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

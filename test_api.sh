#!/bin/bash
set -e

echo "=========================================="
echo "ChatGPT API - Test Script"
echo "=========================================="
echo ""

# Check if server is running
if ! curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "❌ Error: Server is not running at http://localhost:8000"
    echo "Please start the server first:"
    echo "  python -m app.main"
    exit 1
fi

echo "✓ Server is running"
echo ""

# Test 1: Root endpoint
echo "1. Testing root endpoint..."
curl -s http://localhost:8000/ | python -m json.tool
echo ""

# Test 2: Health check
echo "2. Testing health check..."
curl -s http://localhost:8000/api/health | python -m json.tool
echo ""

# Test 3: Send prompt (will fail without API key)
echo "3. Testing prompt endpoint (without API key)..."
curl -s -X POST http://localhost:8000/api/prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Say hello!"}' | python -m json.tool
echo ""

# Test 4: OpenAPI schema
echo "4. Checking OpenAPI endpoints..."
curl -s http://localhost:8000/openapi.json | python -c "import sys, json; data=json.load(sys.stdin); print('Available endpoints:'); [print(f'  - {k}') for k in data['paths'].keys()]"
echo ""

echo "=========================================="
echo "✓ Tests complete!"
echo ""
echo "To use with a real API key:"
echo "1. Edit .env file"
echo "2. Add your OpenAI API key: OPENAI_API_KEY=sk-..."
echo "3. Restart the server"
echo "4. Try: curl -X POST http://localhost:8000/api/prompt -H 'Content-Type: application/json' -d '{\"prompt\": \"Hello!\"}'"
echo "=========================================="

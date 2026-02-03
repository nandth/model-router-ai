"""Demo script showing the router system functionality."""
from app.services.difficulty_estimator import DifficultyEstimator
from app.services.routing_policy import RoutingPolicy, ModelConfig

# Demo prompts of varying difficulty
prompts = [
    "What is Python?",
    "Compare and contrast Python and JavaScript for web development.",
    """Provide a comprehensive technical analysis of distributed consensus algorithms.
    Design a detailed implementation with step-by-step reasoning and mathematical proof.
    Explain the trade-offs between different approaches like Paxos, Raft, and Byzantine fault tolerance."""
]

print("=" * 80)
print("MODEL ROUTER AI - DEMO")
print("=" * 80)
print()

for i, prompt in enumerate(prompts, 1):
    print(f"\n{'='*80}")
    print(f"PROMPT {i}:")
    print(f"{'='*80}")
    print(f"{prompt[:100]}{'...' if len(prompt) > 100 else ''}")
    print()
    
    # Estimate difficulty
    score, level = DifficultyEstimator.estimate(prompt)
    print(f"Difficulty Score: {score:.3f}")
    print(f"Difficulty Level: {level.upper()}")
    
    # Select model
    selected_model = RoutingPolicy.select_model(score, level)
    config = ModelConfig.get_model_config(selected_model)
    
    print(f"\nSelected Model: {selected_model}")
    print(f"Model Tier: {config['tier'].value}")
    print(f"Provider: {config['provider']}")
    print(f"Description: {config['description']}")
    
    # Estimate cost (for 1000 input tokens, 500 output tokens)
    estimated_cost = ModelConfig.estimate_cost(selected_model, 1000, 500)
    print(f"Estimated Cost (1000 in / 500 out): ${estimated_cost:.4f}")
    
    # Show escalation path
    escalated_model = RoutingPolicy.select_model(
        score, level,
        previous_model=selected_model,
        escalate=True
    )
    if escalated_model != selected_model:
        escalated_config = ModelConfig.get_model_config(escalated_model)
        print(f"\nEscalation Option: {escalated_model} ({escalated_config['tier'].value})")

print("\n" + "=" * 80)
print("BUDGET TRACKING DEMO")
print("=" * 80)
print("\nThe system tracks:")
print("- Monthly spending vs. budget limit")
print("- Per-request latency and token usage")
print("- Success/failure rates")
print("- Escalation frequency")
print("\nAll data is persisted in SQLite database (model_router.db)")

print("\n" + "=" * 80)
print("RETRY & ESCALATION LOGIC")
print("=" * 80)
print("\n1. RETRY: Failed API calls automatically retry up to 3 times")
print("   - Exponential backoff: 2s, 4s, 8s delays")
print("   - Handles transient network/API errors")
print("\n2. ESCALATION: Low-confidence responses trigger escalation")
print("   - Detects uncertainty phrases ('I'm not sure', 'unclear', etc.)")
print("   - Very short responses (<50 chars)")
print("   - Automatically switches to stronger model tier")

print("\n" + "=" * 80)
print("API ENDPOINTS")
print("=" * 80)
print("\nPOST /api/prompt    - Route a prompt to appropriate model")
print("GET  /api/budget    - Check monthly budget status")
print("GET  /api/stats     - View usage statistics")
print("GET  /api/health    - Health check")

print("\n" + "=" * 80)

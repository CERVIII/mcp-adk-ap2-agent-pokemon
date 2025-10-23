#!/bin/bash
# Run Shopping Agent (requires other agents to be running)

set -e

echo "🛍️  Starting Pokemon Shopping Agent..."
echo ""

# Check if other agents are running
check_agent() {
    local url=$1
    local name=$2
    
    if curl -s -f "$url/.well-known/agent-card.json" > /dev/null 2>&1; then
        echo "✅ $name is running"
        return 0
    else
        echo "❌ $name is NOT running"
        return 1
    fi
}

echo "Checking prerequisite agents..."

if ! check_agent "http://localhost:8001" "Merchant Agent"; then
    echo ""
    echo "⚠️  Merchant Agent not running. Start it first with:"
    echo "   ./scripts/run-ap2-agents.sh"
    echo ""
    exit 1
fi

if ! check_agent "http://localhost:8002" "Credentials Provider"; then
    echo ""
    echo "⚠️  Credentials Provider not running."
    exit 1
fi

if ! check_agent "http://localhost:8003" "Payment Processor"; then
    echo ""
    echo "⚠️  Payment Processor not running."
    exit 1
fi

echo ""
echo "✅ All prerequisite agents are running!"
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""

# Start shopping agent
PYTHONPATH=src python -m ap2.agents.shopping

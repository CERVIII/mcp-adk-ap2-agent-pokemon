#!/bin/bash
# Run complete AP2 demo with all agents

set -e

echo "🚀 Starting AP2 Pokemon Demo..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Load environment
if [ -f ap2-integration/.env ]; then
    export $(cat ap2-integration/.env | grep -v '^#' | xargs)
else
    echo "⚠️  Warning: .env file not found. Using default ports."
fi

# Default ports
MERCHANT_PORT=${MERCHANT_AGENT_PORT:-8001}
CREDENTIALS_PORT=${CREDENTIALS_PROVIDER_PORT:-8002}
PROCESSOR_PORT=${PAYMENT_PROCESSOR_PORT:-8003}

# Check if MCP server is built
if [ ! -f "mcp-server/build/index.js" ]; then
    echo "❌ MCP server not built. Running: make build"
    make build
fi

echo -e "${BLUE}Starting agents...${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping all agents..."
    kill $(jobs -p) 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# Start Merchant Agent
echo -e "${GREEN}[1/3]${NC} Starting Merchant Agent (port $MERCHANT_PORT)..."
cd ap2-integration
uv run python -m src.merchant_agent &
MERCHANT_PID=$!
cd ..

sleep 2

# Start Credentials Provider
echo -e "${GREEN}[2/3]${NC} Starting Credentials Provider (port $CREDENTIALS_PORT)..."
cd ap2-integration
uv run python -m src.credentials_provider &
CREDENTIALS_PID=$!
cd ..

sleep 2

# Start Payment Processor
echo -e "${GREEN}[3/3]${NC} Starting Payment Processor (port $PROCESSOR_PORT)..."
cd ap2-integration
uv run python -m src.payment_processor &
PROCESSOR_PID=$!
cd ..

sleep 3

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ All agents are running!${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Agent URLs:"
echo "  🏪 Merchant Agent:          http://localhost:$MERCHANT_PORT"
echo "  💳 Credentials Provider:    http://localhost:$CREDENTIALS_PORT"
echo "  💰 Payment Processor:       http://localhost:$PROCESSOR_PORT"
echo ""
echo "AgentCards:"
echo "  curl http://localhost:$MERCHANT_PORT/.well-known/agent-card.json"
echo "  curl http://localhost:$CREDENTIALS_PORT/.well-known/agent-card.json"
echo "  curl http://localhost:$PROCESSOR_PORT/.well-known/agent-card.json"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all agents${NC}"
echo ""

# Keep script running
wait

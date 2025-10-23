#!/bin/bash
# Script para ejecutar TODO: MCP + Agentes AP2 + Web UI

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Load environment from root .env
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Ports
MERCHANT_PORT=8001
CREDENTIALS_PORT=8002
PROCESSOR_PORT=8003
WEB_PORT=8000

echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     🚀 Pokemon MCP + AP2 + Web UI - Full Demo         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo -e "${RED}🛑 Deteniendo todos los agentes...${NC}"
    kill $(jobs -p) 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# Start Merchant Agent
echo -e "${BLUE}[1/4]${NC} Iniciando Merchant Agent (puerto $MERCHANT_PORT)..."
PYTHONPATH=src python -m ap2.agents.merchant &
MERCHANT_PID=$!
sleep 2

# Start Credentials Provider
echo -e "${BLUE}[2/4]${NC} Iniciando Credentials Provider (puerto $CREDENTIALS_PORT)..."
PYTHONPATH=src python -m ap2.agents.credentials &
CREDENTIALS_PID=$!
sleep 2

# Start Payment Processor
echo -e "${BLUE}[3/4]${NC} Iniciando Payment Processor (puerto $PROCESSOR_PORT)..."
PYTHONPATH=src python -m ap2.agents.payment_processor &
PROCESSOR_PID=$!
sleep 2

# Start Shopping Web UI
echo -e "${BLUE}[4/4]${NC} Iniciando Shopping Web UI (puerto $WEB_PORT)..."
PYTHONPATH=src python -m ap2.agents.shopping.web_ui &
WEB_PID=$!
sleep 3

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              ✅ TODO LISTO Y FUNCIONANDO               ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}🌐 Web UI:${NC}                  http://localhost:$WEB_PORT"
echo -e "${YELLOW}📋 Merchant Agent:${NC}          http://localhost:$MERCHANT_PORT"
echo -e "${YELLOW}💳 Credentials Provider:${NC}    http://localhost:$CREDENTIALS_PORT"
echo -e "${YELLOW}💰 Payment Processor:${NC}       http://localhost:$PROCESSOR_PORT"
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}   Presiona Ctrl+C para detener todos los servicios${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Keep script running
wait

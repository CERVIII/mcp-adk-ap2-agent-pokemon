#!/bin/bash

# Script para iniciar la demostración completa de AP2
# Pokemon Marketplace con Shopping Agent y Merchant Agent

set -e

echo "🎮 Pokemon AP2 Demo - Startup Script"
echo "====================================="
echo ""

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar que estamos en el directorio correcto
if [ ! -f "pokemon-gen1.json" ]; then
    echo -e "${RED}❌ Error: pokemon-gen1.json not found${NC}"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Verificar que existe el archivo .env
if [ ! -f "ap2-integration/.env" ]; then
    echo -e "${YELLOW}⚠️  Warning: ap2-integration/.env not found${NC}"
    echo "Creating from .env.example..."
    cp ap2-integration/.env.example ap2-integration/.env
    echo -e "${YELLOW}Please edit ap2-integration/.env and add your GOOGLE_API_KEY${NC}"
    read -p "Press enter to continue when ready..."
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found${NC}"
    exit 1
fi

# Verificar uv
if ! command -v uv &> /dev/null; then
    echo -e "${RED}❌ uv package manager not found${NC}"
    echo "Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"
echo ""

# Función para cleanup al salir
cleanup() {
    echo ""
    echo "🛑 Shutting down agents..."
    kill $MERCHANT_PID 2>/dev/null || true
    kill $SHOPPING_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# Crear logs directory si no existe
mkdir -p logs

# Iniciar Merchant Agent
echo "🏪 Starting Merchant Agent on port 8001..."
cd ap2-integration
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python3 -m src.roles.merchant_agent > ../logs/merchant_agent.log 2>&1 &
MERCHANT_PID=$!
cd ..

sleep 3

# Verificar que el Merchant Agent está corriendo
if ! curl -s http://localhost:8001/ > /dev/null; then
    echo -e "${RED}❌ Merchant Agent failed to start${NC}"
    echo "Check logs/merchant_agent.log for details"
    exit 1
fi

echo -e "${GREEN}✅ Merchant Agent running (PID: $MERCHANT_PID)${NC}"
echo ""

# Iniciar Shopping Agent
echo "🛍️  Starting Shopping Agent on port 8000..."
cd ap2-integration
python3 -m src.roles.shopping_agent > ../logs/shopping_agent.log 2>&1 &
SHOPPING_PID=$!
cd ..

sleep 2

echo -e "${GREEN}✅ Shopping Agent running (PID: $SHOPPING_PID)${NC}"
echo ""

echo "======================================"
echo "🎉 AP2 Demo is now running!"
echo "======================================"
echo ""
echo "Services:"
echo "  • Merchant Agent:  http://localhost:8001"
echo "  • Shopping Agent:  Interactive CLI"
echo ""
echo "Logs:"
echo "  • Merchant: logs/merchant_agent.log"
echo "  • Shopping: logs/shopping_agent.log"
echo ""
echo "Test Merchant API:"
echo "  curl http://localhost:8001/catalog"
echo "  curl http://localhost:8001/.well-known/agent-card.json"
echo ""
echo "Press Ctrl+C to stop all agents"
echo ""

# Mantener el script corriendo
wait

#!/bin/bash
# Script para ejecutar Merchant Agent (AP2 - Puerto 8001)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT/ap2-integration"

# Verificar .env
if [ ! -f ".env" ]; then
    echo "❌ Error: archivo .env no encontrado en ap2-integration/"
    echo "Por favor ejecuta: cp .env.example .env"
    echo "Y configura tu GOOGLE_API_KEY"
    exit 1
fi

# Verificar puerto
if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Puerto 8001 ya está en uso"
    echo "Deseas matar el proceso? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        lsof -ti:8001 | xargs kill -9
        echo "✓ Proceso eliminado"
    else
        exit 1
    fi
fi

echo "🚀 Iniciando Merchant Agent (Puerto 8001)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 Endpoints disponibles:"
echo "  • http://localhost:8001/"
echo "  • http://localhost:8001/.well-known/agent-card.json"
echo "  • http://localhost:8001/cart/create"
echo "  • http://localhost:8001/payment/process"
echo ""

python -m src.roles.merchant_agent

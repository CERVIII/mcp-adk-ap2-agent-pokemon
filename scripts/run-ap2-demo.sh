#!/bin/bash
# Script para ejecutar demo completo de AP2 (Merchant + Shopping)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     🎮 Pokemon AP2 Demo - Merchant + Shopping Agents      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Verificar .env
if [ ! -f "$PROJECT_ROOT/ap2-integration/.env" ]; then
    echo "❌ Error: archivo .env no encontrado en ap2-integration/"
    echo "Por favor ejecuta: cp ap2-integration/.env.example ap2-integration/.env"
    echo "Y configura tu GOOGLE_API_KEY"
    exit 1
fi

# Verificar puertos
if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Puerto 8001 ya está en uso. Limpiando..."
    lsof -ti:8001 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Puerto 8000 ya está en uso. Limpiando..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

echo "🚀 Iniciando Merchant Agent (Puerto 8001)..."
cd "$PROJECT_ROOT/ap2-integration"
python -m src.roles.merchant_agent &
MERCHANT_PID=$!

# Esperar a que el merchant esté listo
echo "⏳ Esperando a que Merchant Agent inicie..."
sleep 3

# Verificar que el merchant esté corriendo
if ! lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "❌ Error: Merchant Agent no pudo iniciar"
    exit 1
fi

echo "✅ Merchant Agent corriendo (PID: $MERCHANT_PID)"
echo ""
echo "🚀 Iniciando Shopping Agent (Puerto 8000)..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💬 Agente conversacional listo"
echo "🛒 Puedes hacer compras interactivamente"
echo ""
echo "📍 Endpoints Merchant Agent:"
echo "  • http://localhost:8001/"
echo "  • http://localhost:8001/.well-known/agent-card.json"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Función de cleanup
cleanup() {
    echo ""
    echo "🛑 Deteniendo agentes..."
    kill $MERCHANT_PID 2>/dev/null || true
    echo "✅ Agentes detenidos"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Ejecutar shopping agent en primer plano
python -m src.roles.shopping_agent

# Si shopping termina, limpiar
cleanup

#!/bin/bash
# Script para ejecutar Shopping Agent (AP2 - Puerto 8000)

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

# Verificar que merchant esté corriendo
if ! lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Merchant Agent no está corriendo en el puerto 8001"
    echo "Por favor ejecuta primero: ./scripts/run-merchant.sh"
    echo ""
    echo "¿Deseas continuar de todos modos? (y/n)"
    read -r response
    if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        exit 1
    fi
fi

# Verificar puerto
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Puerto 8000 ya está en uso"
    echo "Deseas matar el proceso? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        lsof -ti:8000 | xargs kill -9
        echo "✓ Proceso eliminado"
    else
        exit 1
    fi
fi

echo "🚀 Iniciando Shopping Agent (Puerto 8000)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💬 Agente conversacional listo"
echo "🛒 Puedes hacer compras interactivamente"
echo ""

python -m src.roles.shopping_agent

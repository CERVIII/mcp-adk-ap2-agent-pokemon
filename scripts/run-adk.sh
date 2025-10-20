#!/bin/bash
# Script para ejecutar ADK Agent (conversacional simple)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT/adk-agent"

# Verificar .env
if [ ! -f ".env" ]; then
    echo "❌ Error: archivo .env no encontrado en adk-agent/"
    echo "Por favor ejecuta: cp .env.example .env"
    echo "Y configura tu GOOGLE_API_KEY"
    exit 1
fi

echo "🚀 Iniciando ADK Agent (conversacional simple)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python pokemon_agent.py

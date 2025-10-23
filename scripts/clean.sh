#!/bin/bash
# Script para limpiar el proyecto

set -e

echo "🧹 Limpiando proyecto Pokemon MCP + AP2 + ADK..."
echo ""

# Limpiar MCP Server
echo "📦 Limpiando MCP Server..."
rm -rf build/
rm -rf node_modules/
echo "  ✓ MCP Server limpio"

# Limpiar Python caches
echo "🐍 Limpiando caches de Python..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo "  ✓ Caches de Python eliminados"

# Preguntar si eliminar .env
echo ""
echo "⚠️  ¿Deseas eliminar archivos .env? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    rm -f adk-agent/.env ap2-integration/.env
    echo "  ✓ Archivos .env eliminados"
else
    echo "  ↷ Archivos .env conservados"
fi

echo ""
echo "✅ Limpieza completada"

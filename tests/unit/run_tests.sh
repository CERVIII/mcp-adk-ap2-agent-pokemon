#!/bin/bash
# Script para ejecutar tests unitarios

set -e

cd "$(dirname "$0")"

echo "🧪 Unit Tests - Pokemon MCP + AP2 Agent"
echo "=========================================="
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest no está instalado"
    echo "💡 Instálalo con: cd ../ap2-integration && uv pip install pytest pytest-asyncio"
    exit 1
fi

# Check if in virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  No se detectó un entorno virtual activado"
    echo "💡 Actívalo con: cd ../ap2-integration && source .venv/bin/activate"
    echo ""
    read -p "¿Continuar de todos modos? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Run tests
echo "🏃 Ejecutando tests..."
echo ""

if [ "$1" = "--coverage" ]; then
    pytest -v --cov=../ap2-integration/src --cov-report=term-missing --cov-report=html
    echo ""
    echo "📊 Reporte de cobertura generado en: htmlcov/index.html"
elif [ "$1" = "--verbose" ]; then
    pytest -vv --tb=long
elif [ "$1" = "--quick" ]; then
    pytest -x --tb=short
else
    pytest -v --tb=short "$@"
fi

echo ""
echo "✅ Tests completados"

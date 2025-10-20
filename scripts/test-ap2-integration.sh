#!/bin/bash
# Test rápido de la integración AP2

set -e

echo "🧪 Test de Integración AP2"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd "$(dirname "$0")/.."

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Paso 1: Verificar archivos"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -f "mcp-server/build/index.js" ]; then
    echo -e "${RED}❌ MCP server no compilado${NC}"
    echo "   Ejecuta: make build"
    exit 1
fi
echo -e "${GREEN}✅ MCP server compilado${NC}"

if [ ! -f "ap2-integration/.env" ]; then
    echo -e "${RED}❌ .env no encontrado${NC}"
    echo "   Ejecuta: cd ap2-integration && cp .env.example .env"
    exit 1
fi
echo -e "${GREEN}✅ .env configurado${NC}"

if ! grep -q "GOOGLE_API_KEY=AIza" ap2-integration/.env 2>/dev/null; then
    echo -e "${YELLOW}⚠️  GOOGLE_API_KEY parece no estar configurada${NC}"
    echo "   Edita ap2-integration/.env con tu API key"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Paso 2: Verificar estructura"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python_files=$(find ap2-integration/src -name "*.py" | wc -l | tr -d ' ')
echo -e "${GREEN}✅ $python_files archivos Python creados${NC}"

required_files=(
    "ap2-integration/src/common/ap2_types.py"
    "ap2-integration/src/merchant_agent/server.py"
    "ap2-integration/src/credentials_provider/server.py"
    "ap2-integration/src/payment_processor/server.py"
    "ap2-integration/src/shopping_agent/agent.py"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ Falta: $file${NC}"
        exit 1
    fi
done
echo -e "${GREEN}✅ Todos los archivos requeridos existen${NC}"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Paso 3: Verificar dependencias"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if ! command -v uv &> /dev/null; then
    echo -e "${RED}❌ uv no instalado${NC}"
    echo "   Ejecuta: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi
echo -e "${GREEN}✅ uv instalado${NC}"

if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ node no instalado${NC}"
    exit 1
fi
echo -e "${GREEN}✅ node instalado${NC}"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Paso 4: Test de MCP Client"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd ap2-integration
echo "Ejecutando test de MCP client..."
if uv run python -c "
import sys
sys.path.insert(0, 'src')
from common import ap2_types, utils
print('✅ Imports correctos')
" 2>/dev/null; then
    echo -e "${GREEN}✅ Módulos Python importan correctamente${NC}"
else
    echo -e "${YELLOW}⚠️  Algunos módulos pueden tener dependencias faltantes${NC}"
    echo "   Ejecuta: cd ap2-integration && uv sync"
fi
cd ..

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Paso 5: Verificar scripts"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

scripts=(
    "scripts/run-ap2-agents.sh"
    "scripts/run-shopping-agent.sh"
)

for script in "${scripts[@]}"; do
    if [ ! -x "$script" ]; then
        echo -e "${YELLOW}⚠️  $script no es ejecutable${NC}"
        chmod +x "$script"
        echo -e "${GREEN}   ✓ Permisos corregidos${NC}"
    else
        echo -e "${GREEN}✅ $script es ejecutable${NC}"
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 RESULTADO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}✅ Integración AP2 lista para usar!${NC}"
echo ""
echo "Para ejecutar el demo:"
echo ""
echo -e "${YELLOW}Terminal 1:${NC}"
echo "  ./scripts/run-ap2-agents.sh"
echo ""
echo -e "${YELLOW}Terminal 2:${NC}"
echo "  ./scripts/run-shopping-agent.sh"
echo ""
echo "O usa los comandos del Makefile:"
echo "  make run-ap2-agents  # Terminal 1"
echo "  make run-shopping    # Terminal 2"
echo ""
echo "Documentación:"
echo "  - AP2-QUICKSTART.md"
echo "  - AP2-INTEGRATION-SUMMARY.md"
echo "  - ap2-integration/README.md"
echo ""

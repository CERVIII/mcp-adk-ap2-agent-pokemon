#!/bin/bash
# Script de setup completo para Pokemon MCP + AP2 + ADK

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     🎮 Pokemon MCP + AP2 + ADK - Setup Completo          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Función para verificar comandos
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}✗ $1 no está instalado${NC}"
        echo -e "${YELLOW}Por favor instala $1 antes de continuar${NC}"
        exit 1
    else
        echo -e "${GREEN}✓ $1 encontrado${NC}"
    fi
}

# Verificar requisitos
echo -e "${YELLOW}📋 Verificando requisitos previos...${NC}"
check_command node
check_command npm
check_command python3
check_command uv

echo ""
echo -e "${GREEN}✅ Todos los requisitos están instalados${NC}"
echo ""

# 1. Instalar MCP Server
echo -e "${YELLOW}📦 1/3 Instalando MCP Server...${NC}"
npm install
npm run build
cd ..
echo -e "${GREEN}✓ MCP Server instalado y compilado${NC}"
echo ""

# 2. Instalar ADK Agent
echo -e "${YELLOW}📦 2/3 Instalando ADK Agent...${NC}"
cd adk-agent
uv pip install google-adk python-dotenv
cd ..
echo -e "${GREEN}✓ ADK Agent instalado${NC}"
echo ""

# 3. Instalar AP2 dependencies (usando pip en lugar de cd ap2-integration)
echo -e "${YELLOW}📦 3/3 Instalando AP2 dependencies...${NC}"
# Ya tenemos pyproject.toml en src/ap2/, instalar dependencias si es necesario
if [ -f "src/ap2/pyproject.toml" ]; then
    echo -e "${GREEN}✓ AP2 configuration found in src/ap2/${NC}"
else
    echo -e "${YELLOW}⚠️  src/ap2/pyproject.toml not found${NC}"
fi
echo ""

# Configurar .env si no existe (solo raíz ahora)
echo -e "${YELLOW}🔑 Configurando archivos .env...${NC}"

if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creando .env en raíz del proyecto${NC}"
    echo "GOOGLE_API_KEY=YOUR_API_KEY_HERE" > .env
    echo "SHOPPING_AGENT_PORT=8000" >> .env
    echo "MERCHANT_AGENT_PORT=8001" >> .env
    echo "CREDENTIALS_PROVIDER_PORT=8002" >> .env
    echo "PAYMENT_PROCESSOR_PORT=8003" >> .env
    echo -e "${RED}⚠️  Por favor edita .env con tu GOOGLE_API_KEY${NC}"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                  ✅ Setup Completado                       ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}📝 Próximos pasos:${NC}"
echo ""
echo -e "  1. Configurar API Key:"
echo -e "     ${BLUE}nano .env${NC}"
echo ""
echo -e "  2. Ejecutar componentes:"
echo -e "     ${BLUE}./scripts/run-ap2-agents.sh${NC}   # AP2 Agents (puertos 8001-8003)"
echo -e "     ${BLUE}./scripts/run-web-only.sh${NC}     # Shopping Web UI (puerto 8000)"
echo -e "     ${BLUE}./scripts/run-full-demo.sh${NC}    # Demo completo AP2"
echo ""
echo -e "  3. O usar el Makefile:"
echo -e "     ${BLUE}make help${NC}                      # Ver todos los comandos"
echo ""

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
cd mcp-server
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

# 3. Instalar AP2 Integration
echo -e "${YELLOW}📦 3/3 Instalando AP2 Integration...${NC}"
cd ap2-integration
uv pip install fastapi uvicorn pydantic python-dotenv google-adk requests
cd ..
echo -e "${GREEN}✓ AP2 Integration instalado${NC}"
echo ""

# Configurar .env si no existen
echo -e "${YELLOW}🔑 Configurando archivos .env...${NC}"

if [ ! -f "adk-agent/.env" ]; then
    echo -e "${YELLOW}Creando adk-agent/.env desde .env.example${NC}"
    cp adk-agent/.env.example adk-agent/.env
    echo -e "${RED}⚠️  Por favor edita adk-agent/.env con tu GOOGLE_API_KEY${NC}"
fi

if [ ! -f "ap2-integration/.env" ]; then
    echo -e "${YELLOW}Creando ap2-integration/.env desde .env.example${NC}"
    cp ap2-integration/.env.example ap2-integration/.env
    echo -e "${RED}⚠️  Por favor edita ap2-integration/.env con tu GOOGLE_API_KEY${NC}"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                  ✅ Setup Completado                       ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}📝 Próximos pasos:${NC}"
echo ""
echo -e "  1. Configurar API Keys:"
echo -e "     ${BLUE}nano adk-agent/.env${NC}"
echo -e "     ${BLUE}nano ap2-integration/.env${NC}"
echo ""
echo -e "  2. Ejecutar componentes:"
echo -e "     ${BLUE}./scripts/run-adk.sh${NC}           # ADK Agent simple"
echo -e "     ${BLUE}./scripts/run-merchant.sh${NC}      # Merchant Agent (Puerto 8001)"
echo -e "     ${BLUE}./scripts/run-shopping.sh${NC}      # Shopping Agent (Puerto 8000)"
echo -e "     ${BLUE}./scripts/run-ap2-demo.sh${NC}      # Demo completo AP2"
echo ""
echo -e "  3. O usar el Makefile:"
echo -e "     ${BLUE}make help${NC}                      # Ver todos los comandos"
echo ""

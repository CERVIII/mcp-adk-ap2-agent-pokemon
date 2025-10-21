#!/bin/bash
# Script para ejecutar solo el Web UI (sin agentes backend)
# Útil cuando quieres interactuar directamente con los MCPs

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

WEB_PORT=8000

echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          🛍️  Pokemon Shopping Web UI Only             ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}⚠️  Nota:${NC} Este modo solo ejecuta el Web UI."
echo -e "   Los agentes AP2 deben estar ejecutándose por separado."
echo ""
echo -e "${BLUE}Iniciando Web UI en puerto $WEB_PORT...${NC}"
echo ""

cd ap2-integration
uv run python src/shopping_agent/web_ui.py

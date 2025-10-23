#!/bin/bash

# Script para probar el servidor MCP unificado con soporte AP2

echo "🧪 Testing Unified MCP Pokemon Server with AP2 Support"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}📦 Step 1: Installing dependencies...${NC}"
npm install --silent
echo ""

echo -e "${BLUE}🔨 Step 2: Building server...${NC}"
npm run build
echo ""

echo -e "${BLUE}🚀 Step 3: Starting server in test mode...${NC}"
echo -e "${YELLOW}Note: The server will run and listen for stdio commands${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo ""

echo -e "${GREEN}✅ Server is ready with the following tools:${NC}"
echo "  1. get_pokemon_info"
echo "  2. get_pokemon_price"
echo "  3. search_pokemon"
echo "  4. list_pokemon_types"
echo "  5. create_pokemon_cart (AP2) ⭐"
echo "  6. get_pokemon_product (AP2) ⭐"
echo ""

echo -e "${GREEN}📋 Configuration file: .vscode/mcp.json${NC}"
echo ""
echo -e "${GREEN}🔄 To use in GitHub Copilot:${NC}"
echo "  1. Press Ctrl+Shift+P"
echo "  2. Type 'GitHub Copilot: Restart Chat'"
echo "  3. The server will be available automatically"
echo ""

# Run the server
npx tsx src/index.ts

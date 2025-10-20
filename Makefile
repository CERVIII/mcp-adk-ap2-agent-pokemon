# Makefile para Pokemon MCP + AP2 + ADK Integration
# Uso: make <comando>

.PHONY: help install build clean dev test run-mcp run-merchant run-shopping run-all

# Colores para output
GREEN=\033[0;32m
YELLOW=\033[1;33m
RED=\033[0;31m
NC=\033[0m # No Color

help: ## Mostrar esta ayuda
	@echo "$(GREEN)🎮 Pokemon MCP + AP2 + ADK - Comandos Disponibles$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

# ==================== INSTALACIÓN ====================

install: install-mcp install-adk install-ap2 ## Instalar todas las dependencias
	@echo "$(GREEN)✅ Todas las dependencias instaladas$(NC)"

install-mcp: ## Instalar dependencias del MCP Server
	@echo "$(YELLOW)📦 Instalando MCP Server...$(NC)"
	cd mcp-server && npm install

install-adk: ## Instalar dependencias del ADK Agent
	@echo "$(YELLOW)📦 Instalando ADK Agent...$(NC)"
	cd adk-agent && uv pip install google-adk python-dotenv

install-ap2: ## Instalar dependencias de AP2 Integration
	@echo "$(YELLOW)📦 Instalando AP2 Integration...$(NC)"
	cd ap2-integration && uv pip install fastapi uvicorn pydantic python-dotenv google-adk requests

# ==================== COMPILACIÓN ====================

build: build-mcp ## Compilar todos los componentes
	@echo "$(GREEN)✅ Compilación completada$(NC)"

build-mcp: ## Compilar MCP Server (TypeScript)
	@echo "$(YELLOW)🔨 Compilando MCP Server...$(NC)"
	cd mcp-server && npm run build

# ==================== LIMPIEZA ====================

clean: clean-mcp clean-python ## Limpiar archivos compilados y caches
	@echo "$(GREEN)✅ Limpieza completada$(NC)"

clean-mcp: ## Limpiar build de MCP Server
	@echo "$(YELLOW)🧹 Limpiando MCP Server...$(NC)"
	rm -rf mcp-server/build/
	rm -rf mcp-server/node_modules/

clean-python: ## Limpiar caches de Python
	@echo "$(YELLOW)🧹 Limpiando Python caches...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

fclean: clean ## Limpiar todo (incluyendo .env)
	@echo "$(RED)⚠️  Eliminando archivos .env...$(NC)"
	rm -f adk-agent/.env ap2-integration/.env

# ==================== DESARROLLO ====================

dev: build run-mcp ## Modo desarrollo: compilar y ejecutar MCP

setup: install build ## Setup completo: instalar + compilar
	@echo "$(GREEN)✅ Setup completado. Configura tus .env antes de ejecutar.$(NC)"

# ==================== EJECUCIÓN ====================

run-mcp: ## Ejecutar solo MCP Server (stdio)
	@echo "$(YELLOW)🚀 Ejecutando MCP Server...$(NC)"
	cd mcp-server && npm start

run-adk: ## Ejecutar ADK Agent (conversacional simple)
	@echo "$(YELLOW)🚀 Ejecutando ADK Agent...$(NC)"
	cd adk-agent && python pokemon_agent.py

run-merchant: ## Ejecutar Merchant Agent (AP2 - Puerto 8001)
	@echo "$(YELLOW)🚀 Ejecutando Merchant Agent (Puerto 8001)...$(NC)"
	cd ap2-integration && python -m src.roles.merchant_agent

run-shopping: ## Ejecutar Shopping Agent (AP2 - Puerto 8000)
	@echo "$(YELLOW)🚀 Ejecutando Shopping Agent (Puerto 8000)...$(NC)"
	cd ap2-integration && python -m src.roles.shopping_agent

# ==================== TESTS ====================

test: test-mcp ## Ejecutar todos los tests
	@echo "$(GREEN)✅ Tests completados$(NC)"

test-mcp: ## Test del MCP Server
	@echo "$(YELLOW)🧪 Ejecutando tests MCP...$(NC)"
	python tests/test_mcp_simple.py

# ==================== UTILIDADES ====================

check-env: ## Verificar configuración de .env
	@echo "$(YELLOW)🔍 Verificando archivos .env...$(NC)"
	@test -f adk-agent/.env && echo "$(GREEN)✓ adk-agent/.env existe$(NC)" || echo "$(RED)✗ adk-agent/.env NO existe$(NC)"
	@test -f ap2-integration/.env && echo "$(GREEN)✓ ap2-integration/.env existe$(NC)" || echo "$(RED)✗ ap2-integration/.env NO existe$(NC)"

status: ## Ver estado del proyecto
	@echo "$(GREEN)📊 Estado del Proyecto$(NC)"
	@echo ""
	@echo "$(YELLOW)MCP Server:$(NC)"
	@test -d mcp-server/node_modules && echo "  ✓ Dependencias instaladas" || echo "  ✗ Dependencias NO instaladas"
	@test -d mcp-server/build && echo "  ✓ Compilado" || echo "  ✗ NO compilado"
	@echo ""
	@echo "$(YELLOW)ADK Agent:$(NC)"
	@test -f adk-agent/.env && echo "  ✓ .env configurado" || echo "  ✗ .env NO configurado"
	@echo ""
	@echo "$(YELLOW)AP2 Integration:$(NC)"
	@test -f ap2-integration/.env && echo "  ✓ .env configurado" || echo "  ✗ .env NO configurado"
	@echo ""

ports: ## Verificar puertos en uso
	@echo "$(YELLOW)🔌 Verificando puertos...$(NC)"
	@lsof -i :8000 2>/dev/null && echo "$(RED)Puerto 8000 EN USO$(NC)" || echo "$(GREEN)Puerto 8000 disponible$(NC)"
	@lsof -i :8001 2>/dev/null && echo "$(RED)Puerto 8001 EN USO$(NC)" || echo "$(GREEN)Puerto 8001 disponible$(NC)"

# ==================== DEFAULT ====================

.DEFAULT_GOAL := help

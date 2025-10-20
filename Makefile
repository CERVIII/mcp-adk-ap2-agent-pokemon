# Makefile para Pokemon MCP + AP2 + ADK Integration
# Uso: make <comando>

.PHONY: help install build clean dev test run run-demo run-mcp run-adk run-merchant run-shopping \
        ensure-ready ensure-mcp-ready ensure-env-adk ensure-env-ap2 ensure-deps-adk ensure-deps-ap2 \
        check-env configure-api-key status ports

# Colores para output
GREEN=\033[0;32m
YELLOW=\033[1;33m
RED=\033[0;31m
NC=\033[0m # No Color

help: ## Mostrar esta ayuda
	@echo "$(GREEN)╔════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║     🎮 Pokemon MCP + AP2 + ADK - Comandos Disponibles    ║$(NC)"
	@echo "$(GREEN)╚════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)⚡ Inicio Rápido:$(NC)"
	@echo "  $(GREEN)make run$(NC)        - Auto-configura e inicia demo completo"
	@echo ""
	@echo "$(YELLOW)📋 Comandos Disponibles:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)💡 Ejemplos:$(NC)"
	@echo "  make run             # Ejecuta demo completo (auto-setup)"
	@echo "  make run-adk         # Solo ADK Agent"
	@echo "  make status          # Ver estado del proyecto"
	@echo "  make clean           # Limpiar compilados"
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

run: ensure-ready run-demo ## 🚀 Ejecutar demo completo (auto-configura todo)

run-demo: ## Demo AP2 completo (Merchant + Shopping)
	@echo "$(GREEN)🎮 Iniciando Demo Completo AP2...$(NC)"
	@./scripts/run-ap2-demo.sh

run-mcp: ensure-mcp-ready ## Ejecutar solo MCP Server (stdio)
	@echo "$(YELLOW)🚀 Ejecutando MCP Server...$(NC)"
	cd mcp-server && npm start

run-adk: ensure-ready ## Ejecutar ADK Agent (conversacional simple)
	@echo "$(YELLOW)🚀 Ejecutando ADK Agent...$(NC)"
	@./scripts/run-adk.sh

run-merchant: ensure-ready ## Ejecutar Merchant Agent (AP2 - Puerto 8001)
	@echo "$(YELLOW)🚀 Ejecutando Merchant Agent (Puerto 8001)...$(NC)"
	@./scripts/run-merchant.sh

run-shopping: ensure-ready ## Ejecutar Shopping Agent (AP2 - Puerto 8000)
	@echo "$(YELLOW)🚀 Ejecutando Shopping Agent (Puerto 8000)...$(NC)"
	@./scripts/run-shopping.sh

# ==================== TESTS ====================

test: test-mcp ## Ejecutar todos los tests
	@echo "$(GREEN)✅ Tests completados$(NC)"

test-mcp: ## Test del MCP Server
	@echo "$(YELLOW)🧪 Ejecutando tests MCP...$(NC)"
	python tests/test_mcp_simple.py

# ==================== UTILIDADES ====================

# Verificaciones internas (sin mostrar en help)
ensure-mcp-ready:
	@if [ ! -d "mcp-server/node_modules" ]; then \
		echo "$(YELLOW)📦 Instalando dependencias MCP Server...$(NC)"; \
		$(MAKE) install-mcp; \
	fi
	@if [ ! -d "mcp-server/build" ]; then \
		echo "$(YELLOW)🔨 Compilando MCP Server...$(NC)"; \
		$(MAKE) build-mcp; \
	fi

ensure-env-adk:
	@if [ ! -f "adk-agent/.env" ]; then \
		echo "$(YELLOW)🔑 Creando adk-agent/.env desde template...$(NC)"; \
		cp adk-agent/.env.example adk-agent/.env; \
		echo "$(RED)⚠️  IMPORTANTE: Edita adk-agent/.env y añade tu GOOGLE_API_KEY$(NC)"; \
		echo "$(YELLOW)   Obtén tu clave en: https://aistudio.google.com/apikey$(NC)"; \
		echo ""; \
		read -p "Presiona Enter después de configurar tu API Key..." dummy; \
	fi

ensure-env-ap2:
	@if [ ! -f "ap2-integration/.env" ]; then \
		echo "$(YELLOW)🔑 Creando ap2-integration/.env desde template...$(NC)"; \
		cp ap2-integration/.env.example ap2-integration/.env; \
		echo "$(RED)⚠️  IMPORTANTE: Edita ap2-integration/.env y añade tu GOOGLE_API_KEY$(NC)"; \
		echo "$(YELLOW)   Obtén tu clave en: https://aistudio.google.com/apikey$(NC)"; \
		echo ""; \
		read -p "Presiona Enter después de configurar tu API Key..." dummy; \
	fi

ensure-deps-adk:
	@if ! python3 -c "import google.generativeai" 2>/dev/null; then \
		echo "$(YELLOW)📦 Instalando dependencias ADK Agent...$(NC)"; \
		$(MAKE) install-adk; \
	fi

ensure-deps-ap2:
	@if ! python3 -c "import fastapi" 2>/dev/null; then \
		echo "$(YELLOW)📦 Instalando dependencias AP2 Integration...$(NC)"; \
		$(MAKE) install-ap2; \
	fi

ensure-ready: ensure-mcp-ready ensure-env-adk ensure-env-ap2 ensure-deps-adk ensure-deps-ap2
	@echo "$(GREEN)✅ Todo listo para ejecutar$(NC)"
	@echo ""

check-env: ## Verificar configuración de .env
	@echo "$(YELLOW)🔍 Verificando archivos .env...$(NC)"
	@test -f adk-agent/.env && echo "$(GREEN)✓ adk-agent/.env existe$(NC)" || echo "$(RED)✗ adk-agent/.env NO existe$(NC)"
	@test -f ap2-integration/.env && echo "$(GREEN)✓ ap2-integration/.env existe$(NC)" || echo "$(RED)✗ ap2-integration/.env NO existe$(NC)"

configure-api-key: ## Configurar Google API Key interactivamente
	@echo "$(GREEN)╔════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║           🔑 Configuración de Google API Key              ║$(NC)"
	@echo "$(GREEN)╚════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)1. Obtén tu API Key en: https://aistudio.google.com/apikey$(NC)"
	@echo "$(YELLOW)2. Copia la clave$(NC)"
	@echo ""
	@read -p "Ingresa tu Google API Key: " api_key; \
	if [ -z "$$api_key" ]; then \
		echo "$(RED)❌ API Key vacía. Cancelando.$(NC)"; \
		exit 1; \
	fi; \
	echo "GOOGLE_API_KEY=$$api_key" > adk-agent/.env; \
	echo "GOOGLE_API_KEY=$$api_key" > ap2-integration/.env; \
	echo ""; \
	echo "$(GREEN)✅ API Key configurada en:$(NC)"; \
	echo "  • adk-agent/.env"; \
	echo "  • ap2-integration/.env"; \
	echo ""

status: ## Ver estado del proyecto
	@echo "$(GREEN)╔════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║              📊 Estado del Proyecto Pokemon               ║$(NC)"
	@echo "$(GREEN)╚════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)🔷 MCP Server (TypeScript):$(NC)"
	@test -d mcp-server/node_modules && echo "  $(GREEN)✓$(NC) Dependencias instaladas" || echo "  $(RED)✗$(NC) Dependencias NO instaladas (ejecuta: make install-mcp)"
	@test -d mcp-server/build && echo "  $(GREEN)✓$(NC) Compilado" || echo "  $(RED)✗$(NC) NO compilado (ejecuta: make build-mcp)"
	@echo ""
	@echo "$(YELLOW)🤖 ADK Agent (Python):$(NC)"
	@test -f adk-agent/.env && echo "  $(GREEN)✓$(NC) .env configurado" || echo "  $(RED)✗$(NC) .env NO configurado (ejecuta: make ensure-env-adk)"
	@python3 -c "import google.generativeai" 2>/dev/null && echo "  $(GREEN)✓$(NC) Dependencias instaladas" || echo "  $(RED)✗$(NC) Dependencias NO instaladas (ejecuta: make install-adk)"
	@echo ""
	@echo "$(YELLOW)💳 AP2 Integration (Python):$(NC)"
	@test -f ap2-integration/.env && echo "  $(GREEN)✓$(NC) .env configurado" || echo "  $(RED)✗$(NC) .env NO configurado (ejecuta: make ensure-env-ap2)"
	@python3 -c "import fastapi" 2>/dev/null && echo "  $(GREEN)✓$(NC) Dependencias instaladas" || echo "  $(RED)✗$(NC) Dependencias NO instaladas (ejecuta: make install-ap2)"
	@echo ""
	@echo "$(YELLOW)📝 Estado General:$(NC)"
	@if [ -d "mcp-server/node_modules" ] && [ -d "mcp-server/build" ] && [ -f "adk-agent/.env" ] && [ -f "ap2-integration/.env" ]; then \
		echo "  $(GREEN)✅ Todo listo para ejecutar: make run$(NC)"; \
	else \
		echo "  $(YELLOW)⚠️  Configuración incompleta. Ejecuta: make run (auto-configura)$(NC)"; \
	fi
	@echo ""

ports: ## Verificar puertos en uso
	@echo "$(YELLOW)🔌 Verificando puertos...$(NC)"
	@lsof -i :8000 2>/dev/null && echo "$(RED)Puerto 8000 EN USO$(NC)" || echo "$(GREEN)Puerto 8000 disponible$(NC)"
	@lsof -i :8001 2>/dev/null && echo "$(RED)Puerto 8001 EN USO$(NC)" || echo "$(GREEN)Puerto 8001 disponible$(NC)"

# ==================== DEFAULT ====================

.DEFAULT_GOAL := help

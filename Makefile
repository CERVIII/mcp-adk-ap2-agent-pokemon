# Makefile para Pokemon MCP + AP2 Integration
# Uso: make [comando]

.PHONY: help install build clean run stop test status

# Colores
GREEN=\033[0;32m
YELLOW=\033[1;33m
BLUE=\033[0;34m
RED=\033[0;31m
NC=\033[0m

# ==================== HELP ====================

help: ## Mostrar ayuda
	@echo "$(GREEN)🎮 Pokemon MCP + AP2 - Comandos Principales$(NC)"
	@echo ""
	@echo "$(BLUE)Comandos de Uso Diario:$(NC)"
	@echo "  $(YELLOW)make run$(NC)        - Compilar y ejecutar TODO (MCP + Agentes AP2 + Web UI)"
	@echo "  $(YELLOW)make stop$(NC)       - Detener todos los agentes"
	@echo "  $(YELLOW)make status$(NC)     - Ver estado del proyecto"
	@echo ""
	@echo "$(BLUE)Setup Inicial:$(NC)"
	@echo "  $(YELLOW)make setup$(NC)      - Instalar dependencias + compilar (primera vez)"
	@echo "  $(YELLOW)make install$(NC)    - Solo instalar dependencias"
	@echo "  $(YELLOW)make build$(NC)      - Solo compilar TypeScript"
	@echo ""
	@echo "$(BLUE)Limpieza:$(NC)"
	@echo "  $(YELLOW)make clean$(NC)      - Limpiar builds y caches"
	@echo "  $(YELLOW)make reset$(NC)      - Reset completo (limpia TODO menos .env)"
	@echo ""
	@echo "$(BLUE)Testing:$(NC)"
	@echo "  $(YELLOW)make test$(NC)       - Ejecutar tests"
	@echo ""
	@echo "$(BLUE)Avanzado:$(NC) make help-advanced"
	@echo ""

# ==================== SETUP ====================

setup: install build check-env ## Setup completo (primera vez)
	@echo "$(GREEN)✅ Setup completado!$(NC)"
	@echo ""
	@echo "$(YELLOW)Siguiente paso:$(NC) make run"
	@echo ""

install: ## Instalar todas las dependencias
	@echo "$(BLUE)📦 Instalando dependencias...$(NC)"
	@cd mcp-server && npm install
	@cd ap2-integration && uv sync
	@echo "$(GREEN)✅ Dependencias instaladas$(NC)"

build: ## Compilar MCP Server
	@echo "$(BLUE)� Compilando MCP Server...$(NC)"
	@cd mcp-server && npm run build
	@echo "$(GREEN)✅ Compilado$(NC)"

# ==================== RUN ====================

run: build check-env ## 🚀 Compilar y ejecutar TODO
	@echo "$(GREEN)╔════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║  🚀 Iniciando Pokemon MCP + AP2 + Web UI              ║$(NC)"
	@echo "$(GREEN)╚════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)� Se iniciarán:$(NC)"
	@echo "  • Merchant Agent      (Puerto 8001)"
	@echo "  • Credentials Provider (Puerto 8002)"
	@echo "  • Payment Processor    (Puerto 8003)"
	@echo "  • Shopping Web UI      (Puerto 8000)"
	@echo ""
	@echo "$(BLUE)🌐 Web UI disponible en: http://localhost:8000$(NC)"
	@echo ""
	@./scripts/run-full-demo.sh

run-agents: build ## Ejecutar solo agentes AP2 (sin Web UI)
	@echo "$(YELLOW)🚀 Iniciando agentes AP2...$(NC)"
	@./scripts/run-ap2-agents.sh

run-web: ## Ejecutar solo Shopping Web UI
	@echo "$(YELLOW)� Iniciando Web UI...$(NC)"
	@cd ap2-integration && uv run python -m src.shopping_agent

# ==================== STOP ====================

stop: ## Detener todos los agentes
	@echo "$(RED)🛑 Deteniendo agentes...$(NC)"
	@lsof -ti:8000 | xargs kill -9 2>/dev/null || true
	@lsof -ti:8001 | xargs kill -9 2>/dev/null || true
	@lsof -ti:8002 | xargs kill -9 2>/dev/null || true
	@lsof -ti:8003 | xargs kill -9 2>/dev/null || true
	@echo "$(GREEN)✅ Agentes detenidos$(NC)"

# ==================== CLEAN ====================

clean: clean-build clean-cache ## Limpiar builds y caches
	@echo "$(GREEN)✅ Limpieza completada$(NC)"

clean-build: ## Limpiar archivos compilados
	@echo "$(YELLOW)🧹 Limpiando builds...$(NC)"
	@rm -rf mcp-server/build/
	@find . -type f -name "*.tsbuildinfo" -delete 2>/dev/null || true

clean-cache: ## Limpiar caches
	@echo "$(YELLOW)🧹 Limpiando caches...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true

clean-temp: ## Limpiar temporales
	@echo "$(YELLOW)🧹 Limpiando temporales...$(NC)"
	@find . -name ".DS_Store" -delete 2>/dev/null || true
	@find . -type f -name "*.log" -delete 2>/dev/null || true
	@find . -type f -name "*.tmp" -delete 2>/dev/null || true

reset: clean clean-temp ## Reset completo (limpia TODO menos .env)
	@echo "$(RED)⚠️  Reset completo...$(NC)"
	@rm -rf mcp-server/node_modules/
	@rm -rf ap2-integration/.venv/
	@echo "$(GREEN)✅ Reset completado$(NC)"
	@echo "$(YELLOW)Siguiente paso:$(NC) make setup"

# ==================== TEST ====================

test: ## Ejecutar tests
	@echo "$(BLUE)🧪 Ejecutando tests...$(NC)"
	@cd ap2-integration && uv run python ../tests/test_jwt_signature.py
	@echo "$(GREEN)✅ Tests completados$(NC)"

# ==================== UTILITIES ====================

check-env: ## Verificar configuración de .env
	@echo "$(BLUE)🔍 Verificando archivos .env...$(NC)"
	@test -f ap2-integration/.env && echo "$(GREEN)✓ ap2-integration/.env existe$(NC)" || echo "$(RED)✗ ap2-integration/.env NO existe (copia .env.example)$(NC)"

status: ## Ver estado del proyecto
	@echo "$(GREEN)📊 Estado del Proyecto$(NC)"
	@echo ""
	@echo "$(BLUE)MCP Server:$(NC)"
	@test -d mcp-server/node_modules && echo "  $(GREEN)✓$(NC) Dependencias instaladas" || echo "  $(RED)✗$(NC) Dependencias NO instaladas"
	@test -d mcp-server/build && echo "  $(GREEN)✓$(NC) Compilado" || echo "  $(RED)✗$(NC) NO compilado"
	@echo ""
	@echo "$(BLUE)AP2 Integration:$(NC)"
	@test -f ap2-integration/.env && echo "  $(GREEN)✓$(NC) .env configurado" || echo "  $(RED)✗$(NC) .env NO configurado"
	@echo ""
	@echo "$(BLUE)Puertos:$(NC)"
	@lsof -i :8000 2>/dev/null && echo "  $(RED)✗$(NC) 8000 EN USO (Shopping Web UI)" || echo "  $(GREEN)✓$(NC) 8000 disponible"
	@lsof -i :8001 2>/dev/null && echo "  $(RED)✗$(NC) 8001 EN USO (Merchant)" || echo "  $(GREEN)✓$(NC) 8001 disponible"
	@lsof -i :8002 2>/dev/null && echo "  $(RED)✗$(NC) 8002 EN USO (Credentials)" || echo "  $(GREEN)✓$(NC) 8002 disponible"
	@lsof -i :8003 2>/dev/null && echo "  $(RED)✗$(NC) 8003 EN USO (Processor)" || echo "  $(GREEN)✓$(NC) 8003 disponible"

ports: ## Ver qué procesos usan los puertos
	@echo "$(BLUE)🔌 Procesos en puertos 8000-8003:$(NC)"
	@lsof -i :8000,8001,8002,8003 2>/dev/null || echo "$(GREEN)No hay procesos en estos puertos$(NC)"

help-advanced: ## Mostrar comandos avanzados
	@echo "$(GREEN)📚 Comandos Avanzados$(NC)"
	@echo ""
	@echo "$(BLUE)Ejecución granular:$(NC)"
	@echo "  $(YELLOW)make run-agents$(NC)   - Solo AP2 agents (sin Web UI)"
	@echo "  $(YELLOW)make run-web$(NC)      - Solo Shopping Web UI"
	@echo ""
	@echo "$(BLUE)Limpieza granular:$(NC)"
	@echo "  $(YELLOW)make clean-build$(NC)  - Solo archivos compilados"
	@echo "  $(YELLOW)make clean-cache$(NC)  - Solo caches Python"
	@echo "  $(YELLOW)make clean-temp$(NC)   - Solo archivos temporales"
	@echo "  $(YELLOW)make reset$(NC)        - Reset completo (elimina node_modules y .venv)"
	@echo ""
	@echo "$(BLUE)Diagnóstico:$(NC)"
	@echo "  $(YELLOW)make check-env$(NC)    - Verificar .env"
	@echo "  $(YELLOW)make status$(NC)       - Estado completo"
	@echo "  $(YELLOW)make ports$(NC)        - Ver procesos en puertos"

.DEFAULT_GOAL := help

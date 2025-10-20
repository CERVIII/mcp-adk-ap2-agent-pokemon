# 📜 Scripts de Gestión

Scripts centralizados para gestionar el proyecto Pokemon MCP + AP2.

## 🚀 Scripts Disponibles

### Setup y Configuración

#### `setup.sh`
Setup completo del proyecto - **RECOMENDADO PARA PRIMERA INSTALACIÓN**.

```bash
./scripts/setup.sh
```

**Funciones:**
- ✅ Verifica requisitos (Node.js, Python, uv)
- 📦 Instala dependencias MCP Server (npm)
- 📦 Instala dependencias AP2 Integration (uv)
- 🔨 Compila el MCP Server TypeScript
- 🔑 Crea archivos .env desde .env.example
- ✅ Valida que todo esté listo para usar

### Ejecución de Servicios

#### `run-ap2-agents.sh` 🌟
Ejecuta **todos los agentes AP2** simultáneamente.

```bash
./scripts/run-ap2-agents.sh
```

**Inicia:**
- 🏪 **Merchant Agent** (Puerto 8001) - Gestión de CartMandates
- 💳 **Credentials Provider** (Puerto 8002) - Métodos de pago
- 💰 **Payment Processor** (Puerto 8003) - Procesamiento de pagos

**Características:**
- Ejecuta los 3 agentes en background
- URLs de Agent Cards disponibles
- Press Ctrl+C para detener todos
- Logs en tiempo real

**URLs disponibles:**
```
http://localhost:8001/.well-known/agent-card.json
http://localhost:8002/.well-known/agent-card.json
http://localhost:8003/.well-known/agent-card.json
```

#### `run-shopping-agent.sh` 🛍️
Ejecuta el **Shopping Agent con Web UI**.

```bash
./scripts/run-shopping-agent.sh
```

**Características:**
- 🌐 Interfaz web completa en http://localhost:8000
- 📊 API docs en http://localhost:8000/docs
- 🛒 Shopping cart con AP2 checkout
- 🔍 Búsqueda de Pokemon con filtros
- 🔐 JWT RS256 signatures en PaymentMandates
- 💳 Flujo completo de pago

**Endpoints principales:**
```
GET  /                      # Web UI
GET  /api/search            # Buscar Pokemon
POST /api/cart/add          # Agregar al carrito
GET  /api/cart              # Ver carrito
POST /api/cart/checkout     # Checkout con AP2
GET  /api/quick-demo        # Demo automático
```

### Testing

#### `test-ap2-integration.sh`
Tests de integración para el flujo AP2 completo.

```bash
./scripts/test-ap2-integration.sh
```

**Verifica:**
- Conexión entre agentes
- Flujo de CartMandate
- Flujo de PaymentMandate
- Procesamiento de pagos

### Utilidades

#### `clean.sh`
Limpia archivos compilados y caches.

```bash
./scripts/clean.sh
```

**Limpia:**
- `mcp-server/build/` - TypeScript compilado
- `**/node_modules/` - Dependencias npm
- `**/.venv/` - Entornos virtuales Python
- `**/__pycache__/` - Cache de Python
- `**/.pytest_cache/` - Cache de pytest

## 📋 Flujo de Trabajo Recomendado

### Primera vez

```bash
# 1. Setup inicial (solo una vez)
./scripts/setup.sh

# 2. Iniciar agentes AP2 (Terminal 1)
./scripts/run-ap2-agents.sh

# 3. Iniciar Web UI (Terminal 2)
./scripts/run-shopping-agent.sh

# 4. Abrir navegador
open http://localhost:8000
```

### Desarrollo diario

```bash
# Opción A: Usar Web UI
./scripts/run-ap2-agents.sh     # Terminal 1
./scripts/run-shopping-agent.sh # Terminal 2

# Opción B: Usar GitHub Copilot/Claude
# El MCP server ya está configurado en .vscode/mcp.json
# Solo necesitas reiniciar Copilot: Ctrl+Shift+P → "Restart Chat"
```

### Limpiar y recompilar

```bash
# Limpiar todo
./scripts/clean.sh

# Reinstalar y compilar
./scripts/setup.sh
```

## 🔧 Requisitos

Todos los scripts asumen que tienes:

- **Node.js** 18+ y npm
- **Python** 3.10+
- **uv** package manager
- **GOOGLE_API_KEY** en `ap2-integration/.env`

Si falta algo, `setup.sh` te lo indicará.

## 📝 Notas

### Puertos Usados

| Puerto | Servicio               | Script                    |
|--------|------------------------|---------------------------|
| 8000   | Shopping Web UI        | run-shopping-agent.sh     |
| 8001   | Merchant Agent         | run-ap2-agents.sh         |
| 8002   | Credentials Provider   | run-ap2-agents.sh         |
| 8003   | Payment Processor      | run-ap2-agents.sh         |

### Si un puerto está ocupado

```bash
# Ver qué proceso usa el puerto
lsof -i :8000

# Matar proceso
kill -9 <PID>

# O matar todos los puertos AP2
lsof -ti:8000,8001,8002,8003 | xargs kill -9
```

### Variables de Entorno

Los scripts buscan `.env` en:
- `ap2-integration/.env` - Contiene `GOOGLE_API_KEY`

Si no existe, `setup.sh` creará uno desde `.env.example`.

## 🚀 Ejemplos de Uso

### Demo rápido (2 minutos)

```bash
# Setup (solo primera vez)
./scripts/setup.sh

# Iniciar todo
./scripts/run-ap2-agents.sh &  # En background
./scripts/run-shopping-agent.sh

# Abrir http://localhost:8000 y comprar un Pokemon
```

### Desarrollo del Shopping Agent

```bash
# Agentes AP2 corriendo
./scripts/run-ap2-agents.sh

# Editar código en ap2-integration/src/shopping_agent/
# Reiniciar solo el shopping agent:
# Ctrl+C y luego:
./scripts/run-shopping-agent.sh
```

### Testing completo

```bash
# Todos los agentes corriendo
./scripts/run-ap2-agents.sh &
./scripts/run-shopping-agent.sh &

# En otra terminal
./scripts/test-ap2-integration.sh

# O tests individuales
cd tests
python test_mcp.py
python test_mcp_simple.py
```

## 🐛 Troubleshooting

### Script no ejecutable

```bash
chmod +x scripts/*.sh
```

### Error: GOOGLE_API_KEY not found

```bash
# Crear .env manualmente
echo "GOOGLE_API_KEY=tu_api_key" > ap2-integration/.env
```

### MCP Server no compila

```bash
cd mcp-server
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Dependencias Python faltantes

```bash
cd ap2-integration
uv sync
# O reinstalar todo:
./scripts/setup.sh
```

---

**💡 Tip**: Para detener todos los procesos background iniciados por `run-ap2-agents.sh`, simplemente presiona `Ctrl+C` en esa terminal.

**Limpia:**
- `mcp-server/build/`
- `mcp-server/node_modules/`
- Todos los `__pycache__/`
- Archivos `.pyc`
- (Opcional) Archivos `.env`

## 📊 Flujos de Uso

### Primera vez (Setup completo)

```bash
# 1. Setup inicial
./scripts/setup.sh

# 2. Configurar API Keys
nano adk-agent/.env
nano ap2-integration/.env

# 3. Ejecutar demo completo
./scripts/run-ap2-demo.sh
```

### Desarrollo diario

```bash
# Opción 1: ADK Agent simple
./scripts/run-adk.sh

# Opción 2: Demo AP2 completo
./scripts/run-ap2-demo.sh

# Opción 3: Componentes separados (2 terminales)
# Terminal 1
./scripts/run-merchant.sh

# Terminal 2
./scripts/run-shopping.sh
```

### Limpieza

```bash
# Limpiar compilados y caches
./scripts/clean.sh

# Reinstalar desde cero
./scripts/clean.sh
./scripts/setup.sh
```

## 🎯 Casos de Uso

### Caso 1: Solo quiero probar el catálogo de Pokemon

```bash
./scripts/run-adk.sh
```

Luego pregunta cosas como:
- "¿Qué información tienes sobre Pikachu?"
- "Busca pokemon de tipo fire"
- "¿Cuánto cuesta Charizard?"

### Caso 2: Quiero hacer una compra completa con AP2

```bash
./scripts/run-ap2-demo.sh
```

Flujo de compra:
1. "I want to buy a Pikachu"
2. "Add it to my cart"
3. "Checkout"

### Caso 3: Desarrollo de AP2 (necesito ambos agentes)

```bash
# Terminal 1
./scripts/run-merchant.sh

# Terminal 2
./scripts/run-shopping.sh
```

## 🔧 Troubleshooting

### Error: Puerto ya en uso

Los scripts detectan automáticamente si los puertos están en uso y ofrecen matar el proceso.

Manualmente:
```bash
# Ver qué está usando el puerto
lsof -i :8000
lsof -i :8001

# Matar proceso
kill -9 <PID>
```

### Error: .env no encontrado

```bash
# Copiar desde .env.example
cp adk-agent/.env.example adk-agent/.env
cp ap2-integration/.env.example ap2-integration/.env

# Editar y añadir GOOGLE_API_KEY
nano adk-agent/.env
nano ap2-integration/.env
```

### Error: Dependencias no instaladas

```bash
./scripts/setup.sh
```

## 📝 Notas

- Todos los scripts verifican automáticamente las dependencias
- Los scripts usan rutas relativas (pueden ejecutarse desde cualquier ubicación)
- El demo AP2 hace cleanup automático al salir (Ctrl+C)
- Los archivos .env nunca se suben a Git (están en .gitignore)

## 🎨 Makefile Alternativo

También puedes usar el Makefile en lugar de los scripts:

```bash
# Ver todos los comandos
make help

# Setup
make setup

# Ejecutar componentes
make run-adk
make run-merchant
make run-shopping

# Limpieza
make clean
```

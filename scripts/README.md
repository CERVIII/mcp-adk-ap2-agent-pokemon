# 📜 Scripts de Gestión

Scripts centralizados para gestionar el proyecto Pokemon MCP + AP2 + ADK.

## 🚀 Scripts Disponibles

### Setup y Configuración

#### `setup.sh`
Setup completo del proyecto.

```bash
./scripts/setup.sh
```

**Funciones:**
- ✅ Verifica requisitos (Node.js, Python, uv)
- 📦 Instala dependencias de todos los componentes
- 🔨 Compila el MCP Server
- 🔑 Crea archivos .env desde .env.example

### Ejecución

#### `run-adk.sh`
Ejecuta el ADK Agent simple (conversacional básico).

```bash
./scripts/run-adk.sh
```

**Características:**
- Agente conversacional con Gemini
- Acceso a herramientas MCP
- Interfaz interactiva en terminal

#### `run-merchant.sh`
Ejecuta el Merchant Agent (AP2 - Puerto 8001).

```bash
./scripts/run-merchant.sh
```

**Características:**
- Servidor FastAPI en puerto 8001
- Endpoints de AP2 para carritos y pagos
- Agent Card en `.well-known/agent-card.json`

#### `run-shopping.sh`
Ejecuta el Shopping Agent (AP2 - Puerto 8000).

```bash
./scripts/run-shopping.sh
```

**Características:**
- Agente conversacional de compras
- Integración con Merchant Agent
- Flujo completo de compra con AP2

#### `run-ap2-demo.sh`
Demo completo de AP2 (Merchant + Shopping juntos).

```bash
./scripts/run-ap2-demo.sh
```

**Funciones:**
- 🚀 Inicia Merchant Agent en background
- 💬 Inicia Shopping Agent en foreground
- 🧹 Cleanup automático al salir (Ctrl+C)
- ✅ Verifica puertos antes de iniciar

### Utilidades

#### `clean.sh`
Limpia archivos compilados y caches.

```bash
./scripts/clean.sh
```

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

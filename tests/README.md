# 🧪 Tests y Scripts de Prueba

Esta carpeta contiene scripts de prueba para validar el funcionamiento del servidor MCP y la integración AP2.

## 📋 Archivos de Test

### `test_mcp.py` - Test Completo del Servidor MCP
Test exhaustivo del servidor MCP con todas las tools.

**Uso:**
```bash
python tests/test_mcp.py
```

**Prueba:**
- ✅ Conexión con el servidor MCP via stdio
- ✅ Todas las tools disponibles (6 tools)
- ✅ `get_pokemon_info` - Información desde PokeAPI
- ✅ `get_pokemon_price` - Precios e inventario local
- ✅ `search_pokemon` - Búsqueda con filtros
- ✅ `list_pokemon_types` - Listado de tipos
- ✅ `create_pokemon_cart` - CartMandate con JWT RS256
- ✅ `get_pokemon_product` - Producto completo
- ✅ Formato de respuestas JSON
- ✅ Manejo de errores

**Salida esperada:**
```
🚀 Testing MCP Pokemon Server
✅ Connected to MCP server
✅ Tool: get_pokemon_info
✅ Tool: get_pokemon_price
✅ Tool: search_pokemon
✅ Tool: list_pokemon_types
✅ Tool: create_pokemon_cart
✅ Tool: get_pokemon_product
✅ All tests passed!
```

### `test_mcp_simple.py` - Test Rápido
Test simplificado para validación rápida.

**Uso:**
```bash
python tests/test_mcp_simple.py
```

**Prueba:**
- ✅ Conexión básica con servidor MCP
- ✅ Tool `get_pokemon_info` con Pikachu
- ✅ Respuesta correcta en menos de 5 segundos

**Salida esperada:**
```
Testing MCP Pokemon Server (Simple)
✅ Connected successfully
✅ get_pokemon_info test passed
Test completed in 2.3s
```

### `test_unified_mcp.sh` - Script Bash Interactivo
Script bash completo para probar el servidor MCP end-to-end.

**Uso:**
```bash
chmod +x tests/test_unified_mcp.sh
./tests/test_unified_mcp.sh
```

**Realiza:**
1. ⚙️ Verifica dependencias (Node.js, npm)
2. 📦 Instala dependencias si es necesario
3. 🔨 Compila el servidor TypeScript
4. 🚀 Inicia el servidor MCP en modo stdio
5. 🧪 Lista todas las tools disponibles
6. ⏸️ Espera Ctrl+C para detener

**Ejemplo de uso:**
```bash
$ ./tests/test_unified_mcp.sh
Checking dependencies...
✅ Node.js found
✅ npm found
Installing dependencies...
✅ Dependencies installed
Building server...
✅ Server built
Starting MCP server...
✅ Server started on stdio
Tools available:
  - get_pokemon_info
  - get_pokemon_price
  - search_pokemon
  - list_pokemon_types
  - create_pokemon_cart
  - get_pokemon_product
Press Ctrl+C to stop
```

### `test_get_cart.py` - Test de CartMandate
Test específico para la creación de CartMandates con JWT.

**Uso:**
```bash
python tests/test_get_cart.py
```

**Prueba:**
- ✅ Creación de cart con `create_pokemon_cart`
- ✅ Estructura de CartMandate AP2
- ✅ merchant_signature (JWT RS256)
- ✅ payment_request completo
- ✅ displayItems correctos

## 🚀 Ejecutar Todos los Tests

### Opción 1: Tests individuales

```bash
# Test completo (recomendado)
python tests/test_mcp.py

# Test rápido
python tests/test_mcp_simple.py

# Test de CartMandate
python tests/test_get_cart.py

# Test bash interactivo
./tests/test_unified_mcp.sh
```

### Opción 2: Suite completa

```bash
# Ejecutar todos los tests Python
for test in tests/test_*.py; do
    echo "Running $test..."
    python "$test" || exit 1
done

echo "✅ All Python tests passed!"
```

## 📝 Requisitos

### Para tests Python

```bash
# Dependencias necesarias
pip install mcp python-dotenv

# O con uv
cd ap2-integration
uv sync
```

### Para test bash

```bash
# Solo necesitas Node.js y npm
node --version  # >= 18
npm --version
```

### MCP Server compilado

```bash
# Compilar antes de ejecutar tests
cd mcp-server
npm install
npm run build
```

## 🔍 Debugging Tests

### Si test_mcp.py falla

```bash
# 1. Verifica que el servidor esté compilado
cd mcp-server && npm run build

# 2. Verifica la ruta en el test
# El test busca: mcp-server/build/index.js

# 3. Ejecuta con más verbose
python -v tests/test_mcp.py
```

### Si test_unified_mcp.sh no ejecuta

```bash
# Dale permisos de ejecución
chmod +x tests/test_unified_mcp.sh

# Ejecuta directamente
bash tests/test_unified_mcp.sh
```

### Si los tests son lentos

El test completo puede tardar 10-15 segundos debido a:
- Conexión con PokeAPI (externa)
- Inicio del servidor MCP
- Múltiples llamadas a tools

Para tests más rápidos, usa `test_mcp_simple.py`.

## 📊 Cobertura de Tests

| Componente | Test | Cobertura |
|------------|------|-----------|
| MCP Connection | test_mcp.py | ✅ 100% |
| get_pokemon_info | test_mcp.py, test_mcp_simple.py | ✅ 100% |
| get_pokemon_price | test_mcp.py | ✅ 100% |
| search_pokemon | test_mcp.py | ✅ 100% |
| list_pokemon_types | test_mcp.py | ✅ 100% |
| create_pokemon_cart | test_mcp.py, test_get_cart.py | ✅ 100% |
| get_pokemon_product | test_mcp.py | ✅ 100% |
| JWT Signatures | test_get_cart.py | ⚠️ Partial |

## 🎯 Tests de Integración

Para tests de integración completa con AP2:

```bash
# Inicia todos los agentes
./scripts/run-ap2-agents.sh &

# Ejecuta tests de integración
./scripts/test-ap2-integration.sh

# O prueba la Web UI manualmente
./scripts/run-shopping-agent.sh
open http://localhost:8000
```

## 🔗 Ver También

- [README Principal](../README.md) - Documentación general
- [MCP Server README](../mcp-server/README.md) - Documentación del servidor MCP
- [AP2 Integration README](../ap2-integration/README.md) - Documentación de AP2
- [Scripts README](../scripts/README.md) - Scripts de automatización

---

**💡 Tip**: Para CI/CD, usa `test_mcp_simple.py` que es más rápido y no depende de APIs externas lentas.

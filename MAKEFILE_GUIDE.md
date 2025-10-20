# 🎯 Makefile Mejorado - Guía de Uso

El Makefile ahora es **completamente automático**. Solo necesitas ejecutar `make run` y él se encarga de todo! 🚀

## ⚡ Uso Rápido

### Primera Vez (Cero Configuración)

```bash
# Un solo comando hace todo:
make run
```

Esto automáticamente:
1. ✅ Verifica e instala dependencias de Node.js
2. ✅ Compila el MCP Server
3. ✅ Verifica e instala dependencias de Python
4. ✅ Crea archivos .env si no existen
5. ✅ Te pide configurar la API Key si falta
6. ✅ Ejecuta el demo completo (Merchant + Shopping)

### Configurar API Key Interactivamente

Si prefieres configurar la API Key primero:

```bash
make configure-api-key
```

Te pregunta tu Google API Key y la configura automáticamente en ambos archivos .env.

### Ver Estado del Proyecto

```bash
make status
```

Muestra:
- ✅ Estado de dependencias MCP Server
- ✅ Estado de compilación
- ✅ Estado de archivos .env
- ✅ Estado de dependencias Python
- ✅ Recomendaciones de qué ejecutar

## 📋 Comandos Principales

### Ejecución

| Comando | Descripción | Auto-configura |
|---------|-------------|----------------|
| `make run` | Demo completo AP2 | ✅ Sí |
| `make run-adk` | Solo ADK Agent | ✅ Sí |
| `make run-merchant` | Solo Merchant (8001) | ✅ Sí |
| `make run-shopping` | Solo Shopping (8000) | ✅ Sí |
| `make run-mcp` | Solo MCP Server | ✅ Sí |

### Configuración

| Comando | Descripción |
|---------|-------------|
| `make setup` | Instalar + compilar todo |
| `make install` | Instalar todas las dependencias |
| `make build` | Compilar componentes TypeScript |
| `make configure-api-key` | Configurar API Key interactivamente |

### Información

| Comando | Descripción |
|---------|-------------|
| `make status` | Ver estado completo del proyecto |
| `make check-env` | Verificar archivos .env |
| `make ports` | Ver puertos en uso |
| `make help` | Ver todos los comandos |

### Limpieza

| Comando | Descripción |
|---------|-------------|
| `make clean` | Limpiar compilados y caches |
| `make clean-mcp` | Limpiar solo MCP Server |
| `make clean-python` | Limpiar solo caches Python |
| `make fclean` | Limpiar TODO incluyendo .env |

## 🎮 Ejemplos de Uso

### Escenario 1: Primera Ejecución

```bash
# Clonar el repositorio
git clone <repo>
cd prueba-mcp-a2a-ap2

# ¡Un solo comando!
make run

# El Makefile te guiará para configurar la API Key
# Después ejecuta automáticamente el demo
```

### Escenario 2: Desarrollo Diario

```bash
# Ver qué necesita el proyecto
make status

# Ejecutar el demo
make run

# O ejecutar componente específico
make run-adk
```

### Escenario 3: Cambiar API Key

```bash
# Configurar nueva API Key
make configure-api-key

# Ejecutar
make run
```

### Escenario 4: Limpiar y Reinstalar

```bash
# Limpiar todo
make clean

# Reinstalar (automático con run)
make run

# O manualmente
make setup
```

### Escenario 5: Verificar Estado

```bash
# Ver estado detallado
make status

# Verificar solo .env
make check-env

# Ver puertos
make ports
```

## 🔧 Verificaciones Automáticas

El Makefile hace estas verificaciones antes de ejecutar:

### Para MCP Server
- ✅ Verifica si `node_modules/` existe → Si no, ejecuta `npm install`
- ✅ Verifica si `build/` existe → Si no, ejecuta `npm run build`

### Para ADK Agent
- ✅ Verifica si `.env` existe → Si no, lo crea desde `.env.example`
- ✅ Verifica si Google Generative AI está instalado → Si no, ejecuta `uv pip install`
- ✅ Verifica si API Key está configurada → Si no, te pide que la configures

### Para AP2 Integration
- ✅ Verifica si `.env` existe → Si no, lo crea desde `.env.example`
- ✅ Verifica si FastAPI está instalado → Si no, ejecuta `uv pip install`
- ✅ Verifica si API Key está configurada → Si no, te pide que la configures

## 🎯 Flujo Interno de `make run`

```
make run
    ↓
ensure-ready
    ↓
    ├─ ensure-mcp-ready
    │   ├─ ¿node_modules existe? → No → make install-mcp
    │   └─ ¿build existe? → No → make build-mcp
    │
    ├─ ensure-env-adk
    │   └─ ¿.env existe? → No → Crear desde .env.example + pedir configurar
    │
    ├─ ensure-env-ap2
    │   └─ ¿.env existe? → No → Crear desde .env.example + pedir configurar
    │
    ├─ ensure-deps-adk
    │   └─ ¿google.generativeai instalado? → No → make install-adk
    │
    └─ ensure-deps-ap2
        └─ ¿fastapi instalado? → No → make install-ap2
    ↓
run-demo
    └─ ./scripts/run-ap2-demo.sh
```

## 💡 Consejos

### 1. Usa `make status` frecuentemente
Te dice exactamente qué necesitas hacer.

### 2. `make run` es inteligente
No necesitas ejecutar `make setup` primero. `make run` lo hace automáticamente si es necesario.

### 3. Configuración de API Key
Tienes 2 opciones:
- **Automática**: `make run` te la pide cuando la necesitas
- **Manual**: `make configure-api-key` para configurarla antes

### 4. Limpieza segura
- `make clean` → Limpia compilados (seguro)
- `make fclean` → Limpia TODO incluyendo .env (¡cuidado!)

### 5. Componentes individuales
Todos los comandos `run-*` auto-configuran antes de ejecutar:
```bash
make run-adk       # Auto-configura y ejecuta ADK
make run-merchant  # Auto-configura y ejecuta Merchant
make run-shopping  # Auto-configura y ejecuta Shopping
```

## 🐛 Troubleshooting

### "Error: GOOGLE_API_KEY no configurada"

```bash
# Opción 1: Interactivo
make configure-api-key

# Opción 2: Manual
nano adk-agent/.env
nano ap2-integration/.env
```

### "Puerto 8000/8001 ya en uso"

```bash
# Ver qué está usando el puerto
make ports

# Los scripts manejan esto automáticamente
make run
```

### "Dependencias no instaladas"

```bash
# El Makefile las instala automáticamente
make run

# O manualmente
make install
```

### "MCP Server no compila"

```bash
# Limpiar y recompilar
make clean
make build-mcp

# O automático
make run
```

## 🚀 Mejoras del Nuevo Makefile

| Antes | Ahora |
|-------|-------|
| Manual: `./scripts/setup.sh` | Automático con `make run` |
| 5 pasos para configurar | 1 comando |
| Editar .env manualmente | `make configure-api-key` |
| No sabe qué falta | `make status` te lo dice |
| Cada componente separado | Todo integrado |

## 📚 Documentación Relacionada

- **README.md** - Documentación completa del proyecto
- **QUICKSTART.md** - Guía de inicio rápido
- **PROJECT_STRUCTURE.md** - Estructura del proyecto
- **scripts/README.md** - Documentación de scripts

---

**TL;DR**: Solo ejecuta `make run` y disfruta! 🎮

# QUICKSTART.md - Guía Rápida

Este archivo te ayudará a empezar en **menos de 5 minutos**! 🚀

## ⚡ Setup Ultra-Rápido (Recomendado)

### Opción 1: Makefile Automático (¡1 comando!)

```bash
# Un solo comando hace TODO:
make run
```

Esto automáticamente:
- ✅ Instala dependencias
- ✅ Compila el MCP Server
- ✅ Crea archivos .env
- ✅ Te pide configurar la API Key
- ✅ Ejecuta el demo completo

**¿Dónde consigo la API Key?**
→ https://aistudio.google.com/apikey

### Opción 2: Scripts (Manual)

```bash
# 1. Ejecutar script de setup
./scripts/setup.sh

# 2. Configurar API Key
nano adk-agent/.env          # Pega tu GOOGLE_API_KEY
nano ap2-integration/.env    # Pega tu GOOGLE_API_KEY

# 3. Ejecutar demo
./scripts/run-ap2-demo.sh
```

## 🎮 Opciones de Ejecución

### Opción 1: ADK Agent Simple
Agente conversacional básico para consultar Pokemon.

```bash
./scripts/run-adk.sh
```

**Prueba:**
- "¿Qué información tienes sobre Pikachu?"
- "Busca pokemon de tipo fire por menos de 100 USD"
- "¿Cuánto cuesta Charizard?"

### Opción 2: Demo AP2 Completo (Recomendado)
Merchant + Shopping Agent con flujo de compra completo.

```bash
./scripts/run-ap2-demo.sh
```

**Flujo de compra:**
1. "I want to buy a Pikachu"
2. "Add it to my cart"
3. "Checkout"

### Opción 3: Componentes Separados
Para desarrollo, ejecuta en 2 terminales:

```bash
# Terminal 1: Merchant Agent
./scripts/run-merchant.sh

# Terminal 2: Shopping Agent
./scripts/run-shopping.sh
```

## 📚 Comandos Útiles

### Usando Makefile (Recomendado - Automático)

```bash
make run           # 🚀 Ejecutar demo (auto-configura TODO)
make run-adk       # ADK Agent (auto-configura)
make run-merchant  # Merchant (auto-configura)
make run-shopping  # Shopping (auto-configura)
make status        # Ver estado del proyecto
make configure-api-key  # Configurar API Key interactivamente
make clean         # Limpiar compilados
make help          # Ver todos los comandos
```

### Usando Scripts (Alternativo)

```bash
./scripts/setup.sh          # Setup completo
./scripts/run-adk.sh        # ADK Agent
./scripts/run-merchant.sh   # Merchant (Puerto 8001)
./scripts/run-shopping.sh   # Shopping (Puerto 8000)
./scripts/run-ap2-demo.sh   # Demo completo
./scripts/clean.sh          # Limpiar proyecto
```

### ¿Cuál usar?

- **Makefile**: Mejor para desarrollo, auto-configura todo
- **Scripts**: Mejor para CI/CD o ejecución manual controlada

## 🐛 Problemas Comunes

### Error: "GOOGLE_API_KEY no configurada"

```bash
# Crear archivos .env desde .env.example
cp adk-agent/.env.example adk-agent/.env
cp ap2-integration/.env.example ap2-integration/.env

# Editar y añadir tu API Key
nano adk-agent/.env
nano ap2-integration/.env
```

### Error: "Puerto 8000/8001 ya en uso"

```bash
# Opción 1: Los scripts te preguntarán si quieres matar el proceso

# Opción 2: Manual
lsof -ti:8000 | xargs kill -9
lsof -ti:8001 | xargs kill -9
```

### Error: "Dependencias no instaladas"

```bash
# Reinstalar todo
./scripts/clean.sh
./scripts/setup.sh
```

## 📖 Más Información

- **README principal**: Documentación completa del proyecto
- **mcp-server/README.md**: Documentación del MCP Server
- **ap2-integration/README.md**: Documentación de AP2
- **adk-agent/README.md**: Documentación del ADK Agent
- **scripts/README.md**: Documentación de scripts

## 🎯 Próximos Pasos

1. ✅ Ejecuta el demo completo: `./scripts/run-ap2-demo.sh`
2. 📖 Lee el README principal para entender la arquitectura
3. 🧪 Explora los componentes individualmente
4. 🚀 Modifica y experimenta!

---

**¿Problemas?** Revisa el [README principal](README.md) o la [documentación de scripts](scripts/README.md).

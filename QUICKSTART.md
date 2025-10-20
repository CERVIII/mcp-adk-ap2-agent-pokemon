# QUICKSTART.md - Guía Rápida

Este archivo te ayudará a empezar en **menos de 5 minutos**! 🚀

## ⚡ Setup Rápido

### 1️⃣ Requisitos

```bash
# Verificar que tienes todo instalado
node --version   # Debe ser 18+
python3 --version # Debe ser 3.10+
uv --version     # Si no lo tienes: curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2️⃣ Setup Automático

```bash
# Ejecutar script de setup
./scripts/setup.sh

# Configurar API Key
nano adk-agent/.env          # Pega tu GOOGLE_API_KEY
nano ap2-integration/.env    # Pega tu GOOGLE_API_KEY
```

**¿Dónde consigo la API Key?**
→ https://aistudio.google.com/apikey

### 3️⃣ ¡Ejecutar!

```bash
# Demo completo de compra Pokemon con AP2
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

### Usando Scripts

```bash
./scripts/setup.sh          # Setup completo
./scripts/run-adk.sh        # ADK Agent
./scripts/run-merchant.sh   # Merchant (Puerto 8001)
./scripts/run-shopping.sh   # Shopping (Puerto 8000)
./scripts/run-ap2-demo.sh   # Demo completo
./scripts/clean.sh          # Limpiar proyecto
```

### Usando Makefile

```bash
make help          # Ver todos los comandos
make setup         # Setup completo
make status        # Ver estado del proyecto
make ports         # Ver puertos en uso
make clean         # Limpiar compilados
```

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

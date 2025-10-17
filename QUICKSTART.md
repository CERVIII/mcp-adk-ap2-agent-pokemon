# 🚀 GUÍA DE INICIO RÁPIDO

Esta guía te llevará paso a paso para ejecutar el proyecto completo.

## ⚠️ PASO PREVIO CRÍTICO: Configurar Google API Key

Antes de ejecutar cualquier cosa, **DEBES** configurar tu Google API Key:

### 1. Obtener la API Key

1. Ve a [Google AI Studio](https://aistudio.google.com/apikey)
2. Inicia sesión con tu cuenta de Google
3. Crea una nueva API Key
4. **Copia la clave** (la necesitarás en el siguiente paso)

### 2. Configurar en el proyecto

```bash
# Navega al directorio del proyecto
cd /home/idb0181/Escritorio/prueba-mcp-a2a-ap2

# Crear archivo .env para ADK Agent
echo "GOOGLE_API_KEY=TU_API_KEY_AQUI" > adk-agent/.env

# Crear archivo .env para AP2 Integration
cat > ap2-integration/.env << 'EOF'
GOOGLE_API_KEY=TU_API_KEY_AQUI
MERCHANT_AGENT_PORT=8001
SHOPPING_AGENT_PORT=8000
EOF
```

**🔴 IMPORTANTE**: Reemplaza `TU_API_KEY_AQUI` con tu API key real.

---

## 🎯 ESCENARIOS DE USO

Elige el escenario que quieres probar:

### Escenario A: Agente Simple con MCP
**Qué hace**: Agente básico que consulta información de Pokemon usando el MCP server

### Escenario B: Marketplace con AP2 (RECOMENDADO)
**Qué hace**: Sistema completo de compras con Shopping Agent y Merchant Agent usando AP2

---

## 🎮 ESCENARIO A: Agente Simple con MCP

### Terminal Única

```bash
cd /home/idb0181/Escritorio/prueba-mcp-a2a-ap2/adk-agent

# Asegúrate de que el .env existe con tu API key
cat .env

# Ejecutar el agente
python pokemon_agent.py
```

### Interacción de Ejemplo

```
💬 Escribe tu pregunta:

Tú: ¿Qué información tienes sobre Pikachu?

🤖 Pokemon Agent: Pikachu es un Pokemon de tipo eléctrico. 
Tiene las siguientes características:
- Altura: 4 decímetros
- Peso: 60 hectogramos
- Habilidades: static, lightning-rod
[...]

Tú: ¿Cuál es el precio de Charizard?

🤖 Pokemon Agent: Según el catálogo, Charizard cuesta $180 USD 
y tiene 8 unidades disponibles en inventario.

Tú: exit
👋 ¡Hasta luego!
```

---

## 🏪 ESCENARIO B: Marketplace con AP2 (RECOMENDADO)

Este es el escenario completo que demuestra el protocolo AP2.

### Opción 1: Script Automático (Más Fácil)

```bash
cd /home/idb0181/Escritorio/prueba-mcp-a2a-ap2

# Ejecutar script de inicio
./start_ap2_demo.sh
```

Esto iniciará ambos agentes automáticamente. **NOTA**: El Shopping Agent se ejecuta en modo interactivo en tu terminal, mientras que el Merchant Agent corre en background.

### Opción 2: Terminales Separadas (Más Control)

#### Terminal 1: Merchant Agent

```bash
cd /home/idb0181/Escritorio/prueba-mcp-a2a-ap2/ap2-integration

# Verificar .env
cat .env

# Iniciar Merchant Agent
python -m src.roles.merchant_agent
```

**Salida esperada**:
```
🏪 Starting Pokemon Merchant Agent on port 8001...
📋 Agent Card: http://localhost:8001/.well-known/agent-card.json
🔍 Catalog: http://localhost:8001/catalog
INFO:     Started server process [12345]
INFO:     Uvicorn running on http://127.0.0.1:8001
```

#### Terminal 2: Shopping Agent

```bash
cd /home/idb0181/Escritorio/prueba-mcp-a2a-ap2/ap2-integration

# Iniciar Shopping Agent
python -m src.roles.shopping_agent
```

**Salida esperada**:
```
🛍️  Starting Pokemon Shopping Assistant with AP2...
============================================================

⚠️  Make sure the Merchant Agent is running on port 8001
    
============================================================

✅ Shopping Assistant ready!

Example shopping flows:
  1. 'I want to buy a Pikachu'
  2. 'Show me fire Pokemon under $150'
  3. 'Add Charizard and Blastoise to my cart'
  4. 'Proceed to checkout'

============================================================

💬 What can I help you with? (or 'exit' to quit)

You: 
```

### Flujo de Compra Completo

Una vez ambos agentes estén corriendo, prueba este flujo:

```
You: I want to buy a Pikachu

🤖 Assistant: Let me search for Pikachu in our catalog...
[El agente busca y muestra información]

You: Add it to my cart

🤖 Assistant: 🛒 Shopping Cart Created!
Cart ID: cart_a1b2c3d4
Items:
  • Pikachu x1 - $250 each = $250 total

Total: $250 USD
Ready for checkout!

You: Show me payment methods

🤖 Assistant: 💳 Available Payment Methods:
  1. Visa ending in 4242
  2. Mastercard ending in 5555

You: Proceed to checkout

🤖 Assistant: ✅ Payment Successful!
Transaction ID: txn_x9y8z7w6
Status: SUCCESS
Message: Successfully purchased 1 Pokemon for $250.00 USD
Total Paid: $250 USD

You: exit
👋 Thanks for shopping! Goodbye!
```

---

## 🧪 VERIFICACIÓN Y TESTING

### Verificar MCP Server (Opcional)

```bash
cd mcp-server
npm run build
# Si compila sin errores, el MCP server está listo
```

### Verificar Merchant Agent API

Con el Merchant Agent corriendo:

```bash
# Ver catálogo completo
curl http://localhost:8001/catalog

# Ver Agent Card (A2A protocol)
curl http://localhost:8001/.well-known/agent-card.json

# Buscar Pokemon
curl -X POST http://localhost:8001/catalog/search \
  -H "Content-Type: application/json" \
  -d '{"query": "pikachu"}'

# Crear un carrito
curl -X POST http://localhost:8001/cart/create \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"pokemon": "pikachu", "quantity": 1},
      {"pokemon": "charizard", "quantity": 1}
    ]
  }'
```

---

## 🐛 TROUBLESHOOTING

### Error: "GOOGLE_API_KEY not configured"

**Solución**:
```bash
# Verificar que existe el archivo .env
ls -la ap2-integration/.env
ls -la adk-agent/.env

# Si no existe, crearlo
echo "GOOGLE_API_KEY=TU_CLAVE_AQUI" > ap2-integration/.env
echo "GOOGLE_API_KEY=TU_CLAVE_AQUI" > adk-agent/.env
```

### Error: "Connection refused" al conectar con Merchant Agent

**Causa**: El Merchant Agent no está corriendo o no inició correctamente.

**Solución**:
```bash
# Verificar si el puerto 8001 está en uso
lsof -i :8001

# Verificar logs (si usaste el script)
cat logs/merchant_agent.log

# Reiniciar el Merchant Agent
cd ap2-integration
python -m src.roles.merchant_agent
```

### Error: "No module named 'google.adk'"

**Causa**: Dependencias no instaladas.

**Solución**:
```bash
cd ap2-integration
uv pip install google-adk python-dotenv fastapi uvicorn pydantic requests
```

### Puerto 8000 o 8001 ya en uso

**Solución**:
```bash
# Encontrar el proceso
lsof -i :8001
lsof -i :8000

# Matar el proceso (reemplaza PID con el número que aparece)
kill -9 <PID>
```

### Pokemon no encontrado

**Causa**: Solo Pokemon de Gen 1 (1-151) están en el catálogo.

**Solución**: Usa Pokemon de la primera generación:
- Pikachu, Charizard, Blastoise, Venusaur, etc.
- Números del 1 al 151

---

## 📊 LOGS Y DEBUGGING

### Logs del Merchant Agent
```bash
tail -f logs/merchant_agent.log
```

### Logs del Shopping Agent
```bash
tail -f logs/shopping_agent.log
```

### Ver estado de los servicios
```bash
# Ver procesos Python corriendo
ps aux | grep python

# Ver puertos en uso
lsof -i :8000
lsof -i :8001
```

---

## ✅ CHECKLIST DE INICIO

Antes de ejecutar, verifica:

- [ ] Python 3.10+ instalado (`python3 --version`)
- [ ] uv instalado (`uv --version`)
- [ ] Node.js instalado (`node --version`)
- [ ] Google API Key obtenida
- [ ] Archivos `.env` creados con API key
- [ ] MCP Server compilado (`cd mcp-server && npm run build`)
- [ ] Dependencias instaladas en ap2-integration

---

## 🎓 APRENDIENDO

### Conceptos AP2 en Acción

Mientras usas el Shopping Agent, observa estos conceptos de AP2:

1. **CartMandate**: Cuando creas un carrito, verás el CartMandate con items y precios exactos
2. **PaymentMandate**: Al hacer checkout, se crea un PaymentMandate con método de pago
3. **Transaction Receipt**: Después del pago, recibes un recibo con ID de transacción

### Archivos Clave para Aprender

- `ap2-integration/src/common/ap2_types.py` - Tipos de datos del protocolo
- `ap2-integration/src/roles/merchant_agent.py` - Lado del merchant
- `ap2-integration/src/roles/shopping_agent.py` - Lado del shopping agent

---

## 📞 AYUDA ADICIONAL

Para más información, consulta:

- **README principal**: `/README.md`
- **Docs MCP**: `mcp-server/README.md`
- **Docs ADK**: `adk-agent/README.md`
- **Docs AP2**: `ap2-integration/README.md`
- **AP2 Specification**: https://ap2-protocol.net/

---

## 🚀 SIGUIENTE PASO

**Una vez que hayas configurado tu API key**, ejecuta:

```bash
# Para el escenario simple
cd adk-agent && python pokemon_agent.py

# O para el marketplace completo (RECOMENDADO)
./start_ap2_demo.sh
```

¡Disfruta explorando MCP, ADK y AP2! 🎮

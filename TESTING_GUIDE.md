# Guía de Pruebas del Sistema AP2 + MCP + ADK

## 📋 Estado Actual

### ✅ Componentes Completados

1. **MCP Server** (TypeScript)
   - 4 herramientas Pokemon funcionando
   - Integración con PokeAPI
   - Compilado y listo para usar

2. **Merchant Agent** (FastAPI)
   - ✅ Corriendo en puerto 8001 (PID: 418525)
   - Endpoints AP2 funcionando:
     - `/catalog` - Catálogo completo
     - `/catalog/search` - Búsqueda con filtros (nombre, tipo, precio)
     - `/cart/create` - Crear CartMandate
     - `/payment/process` - Procesar PaymentMandate
   - Agent Card en `/.well-known/agent-card.json`

3. **Shopping Agent** (Gemini + google.generativeai)
   - ✅ Herramientas configuradas con function calling
   - ✅ Búsqueda por tipo implementada
   - ⚠️ **Cuota de API excedida** (50 requests/día en tier gratuito)

### 🔧 Funcionalidades Implementadas

#### Búsqueda de Pokemon
- ✅ Por nombre: "busca pikachu"
- ✅ Por tipo: "muéstrame pokemon de tipo Fire" / "pokemon tipo Agua"
- ✅ Por precio: "pokemon de menos de $100"
- ✅ Combinado: "pokemon tipo Fire de menos de $200"

#### Carrito de Compras (AP2 CartMandate)
- ✅ Crear carrito con items
- ✅ Validación de inventario
- ✅ Cálculo de totales
- ✅ Persistencia temporal

#### Pagos (AP2 PaymentMandate)
- ✅ Procesamiento de pagos
- ✅ TransactionReceipt con detalles
- ✅ Métodos: credit_card, agent_balance, crypto

## 🚀 Cómo Probar el Sistema

### Prerequisitos

1. **Cuota de API de Gemini disponible**
   ```bash
   # Tu cuota se reseteará aproximadamente:
   # Tiempo de espera: ~50 minutos desde el último error
   ```

2. **Merchant Agent corriendo**
   ```bash
   # Verificar si está corriendo
   ps aux | grep merchant_agent
   
   # Si no está corriendo, iniciarlo:
   cd /home/idb0181/Escritorio/prueba-mcp-a2a-ap2/ap2-integration
   PYTHONPATH=/home/idb0181/Escritorio/prueba-mcp-a2a-ap2/ap2-integration \
   python3 /home/idb0181/Escritorio/prueba-mcp-a2a-ap2/ap2-integration/src/roles/merchant_agent.py
   ```

### Iniciar Shopping Agent

```bash
cd /home/idb0181/Escritorio/prueba-mcp-a2a-ap2/ap2-integration

PYTHONPATH=/home/idb0181/Escritorio/prueba-mcp-a2a-ap2/ap2-integration \
python3 /home/idb0181/Escritorio/prueba-mcp-a2a-ap2/ap2-integration/src/roles/shopping_agent.py
```

## 🎯 Flujos de Prueba Recomendados

### 1. Búsqueda por Tipo (NUEVO - SOLUCIONADO)

```
You: muéstrame todos los pokemon de tipo Fire
🤖: [Buscará y mostrará Charmander, Charmeleon, Charizard, Vulpix, Ninetales, Growlithe, Arcanine, Ponyta, Rapidash, Moltres]

You: quiero ver pokemon de tipo Water
🤖: [Mostrará Squirtle, Wartortle, Blastoise, Psyduck, Golduck, Poliwag, etc.]

You: pokemon tipo Psychic de menos de $200
🤖: [Filtrará por tipo Psychic Y precio máximo]
```

### 2. Compra Simple

```
You: quiero comprar un Pikachu
🤖: [Buscará Pikachu]
🤖: Pikachu cuesta $X. ¿Cuántos quieres?

You: 1
🤖: [Creará CartMandate]
🤖: Tu carrito tiene 1 Pikachu por $X. ¿Quieres pagar?

You: sí, pagar
🤖: [Procesará PaymentMandate]
🤖: ✅ Pago completado! Transaction ID: xxx-xxx
```

### 3. Compra Múltiple con Tipos

```
You: necesito 2 pokemon de tipo Fire
🤖: [Mostrará todos los Fire type]

You: quiero un Charizard y un Arcanine
🤖: [Creará carrito con ambos]

You: agregar también un Blastoise
🤖: [Actualizará carrito]

You: proceder al pago
🤖: [Procesará payment]
```

### 4. Exploración del Catálogo

```
You: muéstrame pokemon caros
🤖: ¿Qué precio consideras caro?

You: más de $400
🤖: [Buscará con precio mínimo $400]

You: ahora muéstrame baratos de tipo Grass
🤖: [Combinará tipo Grass con precio bajo]
```

## 🔍 Verificar el Protocolo AP2

### Ver CartMandate Creado

```bash
# El Shopping Agent mostrará algo como:
CartMandate ID: cart_abc123
Items:
  - Pikachu x1: $150.00
Total: $150.00
Currency: USD
```

### Ver TransactionReceipt

```bash
# Después del pago verás:
✅ Payment Successful!
Transaction ID: txn_xyz789
Amount: $150.00
Method: credit_card
Timestamp: 2025-10-17T13:30:00
```

### Inspeccionar con cURL

```bash
# Ver el catálogo directamente
curl http://localhost:8001/catalog | jq

# Buscar por tipo
curl -X POST http://localhost:8001/catalog/search \
  -H "Content-Type: application/json" \
  -d '{"type": "Fire"}' | jq

# Ver Agent Card
curl http://localhost:8001/.well-known/agent-card.json | jq
```

## 📊 Tipos de Pokemon Disponibles

Los tipos disponibles en la Gen 1 son:
- **Normal** (Pidgey, Rattata, Meowth, etc.)
- **Fire** (Charmander, Vulpix, Growlithe, Ponyta, Moltres)
- **Water** (Squirtle, Psyduck, Poliwag, Tentacool, etc.)
- **Electric** (Pikachu, Raichu, Magnemite, Voltorb, Zapdos)
- **Grass** (Bulbasaur, Oddish, Bellsprout, Exeggcute, etc.)
- **Ice** (Dewgong, Cloyster, Jynx, Articuno)
- **Fighting** (Mankey, Machop, Hitmonlee, Hitmonchan)
- **Poison** (Weedle, Ekans, Nidoran, Grimer, etc.)
- **Ground** (Sandshrew, Diglett, Geodude, Onix, etc.)
- **Flying** (Pidgey, Spearow, Zubat, Farfetch'd, etc.)
- **Psychic** (Abra, Slowpoke, Drowzee, Mr. Mime, Mewtwo)
- **Bug** (Caterpie, Weedle, Paras, Venonat, Scyther)
- **Rock** (Geodude, Onix, Rhyhorn, Omanyte, Kabuto)
- **Ghost** (Gastly, Haunter, Gengar)
- **Dragon** (Dratini, Dragonair, Dragonite)

## 🐛 Solución de Problemas

### Error: Quota Exceeded

```
Error: 429 You exceeded your current quota
```

**Solución**: Espera ~1 hora para que se resetee la cuota del tier gratuito.

### Error: Merchant Agent no responde

```bash
# Verificar si está corriendo
curl http://localhost:8001/

# Si no responde, reiniciar:
pkill -f merchant_agent
cd ap2-integration
PYTHONPATH=. python3 src/roles/merchant_agent.py &
```

### Error: No encuentra Pokemon por tipo

Ahora ESTÁ SOLUCIONADO. El Shopping Agent ahora usa el parámetro `pokemon_type` correctamente.

## 📝 Notas Importantes

1. **API Key**: Configurada en `/home/idb0181/Escritorio/prueba-mcp-a2a-ap2/ap2-integration/.env`
2. **Límite de Cuota**: 50 requests/día en tier gratuito de Gemini
3. **Merchant Agent**: Debe estar corriendo antes de iniciar Shopping Agent
4. **Pokemon Data**: 151 Pokemon de Gen 1 en `pokemon-gen1.json`

## 🎓 Conceptos AP2 Implementados

### CartMandate
Representa una solicitud de carrito con items específicos y precios exactos que el usuario autoriza.

```json
{
  "cart_id": "cart_123",
  "items": [...],
  "total_amount": 150.00,
  "currency": "USD"
}
```

### PaymentMandate
Autorización de pago para un CartMandate específico.

```json
{
  "payment_id": "pay_456",
  "cart_id": "cart_123",
  "amount": 150.00,
  "payment_method": "credit_card"
}
```

### TransactionReceipt
Recibo de una transacción completada.

```json
{
  "transaction_id": "txn_789",
  "payment_id": "pay_456",
  "status": "completed",
  "timestamp": "2025-10-17T13:30:00"
}
```

---

**¡Todo está listo! Solo necesitas esperar a que se resetee la cuota de la API de Gemini para probarlo! 🚀**

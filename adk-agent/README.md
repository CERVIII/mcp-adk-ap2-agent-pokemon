# Pokemon Agent con Google ADK# 🤖 Shopping Agent con Google ADK# Pokemon Agent con Google ADK



Agente de IA construido con Google Agent Development Kit (ADK) que usa Gemini 2.5 Flash y se conecta con el MCP Server de Pokemon para acceder a información y precios de Pokemon.



## 🎯 CaracterísticasAgente conversacional desarrollado con **Google ADK (Agent Development Kit)** y **Gemini** para compras de Pokemon.Agente de IA construido con Google Agent Development Kit (ADK) que usa Gemini 2.5 Flash y se conecta con el MCP Server de Pokemon para acceder a información y precios de Pokemon.



- **Modelo**: Gemini 2.5 Flash (Google)

- **Framework**: Google ADK (Agent Development Kit)

- **Herramientas**: Integración con MCP Server de Pokemon## 🎯 Descripción## 🎯 Características

- **Interacción**: CLI interactiva



### Capacidades del Agente

El Shopping Agent es un asistente conversacional que:- **Modelo**: Gemini 2.5 Flash (Google)

El agente puede:

- 🔍 Buscar información detallada sobre cualquier Pokemon- Interpreta lenguaje natural- **Framework**: Google ADK (Agent Development Kit)

- 💰 Consultar precios e inventario de Pokemon Gen 1

- 🎯 Buscar Pokemon por tipo, precio y disponibilidad- Busca Pokemon en el catálogo- **Herramientas**: Integración con MCP Server de Pokemon

- 💡 Recomendar Pokemon según preferencias del usuario

- Gestiona carritos de compra- **Interacción**: CLI interactiva

## 📋 Requisitos Previos

- Procesa pagos via AP2

1. Python 3.10 o superior

2. `uv` package manager instalado### Capacidades del Agente

3. MCP Server compilado y funcionando

4. Google API Key de AI Studio## 🧠 Tecnología



## 🔧 ConfiguraciónEl agente puede:



### 1. Instalar dependencias- **LLM**: Gemini 2.0 Flash (gemini-2.0-flash-exp)- 🔍 Buscar información detallada sobre cualquier Pokemon



```bash- **Framework**: Google Generative AI Python SDK- 💰 Consultar precios e inventario de Pokemon Gen 1

cd adk-agent

uv sync- **Function Calling**: Herramientas personalizadas- 🎯 Buscar Pokemon por tipo, precio y disponibilidad

```

- **Protocolo**: Integración con AP2 para pagos- 💡 Recomendar Pokemon según preferencias del usuario

### 2. Configurar variables de entorno



Crea un archivo `.env` basado en `.env.example`:

## 🛠️ Herramientas del Agente## 📋 Requisitos Previos

```bash

cp .env.example .env

```

### 1. `search_pokemon`1. Python 3.10 o superior

Edita el archivo `.env` y añade tu Google API Key:

Busca Pokemon en el catálogo con filtros:2. `uv` package manager instalado

```env

GOOGLE_API_KEY=tu_api_key_aqui- Por nombre: "busca pikachu"3. MCP Server compilado y funcionando

```

- Por tipo: "muéstrame pokemon de tipo Fire"4. Google API Key de AI Studio

**Obtener API Key:**

- Visita: https://aistudio.google.com/apikey- Por precio: "pokemon de menos de $100"

- Crea una nueva API key

- Cópiala al archivo `.env`## 🔧 Configuración



### 3. Verificar MCP Server### 2. `view_cart`



Asegúrate de que el MCP Server esté compilado:Muestra el contenido del carrito actual con:### 1. Instalar dependencias



```bash- Items y cantidades

cd ../mcp-server

npm run build- Precios individuales```bash

```

- Total a pagarcd adk-agent

## 🚀 Ejecución

uv sync

```bash

# Desde el directorio adk-agent### 3. `create_shopping_cart````

uv run python pokemon_agent.py

```Crea un carrito con items seleccionados.



O si prefieres usar el entorno virtual:Genera un CartMandate (AP2).### 2. Configurar variables de entorno



```bash

# Activar entorno

source .venv/bin/activate  # Linux/Mac### 4. `list_payment_methods`Crea un archivo `.env` basado en `.env.example`:

# o

.venv\Scripts\activate  # WindowsLista métodos de pago disponibles:



# Ejecutar- credit_card```bash

python pokemon_agent.py

```- agent_balancecp .env.example .env



## 💬 Ejemplos de Uso- crypto```



Una vez iniciado el agente, puedes hacer preguntas como:



```### 5. `checkout`Edita el archivo `.env` y añade tu Google API Key:

Tú: ¿Qué información tienes sobre Pikachu?

🤖 Pokemon Agent: Pikachu es un Pokemon de tipo eléctrico...Completa la compra:



Tú: ¿Cuál es el precio de Charizard?- Crea PaymentMandate```env

🤖 Pokemon Agent: Charizard tiene un precio de $51 USD...

- Procesa pago via Merchant AgentGOOGLE_API_KEY=tu_api_key_aqui

Tú: Muéstrame Pokemon de tipo fuego con precio menor a $150

🤖 Pokemon Agent: Aquí están los Pokemon de tipo fuego disponibles...- Retorna TransactionReceipt```



Tú: ¿Qué Pokemon están en stock ahora?

🤖 Pokemon Agent: Los siguientes Pokemon están disponibles...

```## 🚀 Instalación**Obtener API Key:**



## 🏗️ Arquitectura- Visita: https://aistudio.google.com/apikey



``````bash- Crea una nueva API key

Usuario

  ↓pip install --user google-generativeai requests python-dotenv- Cópiala al archivo `.env`

Pokemon Agent (ADK + Gemini 2.5)

  ↓```

MCP Tools (4 herramientas)

  ↓### 3. Verificar MCP Server

┌─────────────────────┬──────────────────────┐

│   PokeAPI           │  pokemon-gen1.json   │## ⚙️ Configuración

│   (API externa)     │  (datos locales)     │

└─────────────────────┴──────────────────────┘Asegúrate de que el MCP Server esté compilado:

```

Crear archivo `.env` en `ap2-integration/`:

### Flujo de Datos

```bash

1. **Usuario** hace una pregunta al agente

2. **Agente ADK** procesa la pregunta con Gemini 2.5```bashcd ../mcp-server

3. **Gemini** decide qué herramientas MCP usar

4. **MCP Server** ejecuta las herramientas necesarias:GOOGLE_API_KEY=tu_api_key_aquinpm run build

   - Consulta PokeAPI para información del Pokemon

   - Lee pokemon-gen1.json para preciosMERCHANT_AGENT_PORT=8001```

5. **Agente** recibe los datos y genera respuesta

6. **Usuario** recibe la respuesta formateada```



## 🔌 Integración con MCP## 🚀 Ejecución



El agente se conecta al MCP Server usando `MCPTool.from_server()`:## 🧪 Ejecución



```python```bash

mcp_tools = MCPTool.from_server(

    command="node",```bash# Desde el directorio adk-agent

    args=[mcp_server_path],

    env={}cd ap2-integrationuv run python pokemon_agent.py

)

```PYTHONPATH=. python3 src/roles/shopping_agent.py```



Esto le da acceso a las 4 herramientas del MCP Server:```

1. `get_pokemon_info` - Información de PokeAPI

2. `get_pokemon_price` - Precios e inventarioO si prefieres usar el entorno virtual:

3. `search_pokemon` - Búsqueda avanzada

4. `list_pokemon_types` - Lista de tipos## 💬 Flujos de Conversación



## 📁 Estructura```bash



```### Búsqueda Simple# Activar entorno

adk-agent/

├── pokemon_agent.py      # Agente principal```source .venv/bin/activate  # Linux/Mac

├── pyproject.toml        # Dependencias Python

├── .env.example          # Template de variablesYou: busca un Pikachu# o

├── .env                  # Tu configuración (no en git)

└── README.md             # Esta documentación🤖: Pikachu (#25) - $150.00 - Stock: 42 ✅.venv\Scripts\activate  # Windows

```

```

## 🐛 Troubleshooting

# Ejecutar

### Error: "GOOGLE_API_KEY no está configurada"

- Verifica que existe el archivo `.env`### Búsqueda por Tipopython pokemon_agent.py

- Asegúrate de que contiene `GOOGLE_API_KEY=tu_clave`

``````

### Error: "No se encuentra el MCP Server"

- Compila el MCP Server: `cd ../mcp-server && npm run build`You: muéstrame pokemon de tipo Water

- Verifica que existe `../mcp-server/build/index.js`

🤖: Found 32 Pokemon:## 💬 Ejemplos de Uso

### Error al conectar con PokeAPI

- Verifica tu conexión a internet     • Squirtle (#7) - $200.00 ✅

- PokeAPI puede estar temporalmente no disponible

     • Blastoise (#9) - $149.00 ✅Una vez iniciado el agente, puedes hacer preguntas como:

### Cuota de API excedida

Gemini tier gratuito: **50 requests/día**     ...



Si ves el error:``````

```

Error: 429 Quota ExceededTú: ¿Qué información tienes sobre Pikachu?

```

### Compra Completa🤖 Pokemon Agent: Pikachu es un Pokemon de tipo eléctrico...

**Solución**: Espera ~1 hora o actualiza plan.

```

## 🔗 Referencias

You: quiero comprar un CharizardTú: ¿Cuál es el precio de Charizard?

- [Google ADK Documentation](https://google.github.io/adk-docs/)

- [Model Context Protocol](https://modelcontextprotocol.io/)🤖: [Buscando...] Charizard (#6) - $51.00 ✅🤖 Pokemon Agent: Charizard tiene un precio de $180 USD...

- [PokeAPI](https://pokeapi.co/)

- [Gemini API](https://ai.google.dev/)



---You: añadir al carritoTú: Muéstrame Pokemon de tipo fuego con precio menor a $150



**Framework**: Google ADK + Gemini 2.5 Flash  🤖: [Creando carrito...] ¡Listo! Total: $51.00🤖 Pokemon Agent: Aquí están los Pokemon de tipo fuego disponibles...

**Versión**: 1.0  

**Última actualización**: 20 de Octubre de 2025


You: ver carritoTú: ¿Qué Pokemon están en stock ahora?

🤖: 🛒 Charizard x1 = $51.00🤖 Pokemon Agent: Los siguientes Pokemon están disponibles...

```

You: pagar con tarjeta

🤖: ✅ Pago completado! Transaction ID: txn_xyz## 🏗️ Arquitectura

```

```

### Carrito MúltipleUsuario

```   ↓

You: añade un Pikachu y un Charmander al carritoPokemon Agent (ADK + Gemini 2.5)

🤖: [Creando carrito...]    ↓

     ✅ 2 Pokemon añadidosMCP Tools (4 herramientas)

     Total: $371.00   ↓

┌─────────────────────┬──────────────────────┐

You: ver carrito│   PokeAPI           │  pokemon-gen1.json   │

🤖: 🛒 Tu carrito:│   (API externa)     │  (datos locales)     │

     • Pikachu x1 = $150.00└─────────────────────┴──────────────────────┘

     • Charmander x1 = $221.00```

     💰 Total: $371.00

```### Flujo de Datos



## 🏗️ Arquitectura1. **Usuario** hace una pregunta al agente

2. **Agente ADK** procesa la pregunta con Gemini 2.5

```3. **Gemini** decide qué herramientas MCP usar

Usuario4. **MCP Server** ejecuta las herramientas necesarias:

  ↓ (lenguaje natural)   - Consulta PokeAPI para información del Pokemon

Shopping Agent (Gemini)   - Lee pokemon-gen1.json para precios

  ↓ (function calling)5. **Agente** recibe los datos y genera respuesta

  ├─► search_pokemon() → Catálogo local6. **Usuario** recibe la respuesta formateada

  ├─► view_cart() → Carrito en memoria

  ├─► create_shopping_cart() → Merchant Agent (AP2)## 🔌 Integración con MCP

  └─► checkout() → Merchant Agent (AP2)

```El agente se conecta al MCP Server usando `MCPTool.from_server()`:



## 🔧 Function Calling```python

mcp_tools = MCPTool.from_server(

El agente usa **function calling** de Gemini:    command="node",

    args=[mcp_server_path],

```python    env={}

# Definir herramienta)

search_tool = genai.protos.FunctionDeclaration(```

    name="search_pokemon",

    description="Search for Pokemon...",Esto le da acceso a las 4 herramientas del MCP Server:

    parameters=genai.protos.Schema(1. `get_pokemon_info` - Información de PokeAPI

        type=genai.protos.Type.OBJECT,2. `get_pokemon_price` - Precios e inventario

        properties={3. `search_pokemon` - Búsqueda avanzada

            "query": genai.protos.Schema(4. `list_pokemon_types` - Lista de tipos

                type=genai.protos.Type.STRING

            ),## 📁 Estructura

            "pokemon_type": genai.protos.Schema(

                type=genai.protos.Type.STRING```

            )adk-agent/

        }├── pokemon_agent.py      # Agente principal

    )├── pyproject.toml        # Dependencias Python

)├── .env.example          # Template de variables

├── .env                  # Tu configuración (no en git)

# Crear modelo└── README.md            # Esta documentación

model = genai.GenerativeModel(```

    model_name='gemini-2.0-flash-exp',

    tools=[search_tool, ...],## 🐛 Troubleshooting

    system_instruction="You are a Pokemon shopping assistant..."

)### Error: "GOOGLE_API_KEY no está configurada"

```- Verifica que existe el archivo `.env`

- Asegúrate de que contiene `GOOGLE_API_KEY=tu_clave`

## 🎓 Conceptos ADK Aplicados

### Error: "No se encuentra el MCP Server"

### 1. System Instructions- Compila el MCP Server: `cd ../mcp-server && npm run build`

```python- Verifica que existe `../mcp-server/build/index.js`

system_instruction="""

You are a helpful Pokemon shopping assistant. ### Error al conectar con PokeAPI

Always use tools to help users.- Verifica tu conexión a internet

Be friendly and guide them through shopping!- PokeAPI puede estar temporalmente no disponible

"""

```## 🔗 Referencias



### 2. Tool Definitions- [Google ADK Documentation](https://google.github.io/adk-docs/)

Cada herramienta tiene:- [Model Context Protocol](https://modelcontextprotocol.io/)

- **Nombre**: Identificador único- [PokeAPI](https://pokeapi.co/)

- **Descripción**: Cuándo usarla- [Gemini API](https://ai.google.dev/)

- **Parámetros**: Schema con tipos

### 3. Function Execution
```python
if function_name == "search_pokemon":
    result = assistant.search_pokemon(**function_args)
    
# Enviar resultado de vuelta a Gemini
response = chat.send_message(
    genai.protos.Content(
        parts=[genai.protos.Part(
            function_response=genai.protos.FunctionResponse(
                name=function_name,
                response={"result": result}
            )
        )]
    )
)
```

## 🐛 Limitaciones

### Cuota de API
Gemini tier gratuito: **50 requests/día**

Si excedes:
```
Error: 429 Quota Exceeded
```

**Solución**: Espera ~1 hora o actualiza plan.

### Tipos de Pokemon
La búsqueda por tipo requiere llamadas a PokeAPI, puede ser lenta.

### Persistencia
El carrito se guarda solo en memoria. Se pierde al cerrar el agente.

## 📖 Más Información

Ver [README principal](../README.md) para arquitectura completa.

**Referencias**:
- Google AI SDK: https://ai.google.dev/
- Function Calling: https://ai.google.dev/docs/function_calling
- Gemini Models: https://ai.google.dev/models/gemini

---

**Framework**: Google Generative AI Python SDK  
**Modelo**: Gemini 2.0 Flash  
**Última actualización**: 17 de Octubre de 2025

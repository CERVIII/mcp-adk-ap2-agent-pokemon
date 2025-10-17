"""
Pokemon Agent using Google ADK (Agent Development Kit)

Este agente usa Gemini 2.5 Flash y se conecta con el MCP Server
para acceder a las herramientas de Pokemon.
"""

import os
from dotenv import load_dotenv
from google.adk.llm_agent.types import AgentExecutionConfig, AgentModelConfig
from google.adk.llm_agent import LlmAgent
from google.adk.core.runner import Runner
from google.adk.tools.mcp_tool import MCPTool

# Cargar variables de entorno
load_dotenv()

def create_pokemon_agent() -> LlmAgent:
    """
    Crea el agente de Pokemon con conexión al MCP server.
    """
    
    # Configuración del modelo Gemini
    model_config = AgentModelConfig(
        model_id="gemini-2.0-flash-exp",
        temperature=0.7,
    )
    
    # Configuración de ejecución
    execution_config = AgentExecutionConfig(
        max_turns=10,
    )
    
    # Conectar con el MCP Server de Pokemon
    # El MCP server debe estar corriendo en el path especificado
    mcp_server_path = os.path.join(
        os.path.dirname(__file__),
        "../mcp-server/build/index.js"
    )
    
    # Crear herramientas MCP
    mcp_tools = MCPTool.from_server(
        command="node",
        args=[mcp_server_path],
        env={}
    )
    
    # Crear el agente
    agent = LlmAgent(
        name="pokemon_assistant",
        description=(
            "Soy un asistente experto en Pokemon. Puedo ayudarte a:\n"
            "- Buscar información detallada sobre cualquier Pokemon\n"
            "- Consultar precios e inventario de Pokemon de la primera generación\n"
            "- Buscar Pokemon por tipo, precio y disponibilidad\n"
            "- Recomendar Pokemon según tus preferencias\n"
        ),
        model_config=model_config,
        execution_config=execution_config,
        tools=mcp_tools,
    )
    
    return agent


def main():
    """
    Función principal para ejecutar el agente.
    """
    # Verificar que existe la API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY no está configurada")
        print("Por favor, crea un archivo .env basado en .env.example")
        return
    
    print("🚀 Iniciando Pokemon Agent con Google ADK...")
    print("=" * 60)
    
    # Crear el agente
    agent = create_pokemon_agent()
    
    # Crear runner para ejecutar el agente
    runner = Runner(agent)
    
    print("\n✅ Agente iniciado correctamente!")
    print("\nEjemplos de preguntas que puedes hacer:")
    print("  - ¿Qué información tienes sobre Pikachu?")
    print("  - ¿Cuál es el precio de Charizard?")
    print("  - Muéstrame Pokemon de tipo fuego con precio menor a $150")
    print("  - ¿Qué Pokemon están disponibles para comprar?")
    print("\n" + "=" * 60)
    print("\n💬 Escribe tu pregunta (o 'exit' para salir):\n")
    
    # Loop interactivo
    while True:
        try:
            user_input = input("Tú: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'salir']:
                print("\n👋 ¡Hasta luego!")
                break
            
            if not user_input:
                continue
            
            print("\n🤖 Pokemon Agent: ", end="", flush=True)
            
            # Ejecutar el agente
            result = runner.run(user_input)
            
            # Mostrar la respuesta
            print(result.content)
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print()


if __name__ == "__main__":
    main()

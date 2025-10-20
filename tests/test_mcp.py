#!/usr/bin/env python3
"""
Test MCP Server desde Python
"""

import asyncio
import json
import subprocess


async def test_mcp_server():
    """Test del MCP Server usando stdio"""
    
    print("🧪 Testing MCP Server con @modelcontextprotocol/sdk\n")
    
    # Iniciar el servidor MCP
    mcp_path = "/home/idb0181/Escritorio/prueba-mcp-a2a-ap2/mcp-server/build/index.js"
    
    process = subprocess.Popen(
        ["node", mcp_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    request_id = 1
    
    def send_request(method, params):
        nonlocal request_id
        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params
        }
        request_id += 1
        
        request_str = json.dumps(request) + "\n"
        process.stdin.write(request_str)
        process.stdin.flush()
        
        response_str = process.stdout.readline()
        if not response_str:
            return None
        
        return json.loads(response_str)
    
    # Test 1: Initialize
    print("1️⃣  Inicializando conexión...")
    response = send_request("initialize", {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {
            "name": "test-client",
            "version": "1.0.0"
        }
    })
    print(f"   ✅ Inicializado: {response.get('result', {}).get('serverInfo', {}).get('name')}")
    
    # Test 2: List Tools
    print("\n2️⃣  Listando herramientas...")
    response = send_request("tools/list", {})
    tools = response.get('result', {}).get('tools', [])
    print(f"   ✅ {len(tools)} herramientas encontradas:")
    for tool in tools:
        print(f"      • {tool['name']}")
    
    # Test 3: Get Pokemon Price
    print("\n3️⃣  Probando: get_pokemon_price")
    response = send_request("tools/call", {
        "name": "get_pokemon_price",
        "arguments": {"pokemon": "pikachu"}
    })
    result = response.get('result', {})
    if 'content' in result:
        for content in result['content']:
            if content.get('type') == 'text':
                print(f"   📊 Resultado:")
                # Parsear el texto para mostrar bonito
                text = content.get('text', '')
                for line in text.split('\n')[:5]:
                    print(f"      {line}")
    
    # Test 4: Search Pokemon
    print("\n4️⃣  Probando: search_pokemon (tipo Fire)")
    response = send_request("tools/call", {
        "name": "search_pokemon",
        "arguments": {
            "type": "Fire",
            "max_price": 200
        }
    })
    result = response.get('result', {})
    if 'content' in result:
        for content in result['content']:
            if content.get('type') == 'text':
                text = content.get('text', '')
                # Contar Pokemon encontrados
                try:
                    data = json.loads(text)
                    print(f"   🔥 {len(data)} Pokemon tipo Fire encontrados (precio ≤ $200)")
                    for p in data[:3]:
                        print(f"      • {p['nombre'].capitalize()} - ${p['precio']:.2f}")
                except:
                    print(f"   📊 Respuesta: {text[:100]}...")
    
    # Test 5: List Types
    print("\n5️⃣  Probando: list_pokemon_types")
    response = send_request("tools/call", {
        "name": "list_pokemon_types",
        "arguments": {}
    })
    result = response.get('result', {})
    if 'content' in result:
        for content in result['content']:
            if content.get('type') == 'text':
                try:
                    data = json.loads(content.get('text', '{}'))
                    types = data.get('types', [])
                    print(f"   🎨 {len(types)} tipos disponibles:")
                    print(f"      {', '.join(types[:10])}")
                except:
                    pass
    
    # Test 6: Get Pokemon Info
    print("\n6️⃣  Probando: get_pokemon_info (Charizard)")
    response = send_request("tools/call", {
        "name": "get_pokemon_info",
        "arguments": {"pokemon": "charizard"}
    })
    result = response.get('result', {})
    if 'content' in result:
        for content in result['content']:
            if content.get('type') == 'text':
                text = content.get('text', '')
                lines = text.split('\n')
                print(f"   🐉 Información de Charizard:")
                for line in lines[:8]:
                    if line.strip():
                        print(f"      {line}")
    
    print("\n✅ Tests completados!")
    
    # Cerrar proceso
    process.terminate()
    process.wait()


if __name__ == "__main__":
    asyncio.run(test_mcp_server())

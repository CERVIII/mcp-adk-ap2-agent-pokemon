#!/usr/bin/env python3
"""
Test del MCP Server refactorizado en src/mcp/
"""

import subprocess
import json
import sys
import os

def test_refactored_mcp_server():
    """Prueba básica del servidor MCP refactorizado"""
    print("\n" + "="*60)
    print("Testing Refactored MCP Server")
    print("="*60)
    
    # Ruta al servidor refactorizado
    server_path = os.path.join(
        os.path.dirname(__file__),
        '../../../src/mcp/build/index.js'
    )
    
    if not os.path.exists(server_path):
        print(f"❌ ERROR: Server not found at {server_path}")
        return False
    
    print(f"✓ Server found at: {server_path}")
    
    # Crear proceso del MCP Server
    process = subprocess.Popen(
        ['node', server_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    try:
        # Enviar mensaje de inicialización
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("\n→ Sending initialize request...")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Leer respuesta de inicialización
        init_response = process.stdout.readline()
        if init_response:
            response_data = json.loads(init_response)
            print(f"✓ Received initialize response")
            print(f"  Server name: {response_data.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}")
            print(f"  Protocol version: {response_data.get('result', {}).get('protocolVersion', 'Unknown')}")
        else:
            print("❌ No response received")
            return False
        
        # Solicitar lista de herramientas
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        print("\n→ Requesting tools list...")
        process.stdin.write(json.dumps(tools_request) + "\n")
        process.stdin.flush()
        
        tools_response = process.stdout.readline()
        if tools_response:
            tools_data = json.loads(tools_response)
            tools = tools_data.get('result', {}).get('tools', [])
            print(f"✓ Received {len(tools)} tools:")
            for tool in tools:
                print(f"  - {tool['name']}")
        else:
            print("❌ No tools response received")
            return False
        
        # Probar herramienta simple: list_pokemon_types
        test_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "list_pokemon_types",
                "arguments": {}
            }
        }
        
        print("\n→ Testing list_pokemon_types tool...")
        process.stdin.write(json.dumps(test_request) + "\n")
        process.stdin.flush()
        
        test_response = process.stdout.readline()
        if test_response:
            test_data = json.loads(test_response)
            result = test_data.get('result', {})
            if 'content' in result:
                print("✓ Tool executed successfully")
                content = result['content'][0]['text']
                types_data = json.loads(content)
                print(f"  Found {len(types_data.get('types', []))} Pokemon types")
            else:
                print(f"❌ Tool execution failed: {test_data}")
                return False
        else:
            print("❌ No tool response received")
            return False
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED - MCP Server refactorizado funciona correctamente")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except:
            process.kill()

if __name__ == "__main__":
    success = test_refactored_mcp_server()
    sys.exit(0 if success else 1)

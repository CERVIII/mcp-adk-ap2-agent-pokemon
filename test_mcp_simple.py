#!/usr/bin/env python3
"""
Test simple del MCP Server - Prueba directa de herramientas
"""

import subprocess
import json
import sys


def test_mcp_tool(tool_name, arguments):
    """Prueba una herramienta del MCP Server"""
    print(f"\n{'='*60}")
    print(f"Testing: {tool_name}")
    print(f"Arguments: {json.dumps(arguments, indent=2)}")
    print('='*60)
    
    # Crear proceso del MCP Server
    process = subprocess.Popen(
        ['node', 'build/main.js'],
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
        
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Leer respuesta de inicialización
        init_response = process.stdout.readline()
        print(f"Init response: {init_response.strip()[:100]}...")
        
        # Enviar notificación initialized
        initialized_notif = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        process.stdin.write(json.dumps(initialized_notif) + "\n")
        process.stdin.flush()
        
        # Llamar a la herramienta
        tool_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        process.stdin.write(json.dumps(tool_request) + "\n")
        process.stdin.flush()
        
        # Leer respuesta
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line)
            
            if "error" in response:
                print(f"❌ ERROR: {response['error']}")
                return False
            
            if "result" in response:
                result = response["result"]
                print(f"\n✅ SUCCESS!")
                print(f"Result: {json.dumps(result, indent=2)}")
                
                # Parse content
                if "content" in result:
                    for content in result["content"]:
                        if content.get("type") == "text":
                            text = content.get("text", "")
                            try:
                                data = json.loads(text)
                                print(f"\nParsed data:")
                                print(json.dumps(data, indent=2))
                            except json.JSONDecodeError:
                                print(f"\nText response: {text}")
                
                return True
        
        print("❌ No response received")
        return False
        
    finally:
        process.terminate()
        process.wait()


def main():
    """Ejecutar todas las pruebas"""
    print("🧪 Testing MCP Server Tools")
    print("=" * 60)
    
    tests = [
        ("get_pokemon_price", {"pokemon": "pikachu"}),
        ("get_pokemon_price", {"pokemon": "25"}),
        ("get_pokemon_price", {"pokemon": "charizard"}),
        ("search_pokemon", {"type": "fire", "max_price": 200}),
        ("search_pokemon", {"max_price": 100}),
        ("get_pokemon_info", {"pokemon": "bulbasaur"}),
        ("list_pokemon_types", {}),
    ]
    
    passed = 0
    failed = 0
    
    for tool_name, args in tests:
        if test_mcp_tool(tool_name, args):
            passed += 1
        else:
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed")
    print('='*60)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

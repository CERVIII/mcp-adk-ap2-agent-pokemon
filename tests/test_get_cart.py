#!/usr/bin/env python3
"""
Test script para verificar la nueva tool get_current_cart
"""

import subprocess
import json
import sys

def test_get_current_cart():
    """Test the get_current_cart tool"""
    
    # Path to the MCP server
    server_path = "./mcp-server/build/index.js"
    
    # Request to list tools (verify our new tool exists)
    list_tools_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }
    
    print("📋 Verificando que la tool get_current_cart existe...")
    
    # Start the server
    process = subprocess.Popen(
        ["node", server_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Send list tools request
    process.stdin.write(json.dumps(list_tools_request) + "\n")
    process.stdin.flush()
    
    # Read response
    response_line = process.stdout.readline()
    
    try:
        response = json.loads(response_line)
        tools = response.get("result", {}).get("tools", [])
        
        # Check if get_current_cart exists
        cart_tool = None
        for tool in tools:
            if tool["name"] == "get_current_cart":
                cart_tool = tool
                break
        
        if cart_tool:
            print("✅ Tool 'get_current_cart' encontrada!")
            print(f"   Descripción: {cart_tool['description']}")
        else:
            print("❌ Tool 'get_current_cart' NO encontrada")
            print("   Tools disponibles:")
            for tool in tools:
                print(f"   - {tool['name']}")
            sys.exit(1)
            
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing response: {e}")
        print(f"   Raw response: {response_line}")
        sys.exit(1)
    
    # Now test calling the tool
    print("\n🧪 Probando get_current_cart con carrito vacío...")
    
    call_tool_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "get_current_cart",
            "arguments": {}
        }
    }
    
    process.stdin.write(json.dumps(call_tool_request) + "\n")
    process.stdin.flush()
    
    response_line = process.stdout.readline()
    
    try:
        response = json.loads(response_line)
        result = response.get("result", {})
        content = result.get("content", [])
        
        if content:
            cart_data = json.loads(content[0]["text"])
            print("✅ Respuesta recibida:")
            print(json.dumps(cart_data, indent=2, ensure_ascii=False))
            
            if cart_data.get("status") == "empty":
                print("\n✅ Carrito vacío - funcionando correctamente!")
            else:
                print("\n✅ Carrito con items - funcionando correctamente!")
        else:
            print("❌ No se recibió contenido en la respuesta")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"   Raw response: {response_line}")
        sys.exit(1)
    
    # Clean up
    process.terminate()
    
    print("\n🎉 ¡Test completado exitosamente!")

if __name__ == "__main__":
    test_get_current_cart()

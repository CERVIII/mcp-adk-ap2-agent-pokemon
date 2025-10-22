#!/usr/bin/env python3
"""Debug MCP responses"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "ap2-integration"))

from src.common.mcp_client import get_mcp_client

async def main():
    print("Testing MCP responses...")
    print("=" * 60)
    
    async with get_mcp_client() as mcp:
        # Test 1: search_pokemon
        print("\n1. Testing search_pokemon...")
        result = await mcp.search_pokemon(limit=2)
        print(f"Type: {type(result)}")
        print(f"Value: {result}")
        if isinstance(result, list) and len(result) > 0:
            print(f"First item type: {type(result[0])}")
            print(f"First item: {result[0]}")
        
        # Test 2: list_pokemon_types
        print("\n2. Testing list_pokemon_types...")
        result2 = await mcp.list_pokemon_types()
        print(f"Type: {type(result2)}")
        print(f"Value: {result2}")
        
        # Test 3: create_pokemon_cart
        print("\n3. Testing create_pokemon_cart...")
        result3 = await mcp.create_pokemon_cart([{"product_id": "25", "quantity": 1}])
        print(f"Type: {type(result3)}")
        print(f"Value (first 200 chars): {str(result3)[:200]}")
        
if __name__ == "__main__":
    asyncio.run(main())

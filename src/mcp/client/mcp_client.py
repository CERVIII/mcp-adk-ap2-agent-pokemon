"""
MCP Client - Connects to the Pokemon MCP server

This client enables Python agents to call MCP tools exposed by the
TypeScript MCP server (mcp-server/src/index.ts).
"""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


class MCPClient:
    """Client for interacting with Pokemon MCP server"""
    
    def __init__(self, server_script_path: str):
        """
        Initialize MCP client
        
        Args:
            server_script_path: Path to the MCP server entry point (build/index.js)
        """
        self.server_script_path = os.path.abspath(server_script_path)
        self.session: Optional[ClientSession] = None
        self._stdio_context = None
        
    async def connect(self):
        """Establish connection to MCP server"""
        server_params = StdioServerParameters(
            command="node",
            args=[self.server_script_path],
            env=None
        )
        
        self._stdio_context = stdio_client(server_params)
        self._read, self._write = await self._stdio_context.__aenter__()
        self.session = ClientSession(self._read, self._write)
        await self.session.__aenter__()
        
        # Initialize the session
        await self.session.initialize()
        
        print(f"✅ Connected to MCP server: {self.server_script_path}")
        
    async def disconnect(self):
        """Close connection to MCP server"""
        if self.session:
            await self.session.__aexit__(None, None, None)
        if self._stdio_context:
            await self._stdio_context.__aexit__(None, None, None)
        print("❌ Disconnected from MCP server")
        
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools from MCP server"""
        if not self.session:
            raise RuntimeError("Not connected to MCP server. Call connect() first.")
        
        response = await self.session.list_tools()
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema
            }
            for tool in response.tools
        ]
        
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call a specific MCP tool
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments as dict
            
        Returns:
            Tool result (parsed from JSON if possible)
        """
        if not self.session:
            raise RuntimeError("Not connected to MCP server. Call connect() first.")
        
        result = await self.session.call_tool(tool_name, arguments)
        
        # MCP returns results as a list of content items
        if result.content:
            # Usually the first item contains the result
            first_content = result.content[0]
            if hasattr(first_content, 'text'):
                try:
                    # Try to parse as JSON
                    return json.loads(first_content.text)
                except json.JSONDecodeError:
                    # Return as plain text
                    return first_content.text
        
        return None
        
    # ============================================
    # Convenience methods for Pokemon MCP tools
    # ============================================
    
    async def get_pokemon_info(self, pokemon: str) -> Dict[str, Any]:
        """
        Get detailed Pokemon info from PokeAPI
        
        Args:
            pokemon: Pokemon name or number (e.g., "pikachu" or "25")
            
        Returns:
            Dict with Pokemon abilities, types, stats, sprites
        """
        return await self.call_tool("get_pokemon_info", {"pokemon": pokemon})
        
    async def get_pokemon_price(self, pokemon: str) -> Dict[str, Any]:
        """
        Get Pokemon price and inventory from local catalog
        
        Args:
            pokemon: Pokemon name or number
            
        Returns:
            Dict with price, stock availability, sales info
        """
        return await self.call_tool("get_pokemon_price", {"pokemon": pokemon})
        
    async def search_pokemon(
        self,
        type: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        only_available: bool = False,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search Pokemon with filters
        
        Args:
            type: Pokemon type (fire, water, grass, etc)
            min_price: Minimum price in USD
            max_price: Maximum price in USD
            only_available: Only show in-stock Pokemon
            limit: Max results
            
        Returns:
            List of matching Pokemon with complete info
        """
        args = {"limit": limit}
        if type:
            args["type"] = type
        if min_price is not None:
            args["minPrice"] = min_price
        if max_price is not None:
            args["maxPrice"] = max_price
        if only_available:
            args["onlyAvailable"] = only_available
            
        return await self.call_tool("search_pokemon", args)
        
    async def list_pokemon_types(self) -> List[str]:
        """
        Get all available Pokemon types
        
        Returns:
            List of type names (excludes "unknown" and "shadow")
        """
        result = await self.call_tool("list_pokemon_types", {})
        return result.get("types", [])
        
    async def get_pokemon_product(self, product_id: str) -> Dict[str, Any]:
        """
        Get detailed product info combining PokeAPI + local pricing
        
        Args:
            product_id: Pokemon number (1-151)
            
        Returns:
            Dict with complete Pokemon + pricing data
        """
        return await self.call_tool("get_pokemon_product", {"product_id": product_id})
        
    async def create_pokemon_cart(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a CartMandate for Pokemon purchase (AP2 protocol)
        
        Args:
            items: List of items with format:
                   [{"product_id": "25", "quantity": 1}, ...]
                   
        Returns:
            CartMandate dict ready for AP2 payment processing
        """
        return await self.call_tool("create_pokemon_cart", {"items": items})
        
    async def get_current_cart(self) -> Dict[str, Any]:
        """
        Get the current active cart
        
        Returns:
            CartMandate if exists, or message if empty
        """
        return await self.call_tool("get_current_cart", {})


# ============================================
# Context Manager Support
# ============================================

class MCPClientContextManager:
    """Context manager for automatic connection/disconnection"""
    
    def __init__(self, server_script_path: str):
        self.client = MCPClient(server_script_path)
        
    async def __aenter__(self):
        await self.client.connect()
        return self.client
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.disconnect()


# ============================================
# Utility function
# ============================================

def get_mcp_client(server_script_path: Optional[str] = None) -> MCPClientContextManager:
    """
    Get an MCP client context manager
    
    Args:
        server_script_path: Path to MCP server. If None, uses env var MCP_SERVER_PATH
        
    Returns:
        Context manager that handles connection/disconnection
        
    Example:
        async with get_mcp_client() as mcp:
            result = await mcp.search_pokemon(type="fire", limit=5)
    """
    if server_script_path is None:
        # Try environment variable first
        server_script_path = os.getenv("MCP_SERVER_PATH")
        
        # If not set, calculate absolute path relative to this file
        if not server_script_path:
            current_file = os.path.abspath(__file__)
            # From src/mcp/client/mcp_client.py to build/src/mcp/server/index.js
            # Go up to project root then to build/src/mcp/server/index.js
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
            server_script_path = os.path.join(project_root, "build", "src", "mcp", "server", "index.js")
    
    return MCPClientContextManager(server_script_path)


# ============================================
# CLI for testing
# ============================================

async def test_mcp_client():
    """Test MCP client functionality"""
    print("🧪 Testing MCP Client\n")
    
    async with get_mcp_client() as mcp:
        # List available tools
        print("📋 Available tools:")
        tools = await mcp.list_tools()
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")
        print()
        
        # Test get_pokemon_info
        print("🔍 Getting Pikachu info...")
        pikachu = await mcp.get_pokemon_info("pikachu")
        print(f"  Name: {pikachu['name']}")
        print(f"  Types: {', '.join(pikachu['types'])}")
        print()
        
        # Test get_pokemon_price
        print("💰 Getting Pikachu price...")
        price_info = await mcp.get_pokemon_price("25")
        print(f"  Price: ${price_info['precio']} USD")
        print(f"  Available: {price_info['inventario']['disponibles']}")
        print()
        
        # Test search
        print("🔥 Searching fire Pokemon...")
        fire_pokemon = await mcp.search_pokemon(type="fire", limit=3)
        for p in fire_pokemon:
            print(f"  - {p['name']} (#{p['numero']}): ${p['precio']} USD")
        print()
        
        # Test create cart
        print("🛒 Creating cart...")
        cart = await mcp.create_pokemon_cart([
            {"product_id": "25", "quantity": 1}  # Pikachu
        ])
        print(f"  Cart ID: {cart['contents']['id']}")
        print(f"  Total: ${cart['contents']['payment_request']['details']['total']['amount']['value']}")
        print()
        
        print("✅ All tests passed!")


if __name__ == "__main__":
    # Run tests
    asyncio.run(test_mcp_client())

"""
MCP Client - Connects to MCP Server to query Pokemon catalog
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
import subprocess


class MCPClient:
    """Client to communicate with MCP Server via stdio"""
    
    def __init__(self, mcp_server_path: str):
        """
        Initialize MCP client
        
        Args:
            mcp_server_path: Path to the MCP server executable (e.g., 'node build/index.js')
        """
        self.mcp_server_path = mcp_server_path
        self.process: Optional[subprocess.Popen] = None
        self.request_id = 0
    
    async def start(self):
        """Start the MCP server process"""
        # Split the command into parts
        parts = self.mcp_server_path.split()
        
        self.process = subprocess.Popen(
            parts,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
    
    async def stop(self):
        """Stop the MCP server process"""
        if self.process:
            self.process.terminate()
            self.process.wait()
    
    def _get_next_id(self) -> int:
        """Get next request ID"""
        self.request_id += 1
        return self.request_id
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call a tool on the MCP server
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            Tool response
        """
        if not self.process:
            raise RuntimeError("MCP client not started")
        
        # Build JSON-RPC request
        request = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        # Send request
        request_str = json.dumps(request) + "\n"
        self.process.stdin.write(request_str)
        self.process.stdin.flush()
        
        # Read response
        response_str = self.process.stdout.readline()
        if not response_str:
            raise RuntimeError("No response from MCP server")
        
        response = json.loads(response_str)
        
        # Check for errors
        if "error" in response:
            raise RuntimeError(f"MCP Error: {response['error']}")
        
        return response.get("result")
    
    async def get_pokemon_price(self, pokemon: str) -> Optional[Dict[str, Any]]:
        """
        Get price and inventory for a Pokemon
        
        Args:
            pokemon: Pokemon name or number
            
        Returns:
            Pokemon price info or None if not found
        """
        try:
            result = await self.call_tool(
                "get_pokemon_price",
                {"pokemon": pokemon}
            )
            
            if result and "content" in result:
                for content in result["content"]:
                    if content.get("type") == "text":
                        text = content.get("text", "")
                        
                        # Parse JSON response from MCP
                        try:
                            data = json.loads(text)
                            
                            # Check if it's an error response
                            if "error" in data:
                                return None
                            
                            # Return the structured data
                            return data
                        except json.JSONDecodeError:
                            print(f"Failed to parse MCP response: {text}")
                            return None
            
            return None
        except Exception as e:
            print(f"Error getting pokemon price from MCP: {e}")
            return None
    
    async def search_pokemon(
        self,
        pokemon_type: Optional[str] = None,
        max_price: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for Pokemon with filters
        
        Args:
            pokemon_type: Pokemon type (e.g., 'Fire', 'Water')
            max_price: Maximum price filter
            
        Returns:
            List of matching Pokemon
        """
        try:
            args = {}
            if pokemon_type:
                args["type"] = pokemon_type
            if max_price:
                args["max_price"] = max_price
            
            result = await self.call_tool("search_pokemon", args)
            
            if result and "content" in result:
                for content in result["content"]:
                    if content.get("type") == "text":
                        text = content.get("text", "")
                        
                        # Parse JSON response
                        try:
                            data = json.loads(text)
                            return data.get("results", [])
                        except json.JSONDecodeError:
                            print(f"Failed to parse MCP response: {text}")
                            return []
            
            return []
        except Exception as e:
            print(f"Error searching pokemon from MCP: {e}")
            return []


class SimpleMCPClient:
    """
    Simplified MCP client that reads directly from pokemon-gen1.json
    This is a temporary solution until we implement full MCP protocol
    """
    
    def __init__(self, catalog_path: str = None):
        """Initialize simple MCP client"""
        import os
        if catalog_path is None:
            # Default to project root
            catalog_path = os.path.join(
                os.path.dirname(__file__),
                "../../../pokemon-gen1.json"
            )
        self.catalog_path = catalog_path
        self.catalog_data = None
        self._load_catalog()
    
    def _load_catalog(self):
        """Load catalog from JSON file"""
        try:
            with open(self.catalog_path, 'r') as f:
                self.catalog_data = json.load(f)
        except Exception as e:
            print(f"Error loading catalog: {e}")
            self.catalog_data = []
    
    async def start(self):
        """Start client (no-op for simple client)"""
        pass
    
    async def stop(self):
        """Stop client (no-op for simple client)"""
        pass
    
    async def get_pokemon_price(self, pokemon: str) -> Optional[Dict[str, Any]]:
        """
        Get price and inventory for a Pokemon
        
        Args:
            pokemon: Pokemon name or number
            
        Returns:
            Pokemon data or None if not found
        """
        if not self.catalog_data:
            return None
        
        pokemon_lower = pokemon.lower()
        
        # Search by name or number
        for p in self.catalog_data:
            if (p['nombre'].lower() == pokemon_lower or 
                str(p['numero']) == pokemon):
                return p
        
        return None
    
    async def search_pokemon(
        self,
        query: Optional[str] = None,
        pokemon_type: Optional[str] = None,
        max_price: Optional[float] = None,
        only_available: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search for Pokemon with filters
        
        Args:
            query: Pokemon name or search term
            pokemon_type: Pokemon type (e.g., 'Fire', 'Water')
            max_price: Maximum price filter
            only_available: Only show available Pokemon
            
        Returns:
            List of matching Pokemon
        """
        if not self.catalog_data:
            return []
        
        results = self.catalog_data.copy()
        
        # Filter by query
        if query:
            query_lower = query.lower()
            results = [
                p for p in results
                if query_lower in p['nombre'].lower() or
                   query_lower == str(p['numero'])
            ]
        
        # Filter by price
        if max_price is not None:
            results = [p for p in results if p['precio'] <= max_price]
        
        # Filter by availability
        if only_available:
            results = [
                p for p in results
                if p.get('enVenta') and
                   p['inventario']['disponibles'] > 0
            ]
        
        return results


# Factory function to create the appropriate client
def create_mcp_client(use_real_mcp: bool = False) -> Any:
    """
    Create MCP client
    
    Args:
        use_real_mcp: If True, use real MCP protocol client.
                     If False, use simplified client.
    
    Returns:
        MCP client instance
    """
    if use_real_mcp:
        import os
        mcp_server_path = os.path.join(
            os.path.dirname(__file__),
            "../../../mcp-server/build/index.js"
        )
        return MCPClient(f"node {mcp_server_path}")
    else:
        return SimpleMCPClient()

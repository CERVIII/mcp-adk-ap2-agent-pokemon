#!/usr/bin/env node

/**
 * MCP Pokemon Server - Entry Point
 * Model Context Protocol server with Pokemon catalog and AP2 integration
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

// Import utilities
import { loadOrGenerateRSAKeys } from "./utils/index.js";
import { setMerchantPrivateKey } from "./ap2/index.js";

// Import tools
import { TOOLS } from "./tools/index.js";
import { getPokemonInfo } from "./tools/pokemon-info.js";
import { getPokemonPrice } from "./tools/pokemon-price.js";
import { searchPokemon } from "./tools/search-pokemon.js";
import { listPokemonTypes } from "./tools/list-types.js";
import { createPokemonCart } from "./tools/cart-create.js";
import { getCurrentCartTool } from "./tools/cart-get.js";
import { getPokemonProduct } from "./tools/product-info.js";

// ========================================
// Initialize Server
// ========================================

// Load RSA keys at startup
const keyPair = await loadOrGenerateRSAKeys();
setMerchantPrivateKey(keyPair.privateKey);

// Create MCP server
const server = new Server(
  {
    name: "mcp-pokemon-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// ========================================
// Request Handlers
// ========================================

// Handler: List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: TOOLS,
}));

// Handler: Execute tools
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case "get_pokemon_info":
        return await getPokemonInfo(args as any);

      case "get_pokemon_price":
        return await getPokemonPrice(args as any);

      case "search_pokemon":
        return await searchPokemon(args as any);

      case "list_pokemon_types":
        return await listPokemonTypes();

      case "create_pokemon_cart":
        return await createPokemonCart(args as any);

      case "get_current_cart":
        return await getCurrentCartTool();

      case "get_pokemon_product":
        return await getPokemonProduct(args as any);

      default:
        return {
          content: [
            {
              type: "text",
              text: `Unknown tool: ${name}`,
            },
          ],
          isError: true,
        };
    }
  } catch (error) {
    return {
      content: [
        {
          type: "text",
          text: `Error: ${error instanceof Error ? error.message : String(error)}`,
        },
      ],
      isError: true,
    };
  }
});

// ========================================
// Start Server
// ========================================

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("🚀 MCP Pokemon Server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});

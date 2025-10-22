/**
 * Tool Registry
 * Metadata definitions for all MCP tools
 */

import type { Tool } from "@modelcontextprotocol/sdk/types.js";

export const TOOLS: Tool[] = [
  {
    name: "get_pokemon_info",
    description:
      "Get detailed information about a Pokémon from PokeAPI including abilities, types, stats, and sprites. You can search by name or number (1-151 for Gen 1).",
    inputSchema: {
      type: "object",
      properties: {
        pokemon: {
          type: "string",
          description: "Pokemon name or ID number (e.g., 'pikachu' or '25')",
        },
      },
      required: ["pokemon"],
    },
  },
  {
    name: "get_pokemon_price",
    description:
      "Get price and inventory information for a Pokémon from the local Gen 1 catalog. Returns price in USD, stock availability, and sales information.",
    inputSchema: {
      type: "object",
      properties: {
        pokemon: {
          type: "string",
          description: "Pokemon name or number (1-151)",
        },
      },
      required: ["pokemon"],
    },
  },
  {
    name: "search_pokemon",
    description:
      "Search for Pokémon combining data from PokeAPI and local prices. You can filter by type, price range, and availability. Returns a list of matching Pokémon with complete information.",
    inputSchema: {
      type: "object",
      properties: {
        type: {
          type: "string",
          description: "Filter by Pokémon type (e.g., 'fire', 'water', 'grass')",
        },
        maxPrice: {
          type: "number",
          description: "Maximum price in USD",
        },
        minPrice: {
          type: "number",
          description: "Minimum price in USD",
        },
        onlyAvailable: {
          type: "boolean",
          description: "Only show Pokémon in stock",
          default: false,
        },
        limit: {
          type: "number",
          description: "Maximum number of results to return",
          default: 10,
        },
      },
    },
  },
  {
    name: "list_pokemon_types",
    description:
      "Get a list of all available Pokémon types from PokeAPI. Useful for knowing which types can be used in search filters.",
    inputSchema: {
      type: "object",
      properties: {},
    },
  },
  {
    name: "create_pokemon_cart",
    description:
      "Create a shopping cart (CartMandate) for Pokemon purchase. This follows the AP2 protocol specification. Returns a complete CartMandate with payment request structure ready for AP2 payment processing.",
    inputSchema: {
      type: "object",
      properties: {
        items: {
          type: "array",
          description: "List of items to purchase",
          items: {
            type: "object",
            properties: {
              product_id: {
                type: "string",
                description: "Pokemon number (1-151)",
              },
              quantity: {
                type: "integer",
                description: "Quantity to purchase",
                default: 1,
              },
            },
            required: ["product_id"],
          },
        },
      },
      required: ["items"],
    },
  },
  {
    name: "get_pokemon_product",
    description:
      "Get detailed information about a specific Pokemon product by its number. Combines data from PokeAPI and local pricing catalog.",
    inputSchema: {
      type: "object",
      properties: {
        product_id: {
          type: "string",
          description: "Pokemon number (1-151)",
        },
      },
      required: ["product_id"],
    },
  },
  {
    name: "get_current_cart",
    description:
      "View the current shopping cart with all items, prices, and total. Returns the active CartMandate if one exists, or a message if the cart is empty.",
    inputSchema: {
      type: "object",
      properties: {},
    },
  },
];

#!/usr/bin/env node
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema, } from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";
import { readFile } from "fs/promises";
import { fileURLToPath } from "url";
import { dirname, join } from "path";
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
// Caché para los datos de precios
let pokemonPricesCache = null;
// Función para cargar los precios de Pokémon
async function loadPokemonPrices() {
    if (pokemonPricesCache) {
        return pokemonPricesCache;
    }
    try {
        // Intentar cargar desde la raíz del proyecto
        const pokemonDataPath = join(__dirname, "../../../pokemon-gen1.json");
        const data = await readFile(pokemonDataPath, "utf-8");
        pokemonPricesCache = JSON.parse(data);
        return pokemonPricesCache;
    }
    catch (error) {
        console.error("Error loading pokemon prices:", error);
        return [];
    }
}
// Función para hacer peticiones a PokeAPI
async function fetchPokeAPI(endpoint) {
    const response = await fetch(`https://pokeapi.co/api/v2/${endpoint}`);
    if (!response.ok) {
        throw new Error(`PokeAPI error: ${response.statusText}`);
    }
    return response.json();
}
// Definición de las tools disponibles
const TOOLS = [
    {
        name: "get_pokemon_info",
        description: "Get detailed information about a Pokémon from PokeAPI including abilities, types, stats, and sprites. You can search by name or number (1-151 for Gen 1).",
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
        description: "Get price and inventory information for a Pokémon from the local Gen 1 catalog. Returns price in USD, stock availability, and sales information.",
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
        description: "Search for Pokémon combining data from PokeAPI and local prices. You can filter by type, price range, and availability. Returns a list of matching Pokémon with complete information.",
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
        description: "Get a list of all available Pokémon types from PokeAPI. Useful for knowing which types can be used in search filters.",
        inputSchema: {
            type: "object",
            properties: {},
        },
    },
];
// Crear el servidor MCP
const server = new Server({
    name: "mcp-pokemon-server",
    version: "1.0.0",
}, {
    capabilities: {
        tools: {},
    },
});
// Handler para listar las tools disponibles
server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
        tools: TOOLS,
    };
});
// Handler para ejecutar las tools
server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;
    try {
        switch (name) {
            case "get_pokemon_info": {
                const schema = z.object({
                    pokemon: z.string(),
                });
                const { pokemon } = schema.parse(args);
                const data = await fetchPokeAPI(`pokemon/${pokemon.toLowerCase()}`);
                return {
                    content: [
                        {
                            type: "text",
                            text: JSON.stringify({
                                id: data.id,
                                name: data.name,
                                height: data.height,
                                weight: data.weight,
                                types: data.types.map((t) => t.type.name),
                                abilities: data.abilities.map((a) => ({
                                    name: a.ability.name,
                                    isHidden: a.is_hidden,
                                })),
                                stats: data.stats.map((s) => ({
                                    name: s.stat.name,
                                    value: s.base_stat,
                                })),
                                sprites: {
                                    front_default: data.sprites.front_default,
                                    front_shiny: data.sprites.front_shiny,
                                },
                            }, null, 2),
                        },
                    ],
                };
            }
            case "get_pokemon_price": {
                const schema = z.object({
                    pokemon: z.string(),
                });
                const { pokemon } = schema.parse(args);
                const prices = await loadPokemonPrices();
                const pokemonLower = pokemon.toLowerCase();
                const found = prices.find((p) => p.nombre.toLowerCase() === pokemonLower ||
                    p.numero.toString() === pokemon);
                if (!found) {
                    return {
                        content: [
                            {
                                type: "text",
                                text: `Pokémon "${pokemon}" not found in price catalog. Only Gen 1 Pokémon (1-151) are available.`,
                            },
                        ],
                    };
                }
                return {
                    content: [
                        {
                            type: "text",
                            text: JSON.stringify(found, null, 2),
                        },
                    ],
                };
            }
            case "search_pokemon": {
                const schema = z.object({
                    type: z.string().optional(),
                    maxPrice: z.number().optional(),
                    minPrice: z.number().optional(),
                    onlyAvailable: z.boolean().default(false),
                    limit: z.number().default(10),
                });
                const filters = schema.parse(args);
                const prices = await loadPokemonPrices();
                let results = [];
                // Filtrar por precio y disponibilidad
                let filteredPrices = prices.filter((p) => {
                    if (filters.onlyAvailable && !p.enVenta)
                        return false;
                    if (filters.maxPrice && p.precio > filters.maxPrice)
                        return false;
                    if (filters.minPrice && p.precio < filters.minPrice)
                        return false;
                    return true;
                });
                // Si hay filtro de tipo, necesitamos consultar PokeAPI
                if (filters.type) {
                    const typeData = await fetchPokeAPI(`type/${filters.type.toLowerCase()}`);
                    const pokemonOfType = typeData.pokemon.map((p) => p.pokemon.name.toLowerCase());
                    filteredPrices = filteredPrices.filter((p) => pokemonOfType.includes(p.nombre.toLowerCase()));
                }
                // Limitar resultados
                results = filteredPrices.slice(0, filters.limit);
                return {
                    content: [
                        {
                            type: "text",
                            text: JSON.stringify({
                                total: filteredPrices.length,
                                showing: results.length,
                                filters: filters,
                                results: results,
                            }, null, 2),
                        },
                    ],
                };
            }
            case "list_pokemon_types": {
                const data = await fetchPokeAPI("type");
                const types = data.results
                    .map((t) => t.name)
                    .filter((name) => !["unknown", "shadow"].includes(name));
                return {
                    content: [
                        {
                            type: "text",
                            text: JSON.stringify({
                                total: types.length,
                                types: types,
                            }, null, 2),
                        },
                    ],
                };
            }
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
    }
    catch (error) {
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
// Iniciar el servidor
async function main() {
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error("MCP Pokemon Server running on stdio");
}
main().catch((error) => {
    console.error("Fatal error:", error);
    process.exit(1);
});
//# sourceMappingURL=index.js.map
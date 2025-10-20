import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from 'zod';
import { readFileSync } from 'fs';
import { join } from 'path';

const server = new McpServer({
	name: 'Pokemon Demo',
	version: '1.0.0'
});

// Cargar el inventario de Pokémon
let pokemonInventory: any[] = [];
try {
    const inventoryPath = join(process.cwd(), 'pokemon-gen1.json');
    const inventoryData = readFileSync(inventoryPath, 'utf-8');
    pokemonInventory = JSON.parse(inventoryData);
} catch (error) {
    console.error('Error al cargar el inventario de Pokémon:', error);
}

// Tools

// Tool para consultar el precio de un Pokémon
server.registerTool(
    'get_pokemon_price',
    {
        description: 'Get price and inventory information for a Pokemon',
        inputSchema: {
            pokemon: z.string().describe('Pokemon name or number')
        }
    },
    async (args: any) => {
        const query = String(args.pokemon ?? '').toLowerCase();
        
        // Buscar el Pokémon por nombre o número
        const pokemon = pokemonInventory.find(p => 
            p.nombre.toLowerCase() === query || 
            p.numero.toString() === query ||
            p.numero.toString().padStart(3, '0') === query
        );

        if (!pokemon) {
            return {
                content: [
                    {
                        type: 'text',
                        text: JSON.stringify({ error: `Pokemon "${args.pokemon}" not found` })
                    }
                ]
            };
        }

        // Devolver datos estructurados en JSON
        const result = {
            numero: pokemon.numero,
            nombre: pokemon.nombre,
            precio: pokemon.precio,
            enVenta: pokemon.enVenta,
            estado: pokemon.estado,
            inventario: {
                total: pokemon.inventario.total,
                disponibles: pokemon.inventario.disponibles,
                vendidos: pokemon.inventario.vendidos
            }
        };

        return {
            content: [
                {
                    type: 'text',
                    text: JSON.stringify(result)
                }
            ]
        };
    }
);

// Tool to search Pokemon by type and price
server.registerTool(
    'search_pokemon',
    {
        description: 'Search Pokemon by type and/or maximum price',
        inputSchema: {
            type: z.string().optional().describe('Pokemon type (Fire, Water, Grass, etc.)'),
            max_price: z.number().optional().describe('Maximum price')
        }
    },
    async (args: any) => {
        let results = [...pokemonInventory];
        
        // Filter by price if specified
        if (args.max_price !== undefined) {
            results = results.filter(p => p.precio <= args.max_price);
        }
        
        // If type is specified, we need to check PokeAPI for each Pokemon
        if (args.type) {
            const typeFiltered = [];
            const targetType = String(args.type).toLowerCase();
            
            // Get type data from PokeAPI
            try {
                const response = await fetch(`https://pokeapi.co/api/v2/type/${targetType}`);
                if (response.ok) {
                    const typeData = await response.json();
                    const pokemonWithType = typeData.pokemon.map((p: any) => p.pokemon.name);
                    
                    // Filter our inventory by pokemon that have this type
                    results = results.filter(p => pokemonWithType.includes(p.nombre.toLowerCase()));
                }
            } catch (error) {
                console.error('Error fetching type data:', error);
            }
        }
        
        // Return only available Pokemon
        const available = results.filter(p => p.enVenta && p.inventario.disponibles > 0);
        
        return {
            content: [
                {
                    type: 'text',
                    text: JSON.stringify({
                        count: available.length,
                        results: available.map(p => ({
                            numero: p.numero,
                            nombre: p.nombre,
                            precio: p.precio,
                            disponibles: p.inventario.disponibles
                        }))
                    })
                }
            ]
        };
    }
);

// Tool to fetch Pokemon info by name from PokeAPI
server.registerTool(
    'get_pokemon_info',
    {
        description: 'Get detailed Pokemon information from PokeAPI',
        inputSchema: {
            pokemon: z.string().describe('Pokemon name or number')
        }
    },
    async (args: any) => {
        const pokemon = String(args.pokemon ?? '').toLowerCase();
        const response = await fetch(`https://pokeapi.co/api/v2/pokemon/${pokemon}`);
        if (!response.ok) {
            return {
                content: [
                    {
                        type: 'text',
                        text: JSON.stringify({ error: `Pokemon "${pokemon}" not found` })
                    }
                ]
            };
        }

        const data = await response.json();

        // Return simplified info
        const result = {
            id: data.id,
            name: data.name,
            height: data.height,
            weight: data.weight,
            types: data.types.map((t: any) => t.type.name),
            abilities: data.abilities.map((a: any) => a.ability.name),
            stats: data.stats.map((s: any) => ({
                name: s.stat.name,
                value: s.base_stat
            }))
        };

        return {
            content: [
                {
                    type: 'text',
                    text: JSON.stringify(result)
                }
            ]
        };
    }
);

// Tool to list all available Pokemon types
server.registerTool(
    'list_pokemon_types',
    {
        description: 'List all available Pokemon types',
        inputSchema: {}
    },
    async (args: any) => {
        const response = await fetch('https://pokeapi.co/api/v2/type');
        if (!response.ok) {
            return {
                content: [
                    {
                        type: 'text',
                        text: JSON.stringify({ error: 'Failed to fetch types' })
                    }
                ]
            };
        }

        const data = await response.json();
        const types = data.results.map((t: any) => t.name);

        return {
            content: [
                {
                    type: 'text',
                    text: JSON.stringify({ types })
                }
            ]
        };
    }
);

const transport = new StdioServerTransport();

async function main() {
    await server.connect(transport);
}

main().catch((err) => {
    // Log and rethrow to ensure non-zero exit without referencing Node types
    // eslint-disable-next-line no-console
    console.error('Error al iniciar el servidor MCP:', err);
    throw err;
});

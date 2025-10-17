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
    'precio-pokemon',
    {
        description: 'Consulta el precio y disponibilidad de un Pokémon de primera generación',
        inputSchema: {
            pokemon: z.string().describe('Nombre o número del Pokémon')
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
                        text: `No se encontró el Pokémon "${args.pokemon}" en el inventario.`
                    }
                ]
            };
        }

        const info = `
🎮 INFORMACIÓN DE VENTA - Pokémon #${pokemon.numero.toString().padStart(3, '0')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📛 Nombre: ${pokemon.nombre.charAt(0).toUpperCase() + pokemon.nombre.slice(1)}
💰 Precio: $${pokemon.precio}
📊 Estado: ${pokemon.estado.toUpperCase()}
🏪 En venta: ${pokemon.enVenta ? 'SÍ' : 'NO'}

📦 INVENTARIO:
   • Total de unidades: ${pokemon.inventario.total}
   • Disponibles: ${pokemon.inventario.disponibles}
   • Vendidos: ${pokemon.inventario.vendidos}

${pokemon.inventario.disponibles === 0 ? '⚠️  ¡AGOTADO! No hay unidades disponibles' : 
  pokemon.inventario.disponibles <= 2 ? '⚠️  ¡ÚLTIMAS UNIDADES! Stock limitado' : 
  '✅ Disponible para compra'}
`;

        return {
            content: [
                {
                    type: 'text',
                    text: info
                }
            ]
        };
    }
);

// Tool to fetch Pokemon info by name
server.registerTool(
    'info-pokemon',
    {
        description: 'Tool to fetch Pokemon info by name',

        inputSchema: {
            pokemon: z.string().describe('Pokemon name')
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
                        text: `No se encontró información para el pokemon ${pokemon} (status ${response.status})`
                    }
                ]
            };
        }

        const data = await response.json();

        return {
            content: [
                {
                    type: 'text',
                    text: JSON.stringify(data, null, 2)
                }
            ]
        };
    }
);

// Tool to list Pokemon by ability
server.registerTool(
    'list-pokemon-type',
    {
        description: 'Tool to list Pokemons that have a given type',
        inputSchema: {
            type: z.string().describe('Type name')
        }
    },
    async (args: any) => {
        const type = String(args.type ?? '').toLowerCase();
        // Use the /type/{name} endpoint which lists pokemons with that type
        const response = await fetch(`https://pokeapi.co/api/v2/type/${type}`);
        if (!response.ok) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `No se encontró la habilidad ${type} (status ${response.status})`
                    }
                ]
            };
        }

        const dataType = await response.json();

        return {
            content: [
                {
                    type: 'text',
                    text: JSON.stringify(dataType, null, 2)
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

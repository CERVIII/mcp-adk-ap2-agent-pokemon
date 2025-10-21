#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";
import { readFile, writeFile, mkdir } from "fs/promises";
import { existsSync } from "fs";
import { fileURLToPath } from "url";
import { dirname, join } from "path";
import jwt from "jsonwebtoken";
import crypto from "crypto";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// ========================================
// RSA Key Persistence for JWT Signatures
// ========================================

/**
 * Load existing RSA keys from disk or generate new ones if they don't exist.
 * Keys are stored in mcp-server/keys/ directory for persistence across restarts.
 */
async function loadOrGenerateRSAKeys(): Promise<{ privateKey: string; publicKey: string }> {
  const keysDir = join(__dirname, '..', 'keys');
  const privateKeyPath = join(keysDir, 'merchant_private.pem');
  const publicKeyPath = join(keysDir, 'merchant_public.pem');

  try {
    // Try to load existing keys
    if (existsSync(privateKeyPath) && existsSync(publicKeyPath)) {
      console.error('🔑 Loading existing RSA keys from disk...');
      const privateKey = await readFile(privateKeyPath, 'utf8');
      const publicKey = await readFile(publicKeyPath, 'utf8');
      console.error('✅ RSA keys loaded successfully');
      console.error('📝 Public key preview:', publicKey.substring(0, 100) + '...');
      return { privateKey, publicKey };
    }
  } catch (error) {
    console.error('⚠️  Error loading keys, will generate new ones:', error);
  }

  // Generate new keys if they don't exist
  console.error('🔐 Generating new RSA key pair for merchant signatures...');
  const { privateKey, publicKey } = crypto.generateKeyPairSync('rsa', {
    modulusLength: 2048,
    publicKeyEncoding: {
      type: 'spki',
      format: 'pem'
    },
    privateKeyEncoding: {
      type: 'pkcs8',
      format: 'pem'
    }
  });

  // Save keys to disk
  try {
    // Ensure keys directory exists
    await mkdir(keysDir, { recursive: true });
    
    // Write keys with proper permissions
    await writeFile(privateKeyPath, privateKey, { mode: 0o600 }); // Read/write for owner only
    await writeFile(publicKeyPath, publicKey, { mode: 0o644 });   // Read for all
    
    console.error('� RSA keys saved to disk');
    console.error('   Private key: keys/merchant_private.pem (600)');
    console.error('   Public key:  keys/merchant_public.pem (644)');
    console.error('📝 Public key preview:', publicKey.substring(0, 100) + '...');
  } catch (error) {
    console.error('❌ Error saving keys to disk:', error);
    console.error('⚠️  Keys will only exist in memory for this session');
  }

  return { privateKey, publicKey };
}

// Load keys at startup
const keyPair = await loadOrGenerateRSAKeys();
const MERCHANT_PRIVATE_KEY = keyPair.privateKey;
const MERCHANT_PUBLIC_KEY = keyPair.publicKey;

// Tipos para los datos de Pokémon locales
interface PokemonPrice {
  numero: number;
  nombre: string;
  precio: number;
  enVenta: boolean;
  estado: string;
  inventario: {
    total: number;
    disponibles: number;
    vendidos: number;
  };
}

// ========================================
// AP2 Protocol Types
// ========================================

interface PaymentAmount {
  currency: string;
  value: number;
}

interface DisplayItem {
  label: string;
  amount: PaymentAmount;
}

interface PaymentMethodData {
  supported_methods: string;
  data: {
    payment_processor_url: string;
  };
}

interface PaymentDetails {
  id: string;
  displayItems: DisplayItem[];
  shipping_options: null;
  modifiers: null;
  total: {
    label: string;
    amount: PaymentAmount;
  };
}

interface PaymentOptions {
  requestPayerName: boolean;
  requestPayerEmail: boolean;
  requestPayerPhone: boolean;
  requestShipping: boolean;
  shippingType: null;
}

interface PaymentRequest {
  method_data: PaymentMethodData[];
  details: PaymentDetails;
  options: PaymentOptions;
}

interface CartMandateContents {
  id: string;
  user_signature_required: boolean;
  user_cart_confirmation_required: boolean;
  merchant_name: string;
  payment_request: PaymentRequest;
  cart_expiry?: string | null;
}

interface CartMandate {
  contents: CartMandateContents;
  merchant_signature: string;
  timestamp: string;
}

interface CartItem {
  product_id: string;
  quantity: number;
}

// Caché para los datos de precios
let pokemonPricesCache: PokemonPrice[] | null = null;

// Carrito actual del usuario (almacenado en memoria)
let currentCart: CartMandate | null = null;

// Función para cargar los precios de Pokémon
async function loadPokemonPrices(): Promise<PokemonPrice[]> {
  if (pokemonPricesCache) {
    return pokemonPricesCache;
  }

  try {
    // Intentar cargar desde la raíz del proyecto
    const pokemonDataPath = join(__dirname, "../../pokemon-gen1.json");
    const data = await readFile(pokemonDataPath, "utf-8");
    pokemonPricesCache = JSON.parse(data);
    return pokemonPricesCache!;
  } catch (error) {
    console.error("Error loading pokemon prices:", error);
    return [];
  }
}

// Función para hacer peticiones a PokeAPI
async function fetchPokeAPI(endpoint: string): Promise<any> {
  const response = await fetch(`https://pokeapi.co/api/v2/${endpoint}`);
  if (!response.ok) {
    throw new Error(`PokeAPI error: ${response.statusText}`);
  }
  return response.json();
}

// ========================================
// AP2 Helper Functions
// ========================================

/**
 * Generate a unique cart ID
 */
function generateCartId(): string {
  const randomHex = Math.random().toString(16).substring(2, 10);
  return `cart_pokemon_${randomHex}`;
}

/**
 * Generate a unique order ID
 */
function generateOrderId(): string {
  const randomHex = Math.random().toString(16).substring(2, 10);
  return `order_pokemon_${randomHex}`;
}

/**
 * Generate merchant signature for cart as a JWT RS256
 * 
 * Creates a real JWT signed with the merchant's private RSA key.
 * The JWT contains cart_id, merchant info, and timestamps.
 * 
 * @param cartId - The cart identifier to sign
 * @returns Base64url-encoded JWT string (header.payload.signature)
 */
function generateMerchantSignature(cartId: string): string {
  const now = Math.floor(Date.now() / 1000); // Unix timestamp in seconds
  
  const payload = {
    iss: "PokeMart",                    // Issuer (merchant name)
    sub: cartId,                        // Subject (cart ID)
    iat: now,                           // Issued at
    exp: now + (60 * 60),              // Expires in 1 hour
    cart_id: cartId,
    merchant: "PokeMart - Primera Generación"
  };
  
  // Sign with RS256 algorithm using merchant's private key
  const token = jwt.sign(payload, MERCHANT_PRIVATE_KEY, { algorithm: 'RS256' });
  
  // Log JWT structure for debugging
  const parts = token.split('.');
  console.error(`🔐 Generated JWT merchant signature: ${parts.length} parts (${token.substring(0, 50)}...)`);
  
  return token;
}

/**
 * Get current ISO timestamp
 */
function getCurrentTimestamp(): string {
  return new Date().toISOString();
}

/**
 * Create a CartMandate following AP2 protocol
 */
async function createCartMandate(items: CartItem[]): Promise<CartMandate> {
  const prices = await loadPokemonPrices();
  const displayItems: DisplayItem[] = [];
  let totalAmount = 0;

  // Process each item
  for (const item of items) {
    const pokemon = prices.find(
      (p) => p.numero.toString() === item.product_id
    );

    if (!pokemon) {
      throw new Error(
        `Pokemon #${item.product_id} not found in catalog`
      );
    }

    if (!pokemon.enVenta) {
      throw new Error(`Pokemon ${pokemon.nombre} is not available for sale`);
    }

    if (item.quantity > pokemon.inventario.disponibles) {
      throw new Error(
        `Only ${pokemon.inventario.disponibles} ${pokemon.nombre} available, requested ${item.quantity}`
      );
    }

    const itemTotal = pokemon.precio * item.quantity;
    totalAmount += itemTotal;

    displayItems.push({
      label: `${pokemon.nombre.charAt(0).toUpperCase() + pokemon.nombre.slice(1)} (x${item.quantity})`,
      amount: {
        currency: "USD",
        value: itemTotal,
      },
    });
  }

  // Create CartMandate structure following AP2 specification
  const cartId = generateCartId();
  const orderId = generateOrderId();
  const timestamp = getCurrentTimestamp();

  const cartMandate: CartMandate = {
    contents: {
      id: cartId,
      user_signature_required: false,
      user_cart_confirmation_required: false,
      merchant_name: "PokeMart - Primera Generación",
      payment_request: {
        method_data: [
          {
            supported_methods: "CARD",
            data: {
              payment_processor_url: "http://localhost:8003/a2a/processor",
            },
          },
        ],
        details: {
          id: orderId,
          displayItems: displayItems,
          shipping_options: null,
          modifiers: null,
          total: {
            label: "Total",
            amount: {
              currency: "USD",
              value: totalAmount,
            },
          },
        },
        options: {
          requestPayerName: false,
          requestPayerEmail: false,
          requestPayerPhone: false,
          requestShipping: false,
          shippingType: null,
        },
      },
      cart_expiry: null,
    },
    merchant_signature: generateMerchantSignature(cartId),
    timestamp: timestamp,
  };

  // Guardar el carrito actual en memoria
  currentCart = cartMandate;

  return cartMandate;
}

/**
 * Format cart mandate for display
 */
function formatCartMandateDisplay(cartMandate: CartMandate): string {
  const items = cartMandate.contents.payment_request.details.displayItems;
  const total = cartMandate.contents.payment_request.details.total.amount.value;

  let output = "🛒 CARRITO DE COMPRA CREADO\n";
  output += "━".repeat(50) + "\n\n";
  output += "📋 Items:\n";

  items.forEach((item) => {
    output += `  • ${item.label}: $${item.amount.value}\n`;
  });

  output += `\n💰 TOTAL: $${total}\n\n`;
  output += `🆔 Cart ID: ${cartMandate.contents.id}\n`;
  output += `📅 Timestamp: ${cartMandate.timestamp}\n\n`;
  output += "✅ CartMandate listo para el proceso de pago AP2\n\n";
  output += "📄 CartMandate completo (JSON):\n";
  output += "```json\n";
  output += JSON.stringify(cartMandate, null, 2);
  output += "\n```";

  return output;
}

// Definición de las tools disponibles
const TOOLS: Tool[] = [
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

// Crear el servidor MCP
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
              text: JSON.stringify(
                {
                  id: data.id,
                  name: data.name,
                  height: data.height,
                  weight: data.weight,
                  types: data.types.map((t: any) => t.type.name),
                  abilities: data.abilities.map((a: any) => ({
                    name: a.ability.name,
                    isHidden: a.is_hidden,
                  })),
                  stats: data.stats.map((s: any) => ({
                    name: s.stat.name,
                    value: s.base_stat,
                  })),
                  sprites: {
                    front_default: data.sprites.front_default,
                    front_shiny: data.sprites.front_shiny,
                  },
                },
                null,
                2
              ),
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

        const found = prices.find(
          (p) =>
            p.nombre.toLowerCase() === pokemonLower ||
            p.numero.toString() === pokemon
        );

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
        let results: any[] = [];

        // Filtrar por precio y disponibilidad
        let filteredPrices = prices.filter((p) => {
          if (filters.onlyAvailable && !p.enVenta) return false;
          if (filters.maxPrice && p.precio > filters.maxPrice) return false;
          if (filters.minPrice && p.precio < filters.minPrice) return false;
          return true;
        });

        // Si hay filtro de tipo, necesitamos consultar PokeAPI
        if (filters.type) {
          const typeData = await fetchPokeAPI(
            `type/${filters.type.toLowerCase()}`
          );
          const pokemonOfType = typeData.pokemon.map((p: any) =>
            p.pokemon.name.toLowerCase()
          );

          filteredPrices = filteredPrices.filter((p) =>
            pokemonOfType.includes(p.nombre.toLowerCase())
          );
        }

        // Limitar resultados
        results = filteredPrices.slice(0, filters.limit);

        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(
                {
                  total: filteredPrices.length,
                  showing: results.length,
                  filters: filters,
                  results: results,
                },
                null,
                2
              ),
            },
          ],
        };
      }

      case "list_pokemon_types": {
        const data = await fetchPokeAPI("type");
        const types = data.results
          .map((t: any) => t.name)
          .filter((name: string) => !["unknown", "shadow"].includes(name));

        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(
                {
                  total: types.length,
                  types: types,
                },
                null,
                2
              ),
            },
          ],
        };
      }

      case "create_pokemon_cart": {
        const schema = z.object({
          items: z.array(
            z.object({
              product_id: z.string(),
              quantity: z.number().int().positive().default(1),
            })
          ),
        });
        const { items } = schema.parse(args);

        const cartMandate = await createCartMandate(items);
        
        // Return the CartMandate as JSON for programmatic access
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(cartMandate, null, 2),
            },
          ],
        };
      }

      case "get_pokemon_product": {
        const schema = z.object({
          product_id: z.string(),
        });
        const { product_id } = schema.parse(args);

        // Get price info
        const prices = await loadPokemonPrices();
        const priceInfo = prices.find((p) => p.numero.toString() === product_id);

        if (!priceInfo) {
          return {
            content: [
              {
                type: "text",
                text: `Pokemon #${product_id} not found in catalog. Only Gen 1 Pokemon (1-151) are available.`,
              },
            ],
          };
        }

        // Get detailed info from PokeAPI
        let pokeApiInfo = null;
        try {
          pokeApiInfo = await fetchPokeAPI(`pokemon/${product_id}`);
        } catch (error) {
          // If PokeAPI fails, just return price info
        }

        const productInfo = {
          product_id: product_id,
          name: priceInfo.nombre,
          price: priceInfo.precio,
          currency: "USD",
          available: priceInfo.enVenta,
          stock: priceInfo.inventario.disponibles,
          total_inventory: priceInfo.inventario.total,
          sold: priceInfo.inventario.vendidos,
          ...(pokeApiInfo && {
            types: pokeApiInfo.types.map((t: any) => t.type.name),
            height: pokeApiInfo.height,
            weight: pokeApiInfo.weight,
            abilities: pokeApiInfo.abilities.map((a: any) => a.ability.name),
          }),
        };

        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(productInfo, null, 2),
            },
          ],
        };
      }

      case "get_current_cart": {
        // No need to parse args - this tool takes no parameters
        
        if (!currentCart) {
          return {
            content: [
              {
                type: "text",
                text: JSON.stringify({
                  message: "🛒 Tu carrito está vacío",
                  status: "empty",
                  suggestion: "Usa create_pokemon_cart para agregar Pokémon a tu carrito"
                }, null, 2),
              },
            ],
          };
        }

        // Return formatted cart information
        const items = currentCart.contents.payment_request.details.displayItems;
        const total = currentCart.contents.payment_request.details.total.amount.value;

        const cartSummary = {
          status: "active",
          cart_id: currentCart.contents.id,
          merchant: currentCart.contents.merchant_name,
          created_at: currentCart.timestamp,
          items: items.map(item => ({
            description: item.label,
            price_usd: item.amount.value
          })),
          total_usd: total,
          currency: "USD",
          ready_for_payment: true
        };

        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(cartSummary, null, 2),
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

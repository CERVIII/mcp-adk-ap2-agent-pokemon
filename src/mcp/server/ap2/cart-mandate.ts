/**
 * CartMandate Creation
 * AP2 Protocol CartMandate generation with JWT signatures
 */

import jwt from "jsonwebtoken";
import type { CartItem, CartMandate, DisplayItem } from "../types/index.js";
import { loadPokemonPrices } from "../utils/index.js";
import { setCurrentCart } from "./cart-state.js";

// These will be injected from the main index
let MERCHANT_PRIVATE_KEY: string;

export function setMerchantPrivateKey(key: string): void {
  MERCHANT_PRIVATE_KEY = key;
}

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
export async function createCartMandate(items: CartItem[]): Promise<CartMandate> {
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
      // Extension field: preserve original items for inventory management
      items: items,
    },
    merchant_signature: generateMerchantSignature(cartId),
    timestamp: timestamp,
  };

  // Guardar el carrito actual en memoria
  setCurrentCart(cartMandate);

  return cartMandate;
}

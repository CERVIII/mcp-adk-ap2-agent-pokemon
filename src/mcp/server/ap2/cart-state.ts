/**
 * Cart State Management
 * In-memory storage of current cart
 */

import type { CartMandate } from "../types/index.js";

// Carrito actual del usuario (almacenado en memoria)
let currentCart: CartMandate | null = null;

/**
 * Get the current cart
 */
export function getCurrentCart(): CartMandate | null {
  return currentCart;
}

/**
 * Set the current cart
 */
export function setCurrentCart(cart: CartMandate | null): void {
  currentCart = cart;
}

/**
 * Clear the current cart
 */
export function clearCart(): void {
  currentCart = null;
}

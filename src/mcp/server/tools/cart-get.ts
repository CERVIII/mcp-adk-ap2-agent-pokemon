/**
 * Tool: get_current_cart
 * Get the current shopping cart
 */

import { getCurrentCart } from "../ap2/index.js";

export async function getCurrentCartTool() {
  const currentCart = getCurrentCart();
  
  if (!currentCart) {
    return {
      content: [
        {
          type: "text" as const,
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
        type: "text" as const,
        text: JSON.stringify(cartSummary, null, 2),
      },
    ],
  };
}

/**
 * Cart Mandate Formatting
 * Display formatting for CartMandate output
 */

import type { CartMandate } from "../types/index.js";

/**
 * Format cart mandate for display
 */
export function formatCartMandateDisplay(cartMandate: CartMandate): string {
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

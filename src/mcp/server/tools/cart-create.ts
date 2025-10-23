/**
 * Tool: create_pokemon_cart
 * Create a shopping cart with Pokemon items (AP2 CartMandate)
 */

import { z } from "zod";
import { createCartMandate } from "../ap2/index.js";

export const createPokemonCartSchema = z.object({
  items: z.array(
    z.object({
      product_id: z.string().describe("Pokemon number (1-151)"),
      quantity: z.number().int().positive().default(1).describe("Quantity to purchase"),
    })
  ).describe("List of items to add to cart"),
});

export type CreatePokemonCartArgs = z.infer<typeof createPokemonCartSchema>;

export async function createPokemonCart(args: CreatePokemonCartArgs) {
  const { items } = createPokemonCartSchema.parse(args);

  const cartMandate = await createCartMandate(items);
  
  // Return the CartMandate as JSON for programmatic access
  return {
    content: [
      {
        type: "text" as const,
        text: JSON.stringify(cartMandate, null, 2),
      },
    ],
  };
}

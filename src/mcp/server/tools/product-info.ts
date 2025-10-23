/**
 * Tool: get_pokemon_product
 * Get complete product information (price + PokeAPI data)
 */

import { z } from "zod";
import { loadPokemonPrices, fetchPokeAPI } from "../utils/index.js";

export const getPokemonProductSchema = z.object({
  product_id: z.string().describe("Pokemon number (1-151)"),
});

export type GetPokemonProductArgs = z.infer<typeof getPokemonProductSchema>;

export async function getPokemonProduct(args: GetPokemonProductArgs) {
  const { product_id } = getPokemonProductSchema.parse(args);

  // Get price info
  const prices = await loadPokemonPrices();
  const priceInfo = prices.find((p) => p.numero.toString() === product_id);

  if (!priceInfo) {
    return {
      content: [
        {
          type: "text" as const,
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
        type: "text" as const,
        text: JSON.stringify(productInfo, null, 2),
      },
    ],
  };
}

/**
 * Tool: get_pokemon_price
 * Get Pokemon price and inventory information
 */

import { z } from "zod";
import { loadPokemonPrices } from "../utils/index.js";

export const getPokemonPriceSchema = z.object({
  pokemon: z.string().describe("Pokemon name or number"),
});

export type GetPokemonPriceArgs = z.infer<typeof getPokemonPriceSchema>;

export async function getPokemonPrice(args: GetPokemonPriceArgs) {
  const { pokemon } = getPokemonPriceSchema.parse(args);

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
          type: "text" as const,
          text: `Pokémon "${pokemon}" not found in price catalog. Only Gen 1 Pokémon (1-151) are available.`,
        },
      ],
    };
  }

  return {
    content: [
      {
        type: "text" as const,
        text: JSON.stringify(found, null, 2),
      },
    ],
  };
}

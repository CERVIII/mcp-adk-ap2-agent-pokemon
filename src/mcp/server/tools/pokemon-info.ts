/**
 * Tool: get_pokemon_info
 * Get detailed Pokemon information from PokeAPI
 */

import { z } from "zod";
import { fetchPokeAPI } from "../utils/index.js";

export const getPokemonInfoSchema = z.object({
  pokemon: z.string().describe("Pokemon name or ID number"),
});

export type GetPokemonInfoArgs = z.infer<typeof getPokemonInfoSchema>;

export async function getPokemonInfo(args: GetPokemonInfoArgs) {
  const { pokemon } = getPokemonInfoSchema.parse(args);

  const data = await fetchPokeAPI(`pokemon/${pokemon.toLowerCase()}`);

  return {
    content: [
      {
        type: "text" as const,
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

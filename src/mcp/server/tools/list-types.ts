/**
 * Tool: list_pokemon_types
 * List all available Pokemon types from PokeAPI
 */

import { fetchPokeAPI } from "../utils/index.js";

export async function listPokemonTypes() {
  const data = await fetchPokeAPI("type");
  const types = data.results
    .map((t: any) => t.name)
    .filter((name: string) => !["unknown", "shadow"].includes(name));

  return {
    content: [
      {
        type: "text" as const,
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

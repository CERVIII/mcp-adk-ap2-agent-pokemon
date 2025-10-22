/**
 * Tool: search_pokemon
 * Search Pokemon with filters (type, price, availability)
 */

import { z } from "zod";
import { loadPokemonPrices, fetchPokeAPI } from "../utils/index.js";

export const searchPokemonSchema = z.object({
  type: z.string().optional().describe("Pokemon type filter"),
  maxPrice: z.number().optional().describe("Maximum price filter"),
  minPrice: z.number().optional().describe("Minimum price filter"),
  onlyAvailable: z.boolean().default(false).describe("Only show available Pokemon"),
  limit: z.number().default(10).describe("Maximum results to return"),
});

export type SearchPokemonArgs = z.infer<typeof searchPokemonSchema>;

export async function searchPokemon(args: SearchPokemonArgs) {
  const filters = searchPokemonSchema.parse(args);

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
        type: "text" as const,
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

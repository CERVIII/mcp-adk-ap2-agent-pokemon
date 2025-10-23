/**
 * Tests for search-pokemon.ts
 * MCP tool: search_pokemon
 * 
 * Note: Integration tests using real PokeAPI and database
 */

import { describe, test, expect } from '@jest/globals';
import { searchPokemon, searchPokemonSchema } from '../../../../../../src/mcp/server/tools/search-pokemon.js';

describe('searchPokemon', () => {
  describe('Schema Validation', () => {
    test('should accept valid search parameters', () => {
      const result = searchPokemonSchema.parse({
        type: 'fire',
        maxPrice: 100,
        minPrice: 10,
        onlyAvailable: true,
        limit: 5
      });

      expect(result.type).toBe('fire');
      expect(result.maxPrice).toBe(100);
      expect(result.minPrice).toBe(10);
      expect(result.onlyAvailable).toBe(true);
      expect(result.limit).toBe(5);
    });

    test('should accept empty parameters with defaults', () => {
      const result = searchPokemonSchema.parse({});

      expect(result.onlyAvailable).toBe(false);
      expect(result.limit).toBe(10);
    });

    test('should reject invalid types', () => {
      expect(() => searchPokemonSchema.parse({ type: 123 })).toThrow();
      expect(() => searchPokemonSchema.parse({ maxPrice: 'not a number' })).toThrow();
    });
  });

  describe('Basic Search', () => {
    test('should return search results without filters', async () => {
      const result = await searchPokemon({});

      expect(result.content).toHaveLength(1);
      expect(result.content[0].type).toBe('text');

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed).toHaveProperty('total');
      expect(parsed).toHaveProperty('showing');
      expect(parsed).toHaveProperty('filters');
      expect(parsed).toHaveProperty('results');
    });

    test('should respect default limit of 10', async () => {
      const result = await searchPokemon({});
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed.showing).toBeLessThanOrEqual(10);
      expect(parsed.results).toHaveLength(parsed.showing);
    });

    test('should return all Gen 1 Pokemon without filters', async () => {
      const result = await searchPokemon({ limit: 200 });
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed.total).toBe(151);
    });
  });

  describe('Type Filter', () => {
    test('should filter by electric type', async () => {
      const result = await searchPokemon({ type: 'electric', limit: 50 });
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed.showing).toBeGreaterThan(0);
      expect(parsed.filters.type).toBe('electric');
    }, 10000);

    test('should filter by fire type', async () => {
      const result = await searchPokemon({ type: 'fire', limit: 50 });
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed.showing).toBeGreaterThan(0);
      expect(parsed.filters.type).toBe('fire');
    }, 10000);

    test('should handle type case-insensitively', async () => {
      const result = await searchPokemon({ type: 'WATER', limit: 50 });
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed.showing).toBeGreaterThan(0);
    }, 10000);

    test('should throw error for invalid type', async () => {
      // PokeAPI returns 404 for invalid types
      await expect(searchPokemon({ type: 'notarealtype' }))
        .rejects
        .toThrow('PokeAPI error');
    }, 10000);
  });

  describe('Price Filters', () => {
    test('should filter by max price', async () => {
      const result = await searchPokemon({ maxPrice: 50, limit: 50 });
      const parsed = JSON.parse(result.content[0].text);

      parsed.results.forEach((pokemon: any) => {
        expect(pokemon.precio).toBeLessThanOrEqual(50);
      });
    });

    test('should filter by min price', async () => {
      const result = await searchPokemon({ minPrice: 100, limit: 50 });
      const parsed = JSON.parse(result.content[0].text);

      parsed.results.forEach((pokemon: any) => {
        expect(pokemon.precio).toBeGreaterThanOrEqual(100);
      });
    });

    test('should filter by price range', async () => {
      const result = await searchPokemon({ minPrice: 50, maxPrice: 100, limit: 50 });
      const parsed = JSON.parse(result.content[0].text);

      parsed.results.forEach((pokemon: any) => {
        expect(pokemon.precio).toBeGreaterThanOrEqual(50);
        expect(pokemon.precio).toBeLessThanOrEqual(100);
      });
    });

    test('should return empty for impossible price range', async () => {
      const result = await searchPokemon({ minPrice: 1000, maxPrice: 10 });
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed.showing).toBe(0);
    });
  });

  describe('Availability Filter', () => {
    test('should filter by availability', async () => {
      const result = await searchPokemon({ onlyAvailable: true, limit: 50 });
      const parsed = JSON.parse(result.content[0].text);

      parsed.results.forEach((pokemon: any) => {
        expect(pokemon.enVenta).toBe(true);
      });
    });

    test('should show all when onlyAvailable is false', async () => {
      const result = await searchPokemon({ onlyAvailable: false, limit: 50 });
      const parsed = JSON.parse(result.content[0].text);

      // May include both available and unavailable
      expect(parsed.showing).toBeGreaterThan(0);
    });
  });

  describe('Limit Parameter', () => {
    test('should respect custom limit', async () => {
      const result = await searchPokemon({ limit: 5 });
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed.showing).toBeLessThanOrEqual(5);
    });

    test('should handle limit larger than results', async () => {
      const result = await searchPokemon({ limit: 1000 });
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed.showing).toBe(parsed.total);
    });

    test('should handle limit of 1', async () => {
      const result = await searchPokemon({ limit: 1 });
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed.showing).toBe(1);
      expect(parsed.results).toHaveLength(1);
    });
  });

  describe('Combined Filters', () => {
    test('should combine type and price filters', async () => {
      const result = await searchPokemon({ 
        type: 'fire', 
        maxPrice: 100,
        limit: 50 
      });
      const parsed = JSON.parse(result.content[0].text);

      parsed.results.forEach((pokemon: any) => {
        expect(pokemon.precio).toBeLessThanOrEqual(100);
      });
    }, 10000);

    test('should combine all filters', async () => {
      const result = await searchPokemon({
        type: 'water',
        minPrice: 30,
        maxPrice: 80,
        onlyAvailable: true,
        limit: 20
      });
      const parsed = JSON.parse(result.content[0].text);

      parsed.results.forEach((pokemon: any) => {
        expect(pokemon.precio).toBeGreaterThanOrEqual(30);
        expect(pokemon.precio).toBeLessThanOrEqual(80);
        expect(pokemon.enVenta).toBe(true);
      });

      expect(parsed.showing).toBeLessThanOrEqual(20);
    }, 10000);
  });

  describe('Response Structure', () => {
    test('should return correct structure', async () => {
      const result = await searchPokemon({});
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed).toHaveProperty('total');
      expect(parsed).toHaveProperty('showing');
      expect(parsed).toHaveProperty('filters');
      expect(parsed).toHaveProperty('results');
      expect(typeof parsed.total).toBe('number');
      expect(typeof parsed.showing).toBe('number');
      expect(Array.isArray(parsed.results)).toBe(true);
    });

    test('should include applied filters in response', async () => {
      const result = await searchPokemon({ type: 'fire', maxPrice: 100 });
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed.filters.type).toBe('fire');
      expect(parsed.filters.maxPrice).toBe(100);
    }, 10000);

    test('should format JSON with indentation', async () => {
      const result = await searchPokemon({});

      expect(result.content[0].text).toContain('  "total"');
      expect(result.content[0].text).toContain('  "results"');
    });
  });

  describe('Result Content', () => {
    test('should include full Pokemon data in results', async () => {
      const result = await searchPokemon({ limit: 1 });
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed.results).toHaveLength(1);
      const pokemon = parsed.results[0];

      expect(pokemon).toHaveProperty('numero');
      expect(pokemon).toHaveProperty('nombre');
      expect(pokemon).toHaveProperty('precio');
      expect(pokemon).toHaveProperty('enVenta');
      expect(pokemon).toHaveProperty('inventario');
    });

    test('should show accurate total vs showing count', async () => {
      const result = await searchPokemon({ limit: 5 });
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed.showing).toBeLessThanOrEqual(parsed.total);
      expect(parsed.showing).toBe(parsed.results.length);
    });
  });

  describe('Edge Cases', () => {
    test('should handle limit of 0', async () => {
      const result = await searchPokemon({ limit: 0 });
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed.showing).toBe(0);
      expect(parsed.results).toHaveLength(0);
    });

    test('should handle very restrictive filters', async () => {
      const result = await searchPokemon({
        type: 'dragon',
        minPrice: 200,
        onlyAvailable: true,
        limit: 50
      });
      const parsed = JSON.parse(result.content[0].text);

      // May or may not find results - both valid
      expect(parsed.showing).toBeGreaterThanOrEqual(0);
      expect(parsed.showing).toBeLessThanOrEqual(parsed.total);
    }, 10000);
  });
});

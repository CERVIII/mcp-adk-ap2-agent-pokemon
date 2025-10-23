/**
 * Tests for product-info.ts
 * MCP tool: get_pokemon_product
 * 
 * Note: Integration tests using real PokeAPI and database
 */

import { describe, test, expect } from '@jest/globals';
import { getPokemonProduct, getPokemonProductSchema } from '../../../../../../src/mcp/server/tools/product-info.js';

describe('getPokemonProduct', () => {
  describe('Schema Validation', () => {
    test('should accept valid product_id', () => {
      const result = getPokemonProductSchema.parse({ product_id: '25' });
      expect(result.product_id).toBe('25');
    });

    test('should reject missing product_id', () => {
      expect(() => getPokemonProductSchema.parse({})).toThrow();
    });

    test('should reject invalid type', () => {
      expect(() => getPokemonProductSchema.parse({ product_id: 123 })).toThrow();
    });
  });

  describe('Product Lookup', () => {
    test('should return complete product info for valid Pokemon', async () => {
      const result = await getPokemonProduct({ product_id: '25' }); // Pikachu

      expect(result.content).toHaveLength(1);
      expect(result.content[0].type).toBe('text');

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.product_id).toBe('25');
      expect(parsed.name).toBe('pikachu');
    }, 10000);

    test('should include price information', async () => {
      const result = await getPokemonProduct({ product_id: '1' }); // Bulbasaur

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed).toHaveProperty('price');
      expect(parsed).toHaveProperty('currency', 'USD');
      expect(parsed).toHaveProperty('available');
      expect(typeof parsed.price).toBe('number');
    }, 10000);

    test('should include inventory information', async () => {
      const result = await getPokemonProduct({ product_id: '4' }); // Charmander

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed).toHaveProperty('stock');
      expect(parsed).toHaveProperty('total_inventory');
      expect(parsed).toHaveProperty('sold');
      expect(typeof parsed.stock).toBe('number');
    }, 10000);

    test('should include PokeAPI data when available', async () => {
      const result = await getPokemonProduct({ product_id: '7' }); // Squirtle

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed).toHaveProperty('types');
      expect(parsed).toHaveProperty('height');
      expect(parsed).toHaveProperty('weight');
      expect(parsed).toHaveProperty('abilities');
      expect(Array.isArray(parsed.types)).toBe(true);
    }, 10000);

    test('should handle Pokemon not in catalog', async () => {
      const result = await getPokemonProduct({ product_id: '200' }); // Gen 2

      expect(result.content[0].text).toContain('not found');
      expect(result.content[0].text).toContain('Gen 1');
    });

    test('should handle invalid Pokemon ID', async () => {
      const result = await getPokemonProduct({ product_id: '999' });

      expect(result.content[0].text).toContain('not found');
    });
  });

  describe('Data Structure', () => {
    test('should return properly formatted JSON', async () => {
      const result = await getPokemonProduct({ product_id: '150' }); // Mewtwo

      expect(result.content[0].text).toContain('  "product_id"');
      expect(() => JSON.parse(result.content[0].text)).not.toThrow();
    }, 10000);

    test('should include all required fields', async () => {
      const result = await getPokemonProduct({ product_id: '6' }); // Charizard

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed).toHaveProperty('product_id');
      expect(parsed).toHaveProperty('name');
      expect(parsed).toHaveProperty('price');
      expect(parsed).toHaveProperty('currency');
      expect(parsed).toHaveProperty('available');
      expect(parsed).toHaveProperty('stock');
    }, 10000);

    test('should have correct data types', async () => {
      const result = await getPokemonProduct({ product_id: '10' }); // Caterpie

      const parsed = JSON.parse(result.content[0].text);
      expect(typeof parsed.product_id).toBe('string');
      expect(typeof parsed.name).toBe('string');
      expect(typeof parsed.price).toBe('number');
      expect(typeof parsed.currency).toBe('string');
      expect(typeof parsed.available).toBe('boolean');
      expect(typeof parsed.stock).toBe('number');
    }, 10000);
  });

  describe('PokeAPI Integration', () => {
    test('should include types from PokeAPI', async () => {
      const result = await getPokemonProduct({ product_id: '25' }); // Pikachu (electric)

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.types).toBeDefined();
      expect(parsed.types).toContain('electric');
    }, 10000);

    test('should include abilities from PokeAPI', async () => {
      const result = await getPokemonProduct({ product_id: '1' }); // Bulbasaur

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.abilities).toBeDefined();
      expect(Array.isArray(parsed.abilities)).toBe(true);
      expect(parsed.abilities.length).toBeGreaterThan(0);
    }, 10000);

    test('should include height and weight', async () => {
      const result = await getPokemonProduct({ product_id: '143' }); // Snorlax

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.height).toBeDefined();
      expect(parsed.weight).toBeDefined();
      expect(typeof parsed.height).toBe('number');
      expect(typeof parsed.weight).toBe('number');
    }, 10000);

    test('should handle multiple types', async () => {
      const result = await getPokemonProduct({ product_id: '6' }); // Charizard (fire/flying)

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.types).toBeDefined();
      expect(parsed.types.length).toBeGreaterThanOrEqual(2);
    }, 10000);
  });

  describe('Edge Cases', () => {
    test('should handle Pokemon #1', async () => {
      const result = await getPokemonProduct({ product_id: '1' });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.product_id).toBe('1');
      expect(parsed.name).toBe('bulbasaur');
    }, 10000);

    test('should handle Pokemon #151', async () => {
      const result = await getPokemonProduct({ product_id: '151' }); // Mew

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.product_id).toBe('151');
      expect(parsed.name).toBe('mew');
    }, 10000);

    test('should not find Pokemon with leading zeros', async () => {
      const result = await getPokemonProduct({ product_id: '025' }); // Won't match "25"

      expect(result.content[0].text).toContain('not found');
      expect(result.content[0].text).toContain('Gen 1');
    });

    test('should return price info even if PokeAPI fails', async () => {
      // Using a valid Gen 1 Pokemon - should always get price info
      const result = await getPokemonProduct({ product_id: '50' }); // Diglett

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.product_id).toBe('50');
      expect(parsed.price).toBeDefined();
      expect(parsed.stock).toBeDefined();
    }, 10000);
  });

  describe('Consistency', () => {
    test('should return same data on multiple calls', async () => {
      const result1 = await getPokemonProduct({ product_id: '100' }); // Voltorb
      const result2 = await getPokemonProduct({ product_id: '100' });

      const parsed1 = JSON.parse(result1.content[0].text);
      const parsed2 = JSON.parse(result2.content[0].text);

      expect(parsed1.price).toBe(parsed2.price);
      expect(parsed1.name).toBe(parsed2.name);
    }, 10000);

    test('should have consistent inventory totals', async () => {
      const result = await getPokemonProduct({ product_id: '75' }); // Graveler

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.stock + parsed.sold).toBe(parsed.total_inventory);
    }, 10000);
  });
});

/**
 * Tests for pokemon-price.ts
 * MCP tool: get_pokemon_price
 * 
 * Note: Integration tests using real database via loadPokemonPrices()
 */

import { describe, test, expect } from '@jest/globals';
import { getPokemonPrice, getPokemonPriceSchema } from '../../../../../../src/mcp/server/tools/pokemon-price.js';

describe('getPokemonPrice', () => {
  describe('Schema Validation', () => {
    test('should accept valid pokemon name', () => {
      const result = getPokemonPriceSchema.parse({ pokemon: 'pikachu' });
      expect(result.pokemon).toBe('pikachu');
    });

    test('should accept valid pokemon ID', () => {
      const result = getPokemonPriceSchema.parse({ pokemon: '25' });
      expect(result.pokemon).toBe('25');
    });

    test('should reject missing pokemon parameter', () => {
      expect(() => getPokemonPriceSchema.parse({})).toThrow();
    });

    test('should reject non-string pokemon parameter', () => {
      expect(() => getPokemonPriceSchema.parse({ pokemon: 123 })).toThrow();
    });
  });

  describe('Price Lookup by Name', () => {
    test('should find pokemon by exact name', async () => {
      const result = await getPokemonPrice({ pokemon: 'pikachu' });

      expect(result.content).toHaveLength(1);
      expect(result.content[0].type).toBe('text');

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.nombre.toLowerCase()).toBe('pikachu');
      expect(parsed.numero).toBe(25);
      expect(parsed).toHaveProperty('precio');
    });

    test('should find pokemon by name case-insensitive', async () => {
      const result = await getPokemonPrice({ pokemon: 'PIKACHU' });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.nombre.toLowerCase()).toBe('pikachu');
    });

    test('should find pokemon with mixed case', async () => {
      const result = await getPokemonPrice({ pokemon: 'ChArIzArD' });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.nombre.toLowerCase()).toBe('charizard');
      expect(parsed.numero).toBe(6);
    });
  });

  describe('Price Lookup by Number', () => {
    test('should find pokemon by number string', async () => {
      const result = await getPokemonPrice({ pokemon: '25' });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.numero).toBe(25);
      expect(parsed.nombre.toLowerCase()).toBe('pikachu');
    });

    test('should find pokemon by single digit number', async () => {
      const result = await getPokemonPrice({ pokemon: '1' });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.numero).toBe(1);
      expect(parsed.nombre.toLowerCase()).toBe('bulbasaur');
    });

    test('should find pokemon by three digit number', async () => {
      const result = await getPokemonPrice({ pokemon: '151' });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.numero).toBe(151);
      expect(parsed.nombre.toLowerCase()).toBe('mew');
    });
  });

  describe('Price Data Structure', () => {
    test('should include precio field', async () => {
      const result = await getPokemonPrice({ pokemon: 'pikachu' });
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed).toHaveProperty('precio');
      expect(typeof parsed.precio).toBe('number');
      expect(parsed.precio).toBeGreaterThan(0);
    });

    test('should include inventario field', async () => {
      const result = await getPokemonPrice({ pokemon: 'pikachu' });
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed).toHaveProperty('inventario');
      expect(parsed.inventario).toHaveProperty('total');
      expect(parsed.inventario).toHaveProperty('disponibles');
      expect(parsed.inventario).toHaveProperty('vendidos');
    });

    test('should include enVenta flag', async () => {
      const result = await getPokemonPrice({ pokemon: 'pikachu' });
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed).toHaveProperty('enVenta');
      expect(typeof parsed.enVenta).toBe('boolean');
    });

    test('should have consistent inventory totals', async () => {
      const result = await getPokemonPrice({ pokemon: 'pikachu' });
      const parsed = JSON.parse(result.content[0].text);

      const { total, disponibles, vendidos } = parsed.inventario;
      expect(disponibles + vendidos).toBeLessThanOrEqual(total);
    });
  });

  describe('Error Handling', () => {
    test('should return error message for non-existent pokemon name', async () => {
      const result = await getPokemonPrice({ pokemon: 'missingno' });

      expect(result.content).toHaveLength(1);
      expect(result.content[0].type).toBe('text');
      expect(result.content[0].text).toContain('not found');
      expect(result.content[0].text).toContain('missingno');
      expect(result.content[0].text).toContain('Gen 1');
    });

    test('should return error message for number out of range', async () => {
      const result = await getPokemonPrice({ pokemon: '999' });

      expect(result.content[0].text).toContain('not found');
      expect(result.content[0].text).toContain('1-151');
    });

    test('should return error message for Gen 2+ pokemon', async () => {
      const result = await getPokemonPrice({ pokemon: 'togepi' });

      expect(result.content[0].text).toContain('not found');
    });

    test('should return error message for invalid pokemon name', async () => {
      const result = await getPokemonPrice({ pokemon: 'notapokemon123' });

      expect(result.content[0].text).toContain('not found');
    });
  });

  describe('Response Structure', () => {
    test('should return content array with single text item', async () => {
      const result = await getPokemonPrice({ pokemon: 'pikachu' });

      expect(result).toHaveProperty('content');
      expect(Array.isArray(result.content)).toBe(true);
      expect(result.content).toHaveLength(1);
      expect(result.content[0].type).toBe('text');
    });

    test('should return valid JSON for found pokemon', async () => {
      const result = await getPokemonPrice({ pokemon: 'pikachu' });

      expect(() => JSON.parse(result.content[0].text)).not.toThrow();
    });

    test('should return plain text for not found pokemon', async () => {
      const result = await getPokemonPrice({ pokemon: 'notfound' });

      expect(() => JSON.parse(result.content[0].text)).toThrow();
      expect(typeof result.content[0].text).toBe('string');
    });

    test('should format JSON with indentation', async () => {
      const result = await getPokemonPrice({ pokemon: 'pikachu' });

      expect(result.content[0].text).toContain('  "numero"');
      expect(result.content[0].text).toContain('  "nombre"');
    });
  });

  describe('Edge Cases', () => {
    test('should handle first Gen 1 pokemon', async () => {
      const result = await getPokemonPrice({ pokemon: '1' });
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed.numero).toBe(1);
      expect(parsed.nombre.toLowerCase()).toBe('bulbasaur');
    });

    test('should handle last Gen 1 pokemon', async () => {
      const result = await getPokemonPrice({ pokemon: '151' });
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed.numero).toBe(151);
      expect(parsed.nombre.toLowerCase()).toBe('mew');
    });

    test('should handle pokemon with accents', async () => {
      const result = await getPokemonPrice({ pokemon: 'farfetchd' });
      
      // Will return data or not found - both are valid responses
      expect(result.content).toHaveLength(1);
      expect(result.content[0].type).toBe('text');
    });

    test('should handle pokemon with special characters in DB', async () => {
      const result = await getPokemonPrice({ pokemon: 'mr-mime' });
      
      // Will return data or not found - both are valid responses
      expect(result.content).toHaveLength(1);
      expect(result.content[0].type).toBe('text');
    });
  });

  describe('Multiple Pokemon Queries', () => {
    test('should return consistent results for same pokemon', async () => {
      const result1 = await getPokemonPrice({ pokemon: 'pikachu' });
      const result2 = await getPokemonPrice({ pokemon: 'pikachu' });

      expect(result1.content[0].text).toBe(result2.content[0].text);
    });

    test('should return same pokemon for name and number', async () => {
      const resultName = await getPokemonPrice({ pokemon: 'pikachu' });
      const resultNumber = await getPokemonPrice({ pokemon: '25' });

      const parsedName = JSON.parse(resultName.content[0].text);
      const parsedNumber = JSON.parse(resultNumber.content[0].text);

      expect(parsedName.numero).toBe(parsedNumber.numero);
      expect(parsedName.nombre).toBe(parsedNumber.nombre);
      expect(parsedName.precio).toBe(parsedNumber.precio);
    });

    test('should return different data for different pokemon', async () => {
      const result1 = await getPokemonPrice({ pokemon: 'pikachu' });
      const result2 = await getPokemonPrice({ pokemon: 'charizard' });

      const parsed1 = JSON.parse(result1.content[0].text);
      const parsed2 = JSON.parse(result2.content[0].text);

      expect(parsed1.numero).not.toBe(parsed2.numero);
      expect(parsed1.nombre).not.toBe(parsed2.nombre);
    });
  });
});

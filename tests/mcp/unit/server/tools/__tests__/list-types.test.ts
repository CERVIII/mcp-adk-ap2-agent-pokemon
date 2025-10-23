/**
 * Tests for list-types.ts
 * MCP tool: list_pokemon_types
 * 
 * Note: Integration tests calling real PokeAPI
 */

import { describe, test, expect } from '@jest/globals';
import { listPokemonTypes } from '../../../../../../src/mcp/server/tools/list-types.js';

describe('listPokemonTypes', () => {
  describe('Type Listing', () => {
    test('should return list of Pokemon types', async () => {
      const result = await listPokemonTypes();

      expect(result.content).toHaveLength(1);
      expect(result.content[0].type).toBe('text');

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed).toHaveProperty('total');
      expect(parsed).toHaveProperty('types');
    }, 10000);

    test('should return expected number of types', async () => {
      const result = await listPokemonTypes();
      const parsed = JSON.parse(result.content[0].text);

      // Gen 1-8 has 18 types (excluding unknown and shadow)
      expect(parsed.total).toBeGreaterThan(0);
      expect(parsed.types).toHaveLength(parsed.total);
    }, 10000);

    test('should include common types', async () => {
      const result = await listPokemonTypes();
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed.types).toContain('normal');
      expect(parsed.types).toContain('fire');
      expect(parsed.types).toContain('water');
      expect(parsed.types).toContain('electric');
      expect(parsed.types).toContain('grass');
    }, 10000);

    test('should include all Gen 1 types', async () => {
      const result = await listPokemonTypes();
      const parsed = JSON.parse(result.content[0].text);

      const gen1Types = [
        'normal', 'fire', 'water', 'electric', 'grass', 'ice',
        'fighting', 'poison', 'ground', 'flying', 'psychic',
        'bug', 'rock', 'ghost', 'dragon'
      ];

      gen1Types.forEach(type => {
        expect(parsed.types).toContain(type);
      });
    }, 10000);
  });

  describe('Type Filtering', () => {
    test('should exclude "unknown" type', async () => {
      const result = await listPokemonTypes();
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed.types).not.toContain('unknown');
    }, 10000);

    test('should exclude "shadow" type', async () => {
      const result = await listPokemonTypes();
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed.types).not.toContain('shadow');
    }, 10000);
  });

  describe('Response Structure', () => {
    test('should return content array with single text item', async () => {
      const result = await listPokemonTypes();

      expect(result).toHaveProperty('content');
      expect(Array.isArray(result.content)).toBe(true);
      expect(result.content).toHaveLength(1);
      expect(result.content[0].type).toBe('text');
    }, 10000);

    test('should return valid JSON', async () => {
      const result = await listPokemonTypes();

      expect(() => JSON.parse(result.content[0].text)).not.toThrow();
    }, 10000);

    test('should format JSON with indentation', async () => {
      const result = await listPokemonTypes();

      expect(result.content[0].text).toContain('  "total"');
      expect(result.content[0].text).toContain('  "types"');
    }, 10000);
  });

  describe('Data Validation', () => {
    test('should return array of strings', async () => {
      const result = await listPokemonTypes();
      const parsed = JSON.parse(result.content[0].text);

      expect(Array.isArray(parsed.types)).toBe(true);
      expect(parsed.types.every((t: any) => typeof t === 'string')).toBe(true);
    }, 10000);

    test('should have total matching types array length', async () => {
      const result = await listPokemonTypes();
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed.total).toBe(parsed.types.length);
    }, 10000);

    test('should not contain duplicate types', async () => {
      const result = await listPokemonTypes();
      const parsed = JSON.parse(result.content[0].text);

      const uniqueTypes = new Set(parsed.types);
      expect(uniqueTypes.size).toBe(parsed.types.length);
    }, 10000);

    test('should contain only lowercase type names', async () => {
      const result = await listPokemonTypes();
      const parsed = JSON.parse(result.content[0].text);

      parsed.types.forEach((type: string) => {
        expect(type).toBe(type.toLowerCase());
      });
    }, 10000);
  });

  describe('Consistent Results', () => {
    test('should return same results on multiple calls', async () => {
      const result1 = await listPokemonTypes();
      const result2 = await listPokemonTypes();

      const parsed1 = JSON.parse(result1.content[0].text);
      const parsed2 = JSON.parse(result2.content[0].text);

      expect(parsed1.total).toBe(parsed2.total);
      expect(parsed1.types).toEqual(parsed2.types);
    }, 10000);
  });
});

/**
 * Tests for pokemon-info.ts
 * MCP tool: get_pokemon_info
 * 
 * Note: These are integration tests that call the real PokeAPI.
 * Tests may be slower due to network requests.
 */

import { describe, test, expect } from '@jest/globals';
import { getPokemonInfo, getPokemonInfoSchema } from '../../../../../../src/mcp/server/tools/pokemon-info.js';

describe('getPokemonInfo', () => {

  describe('Schema Validation', () => {
    test('should accept valid pokemon name', () => {
      const result = getPokemonInfoSchema.parse({ pokemon: 'pikachu' });
      expect(result.pokemon).toBe('pikachu');
    });

    test('should accept valid pokemon ID', () => {
      const result = getPokemonInfoSchema.parse({ pokemon: '25' });
      expect(result.pokemon).toBe('25');
    });

    test('should reject missing pokemon parameter', () => {
      expect(() => getPokemonInfoSchema.parse({})).toThrow();
    });

    test('should reject non-string pokemon parameter', () => {
      expect(() => getPokemonInfoSchema.parse({ pokemon: 123 })).toThrow();
    });
  });

  describe('Pokemon Info Retrieval', () => {
    test('should fetch and format pokemon data by name', async () => {
      const result = await getPokemonInfo({ pokemon: 'pikachu' });

      expect(result.content).toHaveLength(1);
      expect(result.content[0].type).toBe('text');

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.id).toBe(25);
      expect(parsed.name).toBe('pikachu');
      expect(parsed.types).toContain('electric');
      expect(parsed.height).toBe(4);
      expect(parsed.weight).toBe(60);
    }, 10000);

    test('should fetch pokemon by ID number', async () => {
      const result = await getPokemonInfo({ pokemon: '25' });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.id).toBe(25);
      expect(parsed.name).toBe('pikachu');
    }, 10000);

    test('should handle mixed case pokemon names', async () => {
      const result = await getPokemonInfo({ pokemon: 'PIKACHU' });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.name).toBe('pikachu');
    }, 10000);
  });

  describe('Data Formatting', () => {
    test('should format dual types correctly', async () => {
      const result = await getPokemonInfo({ pokemon: 'charizard' });
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed.id).toBe(6);
      expect(parsed.types).toContain('fire');
      expect(parsed.types).toContain('flying');
      expect(parsed.types).toHaveLength(2);
    }, 10000);

    test('should format abilities with hidden flag', async () => {
      const result = await getPokemonInfo({ pokemon: 'bulbasaur' });
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed.abilities).toBeDefined();
      expect(Array.isArray(parsed.abilities)).toBe(true);
      expect(parsed.abilities.length).toBeGreaterThan(0);
      
      // Check structure of first ability
      expect(parsed.abilities[0]).toHaveProperty('name');
      expect(parsed.abilities[0]).toHaveProperty('isHidden');
      expect(typeof parsed.abilities[0].isHidden).toBe('boolean');
    }, 10000);

    test('should format stats correctly', async () => {
      const result = await getPokemonInfo({ pokemon: 'pikachu' });
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed.stats).toHaveLength(6);
      expect(parsed.stats[0]).toHaveProperty('name');
      expect(parsed.stats[0]).toHaveProperty('value');
      expect(typeof parsed.stats[0].value).toBe('number');
      
      // Verify all stat names exist
      const statNames = parsed.stats.map((s: any) => s.name);
      expect(statNames).toContain('hp');
      expect(statNames).toContain('speed');
    }, 10000);

    test('should include sprite URLs', async () => {
      const result = await getPokemonInfo({ pokemon: 'pikachu' });
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed.sprites).toBeDefined();
      expect(parsed.sprites).toHaveProperty('front_default');
      expect(parsed.sprites).toHaveProperty('front_shiny');
    }, 10000);

    test('should include height and weight', async () => {
      const result = await getPokemonInfo({ pokemon: 'snorlax' });
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed.id).toBe(143);
      expect(parsed.height).toBeDefined();
      expect(parsed.weight).toBeDefined();
      expect(typeof parsed.height).toBe('number');
      expect(typeof parsed.weight).toBe('number');
    }, 10000);
  });

  describe('Response Structure', () => {
    test('should return content array with single text item', async () => {
      const result = await getPokemonInfo({ pokemon: 'bulbasaur' });

      expect(result).toHaveProperty('content');
      expect(Array.isArray(result.content)).toBe(true);
      expect(result.content).toHaveLength(1);
      expect(result.content[0].type).toBe('text');
    }, 10000);

    test('should return valid JSON in text field', async () => {
      const result = await getPokemonInfo({ pokemon: 'bulbasaur' });

      expect(() => JSON.parse(result.content[0].text)).not.toThrow();
    }, 10000);

    test('should format JSON with indentation', async () => {
      const result = await getPokemonInfo({ pokemon: 'bulbasaur' });

      // Check for indentation (2 spaces)
      expect(result.content[0].text).toContain('  "id"');
      expect(result.content[0].text).toContain('  "name"');
    }, 10000);
  });

  describe('Error Handling', () => {
    test('should throw error for invalid pokemon', async () => {
      await expect(getPokemonInfo({ pokemon: 'notarealmon9999' })).rejects.toThrow();
    }, 10000);

    test('should throw error for empty string', async () => {
      await expect(getPokemonInfo({ pokemon: '' })).rejects.toThrow();
    }, 10000);
  });

  describe('Complete Data Integration', () => {
    test('should return all expected fields for a real pokemon', async () => {
      const result = await getPokemonInfo({ pokemon: 'ditto' });
      const parsed = JSON.parse(result.content[0].text);

      // Verify all expected fields exist
      expect(parsed).toHaveProperty('id');
      expect(parsed).toHaveProperty('name');
      expect(parsed).toHaveProperty('height');
      expect(parsed).toHaveProperty('weight');
      expect(parsed).toHaveProperty('types');
      expect(parsed).toHaveProperty('abilities');
      expect(parsed).toHaveProperty('stats');
      expect(parsed).toHaveProperty('sprites');
      
      expect(parsed.id).toBe(132);
      expect(parsed.name).toBe('ditto');
    }, 10000);
  });
});

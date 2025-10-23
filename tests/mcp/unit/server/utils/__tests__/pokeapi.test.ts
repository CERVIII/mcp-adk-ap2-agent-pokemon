/**
 * Tests para pokeapi.ts - Cliente de PokeAPI
 */
import { describe, it, expect, jest, beforeEach } from '@jest/globals';
import { fetchPokeAPI } from '../../../../../../src/mcp/server/utils/pokeapi.js';

// Mock global fetch
global.fetch = jest.fn() as jest.MockedFunction<typeof fetch>;

describe('PokeAPI Client', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('fetchPokeAPI', () => {
    it('should fetch data from PokeAPI successfully', async () => {
      const mockData = { id: 25, name: 'pikachu' };
      (global.fetch as jest.MockedFunction<typeof fetch>).mockResolvedValueOnce({
        ok: true,
        json: async () => mockData,
      } as Response);

      const result = await fetchPokeAPI('pokemon/25');
      
      expect(global.fetch).toHaveBeenCalledWith('https://pokeapi.co/api/v2/pokemon/25');
      expect(result).toEqual(mockData);
    });

    it('should construct correct URL for pokemon endpoint', async () => {
      (global.fetch as jest.MockedFunction<typeof fetch>).mockResolvedValueOnce({
        ok: true,
        json: async () => ({}),
      } as Response);

      await fetchPokeAPI('pokemon/pikachu');
      
      expect(global.fetch).toHaveBeenCalledWith('https://pokeapi.co/api/v2/pokemon/pikachu');
    });

    it('should construct correct URL for type endpoint', async () => {
      (global.fetch as jest.MockedFunction<typeof fetch>).mockResolvedValueOnce({
        ok: true,
        json: async () => ({}),
      } as Response);

      await fetchPokeAPI('type/electric');
      
      expect(global.fetch).toHaveBeenCalledWith('https://pokeapi.co/api/v2/type/electric');
    });

    it('should throw error when response is not ok', async () => {
      (global.fetch as jest.MockedFunction<typeof fetch>).mockResolvedValueOnce({
        ok: false,
        statusText: 'Not Found',
      } as Response);

      await expect(fetchPokeAPI('pokemon/999999')).rejects.toThrow('PokeAPI error: Not Found');
    });

    it('should handle network errors', async () => {
      (global.fetch as jest.MockedFunction<typeof fetch>).mockRejectedValueOnce(
        new Error('Network error')
      );

      await expect(fetchPokeAPI('pokemon/25')).rejects.toThrow('Network error');
    });

    it('should return JSON data', async () => {
      const mockData = {
        id: 6,
        name: 'charizard',
        types: [{ type: { name: 'fire' } }],
      };
      (global.fetch as jest.MockedFunction<typeof fetch>).mockResolvedValueOnce({
        ok: true,
        json: async () => mockData,
      } as Response);

      const result = await fetchPokeAPI('pokemon/6');
      
      expect(result).toHaveProperty('id');
      expect(result).toHaveProperty('name');
      expect(result.name).toBe('charizard');
    });
  });
});

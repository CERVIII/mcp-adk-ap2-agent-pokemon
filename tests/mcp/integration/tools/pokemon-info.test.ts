/**
 * Integration tests for get_pokemon_info tool
 * Tests the complete flow of fetching Pokemon data from PokeAPI
 */

import { describe, it, expect, beforeAll } from "@jest/globals";
import { getPokemonInfo } from "../../../../src/mcp/server/tools/pokemon-info.js";

describe("get_pokemon_info - Integration Tests", () => {
  describe("Valid Pokemon Queries", () => {
    it("should fetch Pikachu by name", async () => {
      const result = await getPokemonInfo({ pokemon: "pikachu" });
      
      expect(result.content).toBeDefined();
      expect(result.content.length).toBeGreaterThan(0);
      
      const textContent = result.content.find((c: any) => c.type === "text");
      expect(textContent).toBeDefined();
      
      const data = JSON.parse(textContent!.text);
      expect(data.name).toBe("pikachu");
      expect(data.id).toBe(25);
      expect(data.types).toContain("electric");
      expect(data.height).toBeGreaterThan(0);
      expect(data.weight).toBeGreaterThan(0);
    });

    it("should fetch Charizard by number", async () => {
      const result = await getPokemonInfo({ pokemon: "6" });
      
      const textContent = result.content.find((c: any) => c.type === "text");
      const data = JSON.parse(textContent!.text);
      
      expect(data.name).toBe("charizard");
      expect(data.id).toBe(6);
      expect(data.types).toContain("fire");
      expect(data.types).toContain("flying");
    });

    it("should fetch Bulbasaur with complete data", async () => {
      const result = await getPokemonInfo({ pokemon: "bulbasaur" });
      
      const textContent = result.content.find((c: any) => c.type === "text");
      const data = JSON.parse(textContent!.text);
      
      expect(data.name).toBe("bulbasaur");
      expect(data.id).toBe(1);
      expect(data.abilities).toBeDefined();
      expect(Array.isArray(data.abilities)).toBe(true);
      expect(data.abilities.length).toBeGreaterThan(0);
      expect(data.stats).toBeDefined();
      expect(data.sprites).toBeDefined();
    });

    it("should handle case-insensitive names", async () => {
      const result1 = await getPokemonInfo({ pokemon: "PIKACHU" });
      const result2 = await getPokemonInfo({ pokemon: "PiKaChU" });
      const result3 = await getPokemonInfo({ pokemon: "pikachu" });
      
      const data1 = JSON.parse(result1.content.find((c: any) => c.type === "text")!.text);
      const data2 = JSON.parse(result2.content.find((c: any) => c.type === "text")!.text);
      const data3 = JSON.parse(result3.content.find((c: any) => c.type === "text")!.text);
      
      expect(data1.id).toBe(25);
      expect(data2.id).toBe(25);
      expect(data3.id).toBe(25);
    });
  });

  describe("Edge Cases", () => {
    it("should handle Gen 1 boundary - Mew (#151)", async () => {
      const result = await getPokemonInfo({ pokemon: "151" });
      
      const textContent = result.content.find((c: any) => c.type === "text");
      const data = JSON.parse(textContent!.text);
      
      expect(data.name).toBe("mew");
      expect(data.id).toBe(151);
      expect(data.types).toContain("psychic");
    });

    it("should not work with padded numbers (PokeAPI limitation)", async () => {
      // PokeAPI doesn't accept padded numbers like "025"
      await expect(
        getPokemonInfo({ pokemon: "025" })
      ).rejects.toThrow();
    });
  });

  describe("Error Handling", () => {
    it("should throw error for invalid Pokemon name", async () => {
      await expect(
        getPokemonInfo({ pokemon: "invalidpokemon123" })
      ).rejects.toThrow();
    });

    it("should throw error for non-existent Pokemon number", async () => {
      await expect(
        getPokemonInfo({ pokemon: "9999" })
      ).rejects.toThrow();
    });

    it("should throw error for empty input", async () => {
      await expect(
        getPokemonInfo({ pokemon: "" })
      ).rejects.toThrow();
    });
  });

  describe("Data Structure Validation", () => {
    it("should return all required fields", async () => {
      const result = await getPokemonInfo({ pokemon: "pikachu" });
      
      const textContent = result.content.find((c: any) => c.type === "text");
      const data = JSON.parse(textContent!.text);
      
      // Required fields
      expect(data).toHaveProperty("id");
      expect(data).toHaveProperty("name");
      expect(data).toHaveProperty("types");
      expect(data).toHaveProperty("height");
      expect(data).toHaveProperty("weight");
      expect(data).toHaveProperty("abilities");
      expect(data).toHaveProperty("stats");
      expect(data).toHaveProperty("sprites");
    });

    it("should have valid stats structure", async () => {
      const result = await getPokemonInfo({ pokemon: "pikachu" });
      
      const textContent = result.content.find((c: any) => c.type === "text");
      const data = JSON.parse(textContent!.text);
      
      // stats is an array of {name, value} objects
      expect(Array.isArray(data.stats)).toBe(true);
      expect(data.stats.length).toBeGreaterThan(0);
      
      // Find specific stats
      const hp = data.stats.find((s: any) => s.name === "hp");
      const attack = data.stats.find((s: any) => s.name === "attack");
      
      expect(hp).toBeDefined();
      expect(attack).toBeDefined();
      expect(typeof hp.value).toBe("number");
      expect(typeof attack.value).toBe("number");
    });

    it("should have valid sprites URLs", async () => {
      const result = await getPokemonInfo({ pokemon: "pikachu" });
      
      const textContent = result.content.find((c: any) => c.type === "text");
      const data = JSON.parse(textContent!.text);
      
      expect(data.sprites).toHaveProperty("front_default");
      if (data.sprites.front_default) {
        expect(data.sprites.front_default).toMatch(/^https?:\/\//);
      }
    });
  });
});

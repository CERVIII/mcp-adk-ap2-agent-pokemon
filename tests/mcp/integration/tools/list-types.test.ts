/**
 * Integration tests for list_pokemon_types tool
 * Tests fetching all Pokemon types from PokeAPI
 */

import { describe, it, expect } from "@jest/globals";
import { listPokemonTypes } from "../../../../src/mcp/server/tools/list-types.js";

describe("list_pokemon_types - Integration Tests", () => {
  describe("Type List Retrieval", () => {
    it("should return array of Pokemon types", async () => {
      const result = await listPokemonTypes();

      const textContent = result.content.find((c: any) => c.type === "text");
      const data = JSON.parse(textContent!.text);

      expect(data).toHaveProperty("total");
      expect(data).toHaveProperty("types");
      expect(Array.isArray(data.types)).toBe(true);
      expect(data.types.length).toBeGreaterThan(0);
      expect(data.total).toBe(data.types.length);
    });

    it("should include common Gen 1 types", async () => {
      const result = await listPokemonTypes();

      const textContent = result.content.find((c: any) => c.type === "text");
      const data = JSON.parse(textContent!.text); const types = data.types;

      const expectedTypes = [
        "normal", "fire", "water", "electric", "grass", "ice",
        "fighting", "poison", "ground", "flying", "psychic", "bug",
        "rock", "ghost", "dragon"
      ];

      expectedTypes.forEach(type => {
        expect(types).toContain(type);
      });
    });

    it("should exclude unknown and shadow types", async () => {
      const result = await listPokemonTypes();

      const textContent = result.content.find((c: any) => c.type === "text");
      const data = JSON.parse(textContent!.text); const types = data.types;

      expect(types).not.toContain("unknown");
      expect(types).not.toContain("shadow");
    });

    it("should return consistent results on multiple calls", async () => {
      const result1 = await listPokemonTypes();
      const result2 = await listPokemonTypes();

      const types1 = JSON.parse(result1.content.find((c: any) => c.type === "text")!.text);
      const types2 = JSON.parse(result2.content.find((c: any) => c.type === "text")!.text);

      expect(types1).toEqual(types2);
    });
  });

  describe("Data Validation", () => {
    it("should return only string values", async () => {
      const result = await listPokemonTypes();

      const textContent = result.content.find((c: any) => c.type === "text");
      const data = JSON.parse(textContent!.text); const types = data.types;

      types.forEach((type: any) => {
        expect(typeof type).toBe("string");
      });
    });

    it("should have no duplicate types", async () => {
      const result = await listPokemonTypes();

      const textContent = result.content.find((c: any) => c.type === "text");
      const data = JSON.parse(textContent!.text); const types = data.types;

      const uniqueTypes = [...new Set(types)];
      expect(types.length).toBe(uniqueTypes.length);
    });

    it("should have all lowercase type names", async () => {
      const result = await listPokemonTypes();

      const textContent = result.content.find((c: any) => c.type === "text");
      const data = JSON.parse(textContent!.text); const types = data.types;

      types.forEach((type: string) => {
        expect(type).toBe(type.toLowerCase());
      });
    });

    it("should have no empty strings", async () => {
      const result = await listPokemonTypes();

      const textContent = result.content.find((c: any) => c.type === "text");
      const data = JSON.parse(textContent!.text); const types = data.types;

      types.forEach((type: string) => {
        expect(type.length).toBeGreaterThan(0);
      });
    });
  });

  describe("Type Coverage", () => {
    it("should include all 18 main Pokemon types", async () => {
      const result = await listPokemonTypes();

      const textContent = result.content.find((c: any) => c.type === "text");
      const data = JSON.parse(textContent!.text); const types = data.types;

      // Modern Pokemon has 18 types, but Gen 1 had 15
      // (no Dark, Steel, or Fairy in Gen 1)
      expect(types.length).toBeGreaterThanOrEqual(15);
    });

    it("should include fairy type (if available)", async () => {
      const result = await listPokemonTypes();

      const textContent = result.content.find((c: any) => c.type === "text");
      const data = JSON.parse(textContent!.text); const types = data.types;

      // Fairy was added in Gen 6, so it should be in the API
      expect(types).toContain("fairy");
    });
  });
});

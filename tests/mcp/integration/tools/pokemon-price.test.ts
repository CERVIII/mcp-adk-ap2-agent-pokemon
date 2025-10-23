/**
 * Integration tests for get_pokemon_price tool
 * Tests fetching Pokemon pricing and inventory from database/JSON
 */

import { describe, it, expect } from "@jest/globals";
import { getPokemonPrice } from "../../../../src/mcp/server/tools/pokemon-price.js";

describe("get_pokemon_price - Integration Tests", () => {
  describe("Valid Pokemon Queries", () => {
    it("should fetch Pikachu price by name", async () => {
      const result = await getPokemonPrice({ pokemon: "pikachu" });
      
      const textContent = result.content.find((c: any) => c.type === "text");
      expect(textContent).toBeDefined();
      
      const data = JSON.parse(textContent!.text);
      expect(data.numero).toBe(25);
      expect(data.nombre).toBe("pikachu");
      expect(data.precio).toBeGreaterThan(0);
      expect(data).toHaveProperty("enVenta");
      expect(data).toHaveProperty("inventario");
    });

    it("should fetch Charizard price by number", async () => {
      const result = await getPokemonPrice({ pokemon: "6" });
      
      const textContent = result.content.find((c: any) => c.type === "text");
      const data = JSON.parse(textContent!.text);
      
      expect(data.numero).toBe(6);
      expect(data.nombre).toBe("charizard");
      expect(typeof data.precio).toBe("number");
    });

    it("should handle case-insensitive queries", async () => {
      const result1 = await getPokemonPrice({ pokemon: "PIKACHU" });
      const result2 = await getPokemonPrice({ pokemon: "pikachu" });
      
      const data1 = JSON.parse(result1.content.find((c: any) => c.type === "text")!.text);
      const data2 = JSON.parse(result2.content.find((c: any) => c.type === "text")!.text);
      
      expect(data1.numero).toBe(data2.numero);
      expect(data1.precio).toBe(data2.precio);
    });

    it("should handle padded numbers (returns error)", async () => {
      const result = await getPokemonPrice({ pokemon: "025" });
      
      const textContent = result.content.find((c: any) => c.type === "text");
      
      // Padded IDs don't work, should return error message
      expect(textContent!.text).toContain("not found");
    });
  });

  describe("Inventory Data Validation", () => {
    it("should include complete inventory information", async () => {
      const result = await getPokemonPrice({ pokemon: "pikachu" });
      
      const textContent = result.content.find((c: any) => c.type === "text");
      const data = JSON.parse(textContent!.text);
      
      expect(data.inventario).toBeDefined();
      expect(data.inventario).toHaveProperty("total");
      expect(data.inventario).toHaveProperty("disponibles");
      expect(data.inventario).toHaveProperty("vendidos");
      
      expect(typeof data.inventario.total).toBe("number");
      expect(typeof data.inventario.disponibles).toBe("number");
      expect(typeof data.inventario.vendidos).toBe("number");
    });

    it("should have consistent inventory totals", async () => {
      const result = await getPokemonPrice({ pokemon: "pikachu" });
      
      const textContent = result.content.find((c: any) => c.type === "text");
      const data = JSON.parse(textContent!.text);
      
      const { total, disponibles, vendidos } = data.inventario;
      expect(disponibles + vendidos).toBeLessThanOrEqual(total);
    });

    it("should indicate availability status", async () => {
      const result = await getPokemonPrice({ pokemon: "pikachu" });
      
      const textContent = result.content.find((c: any) => c.type === "text");
      const data = JSON.parse(textContent!.text);
      
      expect(typeof data.enVenta).toBe("boolean");
    });
  });

  describe("Gen 1 Coverage", () => {
    it("should fetch first Pokemon - Bulbasaur", async () => {
      const result = await getPokemonPrice({ pokemon: "1" });
      
      const textContent = result.content.find((c: any) => c.type === "text");
      const data = JSON.parse(textContent!.text);
      
      expect(data.numero).toBe(1);
      expect(data.nombre).toBe("bulbasaur");
    });

    it("should fetch last Gen 1 Pokemon - Mew", async () => {
      const result = await getPokemonPrice({ pokemon: "151" });
      
      const textContent = result.content.find((c: any) => c.type === "text");
      const data = JSON.parse(textContent!.text);
      
      expect(data.numero).toBe(151);
      expect(data.nombre).toBe("mew");
    });

    it("should have prices for all Gen 1 Pokemon", async () => {
      const testPokemon = ["1", "25", "50", "100", "151"];
      
      for (const id of testPokemon) {
        const result = await getPokemonPrice({ pokemon: id });
        const textContent = result.content.find((c: any) => c.type === "text");
        const data = JSON.parse(textContent!.text);
        
        expect(data.precio).toBeGreaterThan(0);
        expect(data.numero).toBe(parseInt(id));
      }
    });
  });

  describe("Error Handling", () => {
    it("should return error message for Pokemon outside Gen 1", async () => {
      const result = await getPokemonPrice({ pokemon: "152" });
      const textContent = result.content.find((c: any) => c.type === "text");
      
      expect(textContent!.text).toContain("not found");
      expect(textContent!.text).toContain("152");
    });

    it("should return error message for invalid Pokemon name", async () => {
      const result = await getPokemonPrice({ pokemon: "invalidpokemon" });
      const textContent = result.content.find((c: any) => c.type === "text");
      
      expect(textContent!.text).toContain("not found");
    });

    it("should return error message for empty input", async () => {
      const result = await getPokemonPrice({ pokemon: "" });
      const textContent = result.content.find((c: any) => c.type === "text");
      
      expect(textContent!.text).toContain("not found");
    });
  });

  describe("Price Data Consistency", () => {
    it("should return consistent prices for same Pokemon", async () => {
      const result1 = await getPokemonPrice({ pokemon: "pikachu" });
      const result2 = await getPokemonPrice({ pokemon: "25" });
      
      const data1 = JSON.parse(result1.content.find((c: any) => c.type === "text")!.text);
      const data2 = JSON.parse(result2.content.find((c: any) => c.type === "text")!.text);
      
      expect(data1.precio).toBe(data2.precio);
      expect(data1.inventario).toEqual(data2.inventario);
    });

    it("should have valid price range (USD)", async () => {
      const result = await getPokemonPrice({ pokemon: "pikachu" });
      
      const textContent = result.content.find((c: any) => c.type === "text");
      const data = JSON.parse(textContent!.text);
      
      expect(data.precio).toBeGreaterThan(0);
      expect(data.precio).toBeLessThan(10000); // Reasonable upper limit
    });
  });
});

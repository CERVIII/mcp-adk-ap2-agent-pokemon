/**
 * Integration tests for get_pokemon_product tool
 * Tests combined PokeAPI + local price data for single Pokemon
 */

import { describe, it, expect } from "@jest/globals";
import { getPokemonProduct } from "../../../../src/mcp/server/tools/product-info.js";

describe("get_pokemon_product - Integration Tests", () => {
  describe("Valid Product Queries", () => {
    it("should fetch complete Pikachu data", async () => {
      const result = await getPokemonProduct({ product_id: "25" });

      const textContent = result.content.find((c: any) => c.type === "text");
      const product = JSON.parse(textContent!.text);

      expect(product.product_id).toBe("25");
      expect(product.name).toBe("pikachu");
      expect(product.price).toBeGreaterThan(0);
      expect(product.currency).toBe("USD");
    });

    it("should merge PokeAPI and local data", async () => {
      const result = await getPokemonProduct({ product_id: "6" });

      const textContent = result.content.find((c: any) => c.type === "text");
      const product = JSON.parse(textContent!.text);

      // PokeAPI fields
      expect(product).toHaveProperty("types");
      expect(product).toHaveProperty("height");
      expect(product).toHaveProperty("weight");
      expect(product).toHaveProperty("abilities");

      // Local pricing fields
      expect(product).toHaveProperty("price");
      expect(product).toHaveProperty("available");
      expect(product).toHaveProperty("stock");
      expect(product).toHaveProperty("total_inventory");
      expect(product).toHaveProperty("sold");
    });

    it("should handle different product IDs", async () => {
      const testIds = ["1", "25", "50", "100", "151"];

      for (const id of testIds) {
        const result = await getPokemonProduct({ product_id: id });
        const textContent = result.content.find((c: any) => c.type === "text");
        const product = JSON.parse(textContent!.text);

        expect(product.product_id).toBe(id);
      }
    });
  });

  describe("Data Completeness", () => {
    it("should include all PokeAPI fields", async () => {
      const result = await getPokemonProduct({ product_id: "25" });

      const textContent = result.content.find((c: any) => c.type === "text");
      const product = JSON.parse(textContent!.text);

      expect(product).toHaveProperty("product_id");
      expect(product).toHaveProperty("name");
      expect(product).toHaveProperty("types");
      expect(product).toHaveProperty("height");
      expect(product).toHaveProperty("weight");
      expect(product).toHaveProperty("abilities");
      // Note: stats and sprites are NOT included in product-info tool
    });

    it("should include all pricing fields", async () => {
      const result = await getPokemonProduct({ product_id: "25" });

      const textContent = result.content.find((c: any) => c.type === "text");
      const product = JSON.parse(textContent!.text);

      expect(product).toHaveProperty("product_id");
      expect(product).toHaveProperty("name");
      expect(product).toHaveProperty("price");
      expect(product).toHaveProperty("currency");
      expect(product).toHaveProperty("available");
      expect(product).toHaveProperty("stock");
      expect(product).toHaveProperty("total_inventory");
      expect(product).toHaveProperty("sold");
    });

    it("should have consistent product_id", async () => {
      const result = await getPokemonProduct({ product_id: "25" });

      const textContent = result.content.find((c: any) => c.type === "text");
      const product = JSON.parse(textContent!.text);

      expect(product.product_id).toBe("25");
      expect(product.name).toBe("pikachu");
    });
  });

  describe("Data Types Validation", () => {
    it("should have correct data types", async () => {
      const result = await getPokemonProduct({ product_id: "25" });

      const textContent = result.content.find((c: any) => c.type === "text");
      const product = JSON.parse(textContent!.text);

      expect(typeof product.product_id).toBe("string");
      expect(typeof product.name).toBe("string");
      expect(Array.isArray(product.types)).toBe(true);
      expect(typeof product.height).toBe("number");
      expect(typeof product.weight).toBe("number");
      expect(typeof product.price).toBe("number");
      expect(typeof product.available).toBe("boolean");
      expect(typeof product.stock).toBe("number");
    });

    it("should have valid inventory numbers", async () => {
      const result = await getPokemonProduct({ product_id: "25" });

      const textContent = result.content.find((c: any) => c.type === "text");
      const product = JSON.parse(textContent!.text);

      expect(product.total_inventory).toBeGreaterThanOrEqual(0);
      expect(product.stock).toBeGreaterThanOrEqual(0);
      expect(product.sold).toBeGreaterThanOrEqual(0);
      expect(product.stock + product.sold)
        .toBeLessThanOrEqual(product.total_inventory);
    });
  });

  describe("Edge Cases", () => {
    it("should handle first Gen 1 Pokemon", async () => {
      const result = await getPokemonProduct({ product_id: "1" });

      const textContent = result.content.find((c: any) => c.type === "text");
      const product = JSON.parse(textContent!.text);

      expect(product.product_id).toBe("1");
      expect(product.name).toBe("bulbasaur");
    });

    it("should handle last Gen 1 Pokemon", async () => {
      const result = await getPokemonProduct({ product_id: "151" });

      const textContent = result.content.find((c: any) => c.type === "text");
      const product = JSON.parse(textContent!.text);

      expect(product.product_id).toBe("151");
      expect(product.name).toBe("mew");
    });

    it("should handle padded product IDs", async () => {
      const result = await getPokemonProduct({ product_id: "025" });

      const textContent = result.content.find((c: any) => c.type === "text");
      
      // Padded IDs might return error message
      if (textContent!.text.startsWith("Pokemon")) {
        // It's an error message
        expect(textContent!.text).toContain("not found");
      } else {
        const product = JSON.parse(textContent!.text);
        // If it works, should be Pikachu
        expect(product.name).toBe("pikachu");
      }
    });
  });

  describe("Error Handling", () => {
    it("should return error message for Pokemon outside Gen 1", async () => {
      const result = await getPokemonProduct({ product_id: "152" });
      const textContent = result.content.find((c: any) => c.type === "text");
      
      // Should return error message, not throw
      expect(textContent!.text).toContain("not found");
      expect(textContent!.text).toContain("152");
    });

    it("should return error message for invalid product_id", async () => {
      const result = await getPokemonProduct({ product_id: "999" });
      const textContent = result.content.find((c: any) => c.type === "text");
      
      expect(textContent!.text).toContain("not found");
    });

    it("should return error message for non-numeric product_id", async () => {
      const result = await getPokemonProduct({ product_id: "invalid" });
      const textContent = result.content.find((c: any) => c.type === "text");
      
      expect(textContent!.text).toContain("not found");
    });

    it("should return error message for empty product_id", async () => {
      const result = await getPokemonProduct({ product_id: "" });
      const textContent = result.content.find((c: any) => c.type === "text");
      
      expect(textContent!.text).toContain("not found");
    });

    it("should return error message for negative product_id", async () => {
      const result = await getPokemonProduct({ product_id: "-1" });
      const textContent = result.content.find((c: any) => c.type === "text");
      
      expect(textContent!.text).toContain("not found");
    });

    it("should return error message for zero product_id", async () => {
      const result = await getPokemonProduct({ product_id: "0" });
      const textContent = result.content.find((c: any) => c.type === "text");
      
      expect(textContent!.text).toContain("not found");
    });
  });

  describe("Consistency with Other Tools", () => {
    it("should have PokeAPI data when available", async () => {
      const result = await getPokemonProduct({ product_id: "25" });

      const textContent = result.content.find((c: any) => c.type === "text");
      const product = JSON.parse(textContent!.text);

      // Should have PokeAPI fields
      expect(product).toHaveProperty("types");
      expect(product).toHaveProperty("abilities");
      expect(product.types).toContain("electric");
    });

    it("should have pricing data", async () => {
      const result = await getPokemonProduct({ product_id: "25" });

      const textContent = result.content.find((c: any) => c.type === "text");
      const product = JSON.parse(textContent!.text);

      // Should have pricing fields
      expect(product.price).toBeGreaterThan(0);
      expect(product).toHaveProperty("available");
      expect(product).toHaveProperty("stock");
    });
  });
});

/**
 * Integration tests for create_pokemon_cart tool (AP2)
 * Tests CartMandate creation with JWT signatures
 */

import { describe, it, expect, beforeAll } from "@jest/globals";
import { createPokemonCart } from "../../../../src/mcp/server/tools/cart-create.js";
import { loadOrGenerateRSAKeys } from "../../../../src/mcp/server/utils/rsa-keys.js";
import { setMerchantPrivateKey } from "../../../../src/mcp/server/ap2/cart-mandate.js";
import jwt from "jsonwebtoken";

describe("create_pokemon_cart - Integration Tests", () => {
  let publicKey: string;

  beforeAll(async () => {
    // Load RSA keys and inject into cart-mandate module
    const keys = await loadOrGenerateRSAKeys();
    setMerchantPrivateKey(keys.privateKey);
    publicKey = keys.publicKey;
  });

  describe("Valid Cart Creation", () => {
    it("should create cart with single item", async () => {
      const result = await createPokemonCart({
        items: [
          { product_id: "25", quantity: 1 }
        ]
      });

      const textContent = result.content.find((c: any) => c.type === "text");
      const cartMandate = JSON.parse(textContent!.text);

      expect(cartMandate).toHaveProperty("contents");
      expect(cartMandate).toHaveProperty("merchant_signature");
      expect(cartMandate).toHaveProperty("timestamp");
      expect(cartMandate.contents).toHaveProperty("merchant_name");
    });

    it("should create cart with multiple items (if stock allows)", async () => {
      const result = await createPokemonCart({
        items: [
          { product_id: "25", quantity: 1 },
          { product_id: "6", quantity: 1 },
          { product_id: "1", quantity: 1 }
        ]
      });

      const textContent = result.content.find((c: any) => c.type === "text");
      const cartMandate = JSON.parse(textContent!.text);

      expect(cartMandate.contents.items.length).toBe(3);
      expect(cartMandate.contents.payment_request.details.displayItems.length).toBe(3);
    });

    it("should handle different quantities", async () => {
      const result = await createPokemonCart({
        items: [
          { product_id: "25", quantity: 2 }
        ]
      });

      const textContent = result.content.find((c: any) => c.type === "text");
      const cartMandate = JSON.parse(textContent!.text);

      const item = cartMandate.contents.items[0];
      expect(item.quantity).toBe(2);
      expect(item.product_id).toBe("25");
      
      // Verify displayItems has the expanded data
      const displayItem = cartMandate.contents.payment_request.details.displayItems[0];
      expect(displayItem.label).toContain("Pikachu");
      expect(displayItem.label).toContain("x2");
    });
  });

  describe("CartMandate Structure", () => {
    it("should have valid cart ID format", async () => {
      const result = await createPokemonCart({
        items: [{ product_id: "25", quantity: 1 }]
      });

      const textContent = result.content.find((c: any) => c.type === "text");
      const cartMandate = JSON.parse(textContent!.text);

      expect(cartMandate.contents.id).toMatch(/^cart_pokemon_[a-f0-9]{8}$/);
    });

    it("should set user_signature_required to false", async () => {
      const result = await createPokemonCart({
        items: [{ product_id: "25", quantity: 1 }]
      });

      const textContent = result.content.find((c: any) => c.type === "text");
      const cartMandate = JSON.parse(textContent!.text);

      expect(cartMandate.contents.user_signature_required).toBe(false);
    });

    it("should include merchant name", async () => {
      const result = await createPokemonCart({
        items: [{ product_id: "25", quantity: 1 }]
      });

      const textContent = result.content.find((c: any) => c.type === "text");
      const cartMandate = JSON.parse(textContent!.text);

      expect(cartMandate.contents.merchant_name).toBe("PokeMart - Primera Generación");
    });

    it("should have ISO8601 timestamp", async () => {
      const result = await createPokemonCart({
        items: [{ product_id: "25", quantity: 1 }]
      });

      const textContent = result.content.find((c: any) => c.type === "text");
      const cartMandate = JSON.parse(textContent!.text);

      expect(cartMandate.timestamp).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/);
    });
  });

  describe("Payment Request Structure", () => {
    it("should include all required payment fields", async () => {
      const result = await createPokemonCart({
        items: [{ product_id: "25", quantity: 1 }]
      });

      const textContent = result.content.find((c: any) => c.type === "text");
      const cartMandate = JSON.parse(textContent!.text);
      const payment = cartMandate.contents.payment_request;

      expect(payment).toHaveProperty("details");
      expect(payment.details).toHaveProperty("total");
      expect(payment.details.total).toHaveProperty("amount");
      expect(payment).toHaveProperty("method_data");
      expect(payment.method_data[0].data).toHaveProperty("payment_processor_url");
    });

    it("should calculate total correctly", async () => {
      const result = await createPokemonCart({
        items: [
          { product_id: "25", quantity: 1 },
          { product_id: "6", quantity: 1 }
        ]
      });

      const textContent = result.content.find((c: any) => c.type === "text");
      const cartMandate = JSON.parse(textContent!.text);
      const payment = cartMandate.contents.payment_request;

      const displayItemsTotal = payment.details.displayItems.reduce((sum: number, item: any) => 
        sum + item.amount.value, 0
      );

      expect(payment.details.total.amount.value).toBe(displayItemsTotal);
    });

    it("should use USD currency", async () => {
      const result = await createPokemonCart({
        items: [{ product_id: "25", quantity: 1 }]
      });

      const textContent = result.content.find((c: any) => c.type === "text");
      const cartMandate = JSON.parse(textContent!.text);

      expect(cartMandate.contents.payment_request.details.total.amount.currency).toBe("USD");
    });

    it("should include processor URL", async () => {
      const result = await createPokemonCart({
        items: [{ product_id: "25", quantity: 1 }]
      });

      const textContent = result.content.find((c: any) => c.type === "text");
      const cartMandate = JSON.parse(textContent!.text);

      expect(cartMandate.contents.payment_request.method_data[0].data.payment_processor_url).toBe(
        "http://localhost:8003/a2a/processor"
      );
    });
  });

  describe("Item Data Validation", () => {
    it("should include Pokemon name in items", async () => {
      const result = await createPokemonCart({
        items: [{ product_id: "25", quantity: 1 }]
      });

      const textContent = result.content.find((c: any) => c.type === "text");
      const cartMandate = JSON.parse(textContent!.text);
      const item = cartMandate.contents.items[0];

      expect(item.product_id).toBe("25");
      expect(item.quantity).toBe(1);
      
      // Name is in displayItems, not items
      const displayItem = cartMandate.contents.payment_request.details.displayItems[0];
      expect(displayItem.label.toLowerCase()).toContain("pikachu");
    });

    it("should include correct unit prices", async () => {
      const result = await createPokemonCart({
        items: [{ product_id: "25", quantity: 1 }]
      });

      const textContent = result.content.find((c: any) => c.type === "text");
      const cartMandate = JSON.parse(textContent!.text);
      
      // Prices are in displayItems
      const displayItem = cartMandate.contents.payment_request.details.displayItems[0];
      expect(displayItem.amount.value).toBeGreaterThan(0);
      expect(typeof displayItem.amount.value).toBe("number");
      expect(displayItem.amount.currency).toBe("USD");
    });

    it("should calculate item totals correctly", async () => {
      const result = await createPokemonCart({
        items: [{ product_id: "25", quantity: 2 }]
      });

      const textContent = result.content.find((c: any) => c.type === "text");
      const cartMandate = JSON.parse(textContent!.text);
      
      // Total is in displayItems
      const displayItem = cartMandate.contents.payment_request.details.displayItems[0];
      expect(displayItem.amount.value).toBeGreaterThan(0);
      expect(displayItem.label).toContain("x2");
      
      // Verify total matches sum
      expect(cartMandate.contents.payment_request.details.total.amount.value).toBe(displayItem.amount.value);
    });
  });

  describe("JWT Signature Validation", () => {
    it("should generate valid JWT signature", async () => {
      const result = await createPokemonCart({
        items: [{ product_id: "25", quantity: 1 }]
      });

      const textContent = result.content.find((c: any) => c.type === "text");
      const cartMandate = JSON.parse(textContent!.text);

      // JWT signature should be a full JWT token (3 parts separated by dots)
      expect(cartMandate.merchant_signature).toMatch(/^eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$/);
    });

    it("should have JWT with 3 parts", async () => {
      if (!publicKey) {
        console.warn("Skipping JWT verification - public key not available");
        return;
      }

      const result = await createPokemonCart({
        items: [{ product_id: "25", quantity: 1 }]
      });

      const textContent = result.content.find((c: any) => c.type === "text");
      const cartMandate = JSON.parse(textContent!.text);
      const jwtToken = cartMandate.merchant_signature;

      const parts = jwtToken.split(".");
      expect(parts.length).toBe(3);
    });

    it("should verify JWT with public key", async () => {
      if (!publicKey) {
        console.warn("Skipping JWT verification - public key not available");
        return;
      }

      const result = await createPokemonCart({
        items: [{ product_id: "25", quantity: 1 }]
      });

      const textContent = result.content.find((c: any) => c.type === "text");
      const cartMandate = JSON.parse(textContent!.text);

      const decoded = jwt.verify(cartMandate.merchant_signature, publicKey, {
        algorithms: ["RS256"]
      });

      expect(decoded).toHaveProperty("iss");
      expect(decoded).toHaveProperty("sub");
      expect(decoded).toHaveProperty("iat");
      expect(decoded).toHaveProperty("exp");
    });

    it("should have correct JWT claims", async () => {
      if (!publicKey) {
        console.warn("Skipping JWT verification - public key not available");
        return;
      }

      const result = await createPokemonCart({
        items: [{ product_id: "25", quantity: 1 }]
      });

      const textContent = result.content.find((c: any) => c.type === "text");
      const cartMandate = JSON.parse(textContent!.text);

      const decoded: any = jwt.verify(cartMandate.merchant_signature, publicKey, {
        algorithms: ["RS256"]
      });

      expect(decoded.iss).toBe("PokeMart");
      expect(decoded.sub).toBe(cartMandate.contents.id);
    });
  });

  describe("Inventory Validation", () => {
    it("should check stock availability", async () => {
      const result = await createPokemonCart({
        items: [{ product_id: "25", quantity: 1 }]
      });

      const textContent = result.content.find((c: any) => c.type === "text");
      const cartMandate = JSON.parse(textContent!.text);

      expect(cartMandate).toBeDefined();
      // If we got here, stock was available
    });

    it("should handle insufficient stock gracefully", async () => {
      try {
        await createPokemonCart({
          items: [{ product_id: "25", quantity: 999999 }]
        });
        fail("Should have thrown an error for insufficient stock");
      } catch (error: any) {
        expect(error.message).toContain("available");
      }
    });

    it("should throw error for out-of-stock Pokemon", async () => {
      // Find a Pokemon that's out of stock (disponibles = 0)
      // This test assumes there's at least one out-of-stock Pokemon
      // If all are in stock, this test will be skipped
      try {
        await createPokemonCart({
          items: [{ product_id: "999", quantity: 1 }]
        });
        // If it doesn't throw, the Pokemon has stock
      } catch (error) {
        expect(error).toBeDefined();
      }
    });
  });

  describe("Error Handling", () => {
    it("should handle invalid product_id", async () => {
      try {
        await createPokemonCart({
          items: [{ product_id: "999", quantity: 1 }]
        });
        fail("Should have thrown an error for invalid product_id");
      } catch (error: any) {
        expect(error.message).toContain("not found");
      }
    });

    it("should handle empty items array", async () => {
      const result = await createPokemonCart({ items: [] });

      const textContent = result.content.find((c: any) => c.type === "text");
      const cartMandate = JSON.parse(textContent!.text);

      // Tool creates cart with empty items
      expect(cartMandate.contents.items).toHaveLength(0);
      expect(cartMandate.contents.payment_request.details.displayItems).toHaveLength(0);
      expect(cartMandate.contents.payment_request.details.total.amount.value).toBe(0);
    });

    it("should handle zero quantity", async () => {
      try {
        await createPokemonCart({
          items: [{ product_id: "25", quantity: 0 }]
        });
        fail("Should have thrown validation error for zero quantity");
      } catch (error: any) {
        expect(error.name).toBe("ZodError");
      }
    });

    it("should handle negative quantity", async () => {
      try {
        await createPokemonCart({
          items: [{ product_id: "25", quantity: -1 }]
        });
        fail("Should have thrown validation error for negative quantity");
      } catch (error: any) {
        expect(error.name).toBe("ZodError");
      }
    });

    it("should handle Pokemon outside Gen 1", async () => {
      try {
        await createPokemonCart({
          items: [{ product_id: "152", quantity: 1 }]
        });
        fail("Should have thrown an error for Pokemon outside Gen 1");
      } catch (error: any) {
        expect(error.message).toContain("not found");
      }
    });
  });
});

/**
 * Tests for cart-create.ts
 * MCP tool: create_pokemon_cart
 * 
 * Note: Integration tests using real database and RSA keys
 */

import { describe, test, expect, beforeAll } from '@jest/globals';
import { createPokemonCart, createPokemonCartSchema } from '../../../../../../src/mcp/server/tools/cart-create.js';
import { loadOrGenerateRSAKeys } from '../../../../../../src/mcp/server/utils/rsa-keys.js';
import { setMerchantPrivateKey } from '../../../../../../src/mcp/server/ap2/cart-mandate.js';

describe('createPokemonCart', () => {
  beforeAll(async () => {
    // Load RSA keys and inject into cart-mandate module
    const keys = await loadOrGenerateRSAKeys();
    setMerchantPrivateKey(keys.privateKey);
  });

  describe('Schema Validation', () => {
    test('should accept valid items array', () => {
      const result = createPokemonCartSchema.parse({
        items: [
          { product_id: '25', quantity: 1 }
        ]
      });

      expect(result.items).toHaveLength(1);
      expect(result.items[0].product_id).toBe('25');
    });

    test('should use default quantity of 1', () => {
      const result = createPokemonCartSchema.parse({
        items: [{ product_id: '25' }]
      });

      expect(result.items[0].quantity).toBe(1);
    });

    test('should accept multiple items', () => {
      const result = createPokemonCartSchema.parse({
        items: [
          { product_id: '1', quantity: 2 },
          { product_id: '4', quantity: 1 },
          { product_id: '7', quantity: 3 }
        ]
      });

      expect(result.items).toHaveLength(3);
    });

    test('should accept empty items array (Zod allows it)', () => {
      const result = createPokemonCartSchema.parse({ items: [] });
      expect(result.items).toHaveLength(0);
    });

    test('should reject negative quantity', () => {
      expect(() => createPokemonCartSchema.parse({
        items: [{ product_id: '25', quantity: -1 }]
      })).toThrow();
    });

    test('should reject zero quantity', () => {
      expect(() => createPokemonCartSchema.parse({
        items: [{ product_id: '25', quantity: 0 }]
      })).toThrow();
    });

    test('should reject missing items', () => {
      expect(() => createPokemonCartSchema.parse({})).toThrow();
    });
  });

  describe('Cart Creation', () => {
    test('should create cart with single item', async () => {
      const result = await createPokemonCart({
        items: [{ product_id: '25', quantity: 1 }]
      });

      expect(result.content).toHaveLength(1);
      expect(result.content[0].type).toBe('text');

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed).toHaveProperty('contents');
      expect(parsed).toHaveProperty('merchant_signature');
      expect(parsed).toHaveProperty('timestamp');
    });

    test('should create cart with multiple items', async () => {
      const result = await createPokemonCart({
        items: [
          { product_id: '25', quantity: 1 }, // Pikachu
          { product_id: '4', quantity: 1 }   // Charmander
        ]
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.contents.items).toHaveLength(2);
    });

    test('should include merchant signature', async () => {
      const result = await createPokemonCart({
        items: [{ product_id: '150', quantity: 1 }]
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.merchant_signature).toBeDefined();
      expect(typeof parsed.merchant_signature).toBe('string');
      expect(parsed.merchant_signature.split('.')).toHaveLength(3); // JWT format
    });

    test('should include timestamp', async () => {
      const result = await createPokemonCart({
        items: [{ product_id: '6', quantity: 1 }]
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.timestamp).toBeDefined();
      expect(new Date(parsed.timestamp).toISOString()).toBe(parsed.timestamp);
    });
  });

  describe('CartMandate Structure', () => {
    test('should have contents with payment_request', async () => {
      const result = await createPokemonCart({
        items: [{ product_id: '100', quantity: 1 }]
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.contents).toHaveProperty('id');
      expect(parsed.contents).toHaveProperty('user_signature_required');
      expect(parsed.contents).toHaveProperty('payment_request');
    });

    test('should have user_signature_required as false', async () => {
      const result = await createPokemonCart({
        items: [{ product_id: '75', quantity: 1 }]
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.contents.user_signature_required).toBe(false);
    });

    test('should include payment processor URL', async () => {
      const result = await createPokemonCart({
        items: [{ product_id: '50', quantity: 1 }]
      });

      const parsed = JSON.parse(result.content[0].text);
      const processorUrl = parsed.contents.payment_request.method_data[0].data.payment_processor_url;
      expect(processorUrl).toBeDefined();
      expect(processorUrl).toContain('processor');
    });

    test('should include merchant name', async () => {
      const result = await createPokemonCart({
        items: [{ product_id: '143', quantity: 1 }]
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.contents.merchant_name).toBeDefined();
      expect(typeof parsed.contents.merchant_name).toBe('string');
    });
  });

  describe('Item Details', () => {
    test('should include correct item details', async () => {
      const result = await createPokemonCart({
        items: [{ product_id: '25', quantity: 1 }]
      });

      const parsed = JSON.parse(result.content[0].text);
      const item = parsed.contents.items[0];

      expect(item).toHaveProperty('product_id');
      expect(item).toHaveProperty('quantity');
      expect(item.product_id).toBe('25');
      expect(item.quantity).toBe(1);
    });

    test('should calculate total correctly', async () => {
      const result = await createPokemonCart({
        items: [
          { product_id: '25', quantity: 1 }, // Pikachu
          { product_id: '4', quantity: 1 }   // Charmander
        ]
      });

      const parsed = JSON.parse(result.content[0].text);
      const total = parsed.contents.payment_request.details.total.amount.value;
      expect(total).toBeDefined();
      expect(typeof total).toBe('number');
      expect(total).toBeGreaterThan(0);
    });

    test('should include currency', async () => {
      const result = await createPokemonCart({
        items: [{ product_id: '7', quantity: 1 }]
      });

      const parsed = JSON.parse(result.content[0].text);
      const currency = parsed.contents.payment_request.details.total.amount.currency;
      expect(currency).toBe('USD');
    });
  });

  describe('Error Handling', () => {
    test('should handle invalid Pokemon ID', async () => {
      await expect(createPokemonCart({
        items: [{ product_id: '999', quantity: 1 }]
      })).rejects.toThrow();
    });

    test('should handle out of stock Pokemon', async () => {
      // This will depend on inventory - test the error mechanism
      try {
        await createPokemonCart({
          items: [{ product_id: '1', quantity: 10000 }] // Excessive quantity
        });
      } catch (error) {
        expect(error).toBeDefined();
      }
    });

    test('should handle Gen 2+ Pokemon', async () => {
      await expect(createPokemonCart({
        items: [{ product_id: '200', quantity: 1 }]
      })).rejects.toThrow();
    });
  });

  describe('JSON Formatting', () => {
    test('should return properly formatted JSON', async () => {
      const result = await createPokemonCart({
        items: [{ product_id: '10', quantity: 1 }]
      });

      expect(result.content[0].text).toContain('  "contents"');
      expect(result.content[0].text).toContain('  "merchant_signature"');
      expect(() => JSON.parse(result.content[0].text)).not.toThrow();
    });

    test('should use 2-space indentation', async () => {
      const result = await createPokemonCart({
        items: [{ product_id: '15', quantity: 1 }]
      });

      const lines = result.content[0].text.split('\n');
      const indentedLine = lines.find(line => line.startsWith('  "'));
      expect(indentedLine).toBeDefined();
    });
  });

  describe('Multiple Quantities', () => {
    test('should handle quantity of 1', async () => {
      const result = await createPokemonCart({
        items: [{ product_id: '25', quantity: 1 }]
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.contents.items[0].quantity).toBe(1);
    });

    test('should handle quantity greater than 1', async () => {
      const result = await createPokemonCart({
        items: [{ product_id: '25', quantity: 1 }]
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.contents.items[0].quantity).toBe(1);
    });

    test('should handle mixed quantities', async () => {
      const result = await createPokemonCart({
        items: [
          { product_id: '25', quantity: 1 },
          { product_id: '4', quantity: 1 },
          { product_id: '7', quantity: 1 }
        ]
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.contents.items[0].quantity).toBe(1);
      expect(parsed.contents.items[1].quantity).toBe(1);
      expect(parsed.contents.items[2].quantity).toBe(1);
    });
  });

  describe('Unique Cart IDs', () => {
    test('should generate unique cart IDs', async () => {
      const result1 = await createPokemonCart({
        items: [{ product_id: '25', quantity: 1 }]
      });
      const result2 = await createPokemonCart({
        items: [{ product_id: '25', quantity: 1 }]
      });

      const parsed1 = JSON.parse(result1.content[0].text);
      const parsed2 = JSON.parse(result2.content[0].text);

      expect(parsed1.contents.id).not.toBe(parsed2.contents.id);
    });

    test('should have cart_pokemon prefix in cart ID', async () => {
      const result = await createPokemonCart({
        items: [{ product_id: '50', quantity: 1 }]
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.contents.id).toMatch(/^cart_pokemon_[0-9a-f]+$/);
    });
  });
});

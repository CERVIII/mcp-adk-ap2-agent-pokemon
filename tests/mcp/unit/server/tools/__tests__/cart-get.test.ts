/**
 * Tests for cart-get.ts
 * MCP tool: get_current_cart
 * 
 * Note: Integration tests using real cart state
 */

import { describe, test, expect, beforeAll, beforeEach } from '@jest/globals';
import { getCurrentCartTool } from '../../../../../../src/mcp/server/tools/cart-get.js';
import { createPokemonCart } from '../../../../../../src/mcp/server/tools/cart-create.js';
import { loadOrGenerateRSAKeys } from '../../../../../../src/mcp/server/utils/rsa-keys.js';
import { setMerchantPrivateKey } from '../../../../../../src/mcp/server/ap2/cart-mandate.js';
import { setCurrentCart } from '../../../../../../src/mcp/server/ap2/cart-state.js';

describe('getCurrentCartTool', () => {
  beforeAll(async () => {
    // Load RSA keys and inject into cart-mandate module
    const keys = await loadOrGenerateRSAKeys();
    setMerchantPrivateKey(keys.privateKey);
  });

  beforeEach(() => {
    // Clear cart state before each test
    setCurrentCart(null);
  });

  describe('Empty Cart', () => {
    test('should return empty cart message', async () => {
      const result = await getCurrentCartTool();

      expect(result.content).toHaveLength(1);
      expect(result.content[0].type).toBe('text');

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.status).toBe('empty');
      expect(parsed.message).toContain('vacío');
    });

    test('should include suggestion for empty cart', async () => {
      const result = await getCurrentCartTool();
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed).toHaveProperty('suggestion');
      expect(parsed.suggestion).toContain('create_pokemon_cart');
    });

    test('should have emoji in empty message', async () => {
      const result = await getCurrentCartTool();
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed.message).toContain('🛒');
    });
  });

  describe('Active Cart', () => {
    test('should return cart summary after creating cart', async () => {
      // First create a cart
      await createPokemonCart({
        items: [{ product_id: '25', quantity: 1 }]
      });

      // Then get it
      const result = await getCurrentCartTool();
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed.status).toBe('active');
      expect(parsed).toHaveProperty('cart_id');
      expect(parsed).toHaveProperty('items');
      expect(parsed).toHaveProperty('total_usd');
    });

    test('should include merchant information', async () => {
      await createPokemonCart({
        items: [{ product_id: '4', quantity: 1 }]
      });

      const result = await getCurrentCartTool();
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed).toHaveProperty('merchant');
      expect(typeof parsed.merchant).toBe('string');
    });

    test('should include timestamp', async () => {
      await createPokemonCart({
        items: [{ product_id: '7', quantity: 1 }]
      });

      const result = await getCurrentCartTool();
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed).toHaveProperty('created_at');
      expect(new Date(parsed.created_at).toISOString()).toBe(parsed.created_at);
    });

    test('should have ready_for_payment flag', async () => {
      await createPokemonCart({
        items: [{ product_id: '150', quantity: 1 }]
      });

      const result = await getCurrentCartTool();
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed.ready_for_payment).toBe(true);
    });
  });

  describe('Cart Items', () => {
    test('should show single item correctly', async () => {
      await createPokemonCart({
        items: [{ product_id: '25', quantity: 1 }]
      });

      const result = await getCurrentCartTool();
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed.items).toHaveLength(1);
      expect(parsed.items[0]).toHaveProperty('description');
      expect(parsed.items[0]).toHaveProperty('price_usd');
    });

    test('should show multiple items correctly', async () => {
      await createPokemonCart({
        items: [
          { product_id: '25', quantity: 1 },
          { product_id: '4', quantity: 1 }
        ]
      });

      const result = await getCurrentCartTool();
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed.items).toHaveLength(2);
    });

    test('should include item descriptions', async () => {
      await createPokemonCart({
        items: [{ product_id: '1', quantity: 1 }]
      });

      const result = await getCurrentCartTool();
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed.items[0].description).toBeDefined();
      expect(typeof parsed.items[0].description).toBe('string');
    });

    test('should include item prices', async () => {
      await createPokemonCart({
        items: [{ product_id: '6', quantity: 1 }]
      });

      const result = await getCurrentCartTool();
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed.items[0].price_usd).toBeDefined();
      expect(typeof parsed.items[0].price_usd).toBe('number');
      expect(parsed.items[0].price_usd).toBeGreaterThan(0);
    });
  });

  describe('Total Calculation', () => {
    test('should include total in USD', async () => {
      await createPokemonCart({
        items: [{ product_id: '10', quantity: 1 }]
      });

      const result = await getCurrentCartTool();
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed.total_usd).toBeDefined();
      expect(typeof parsed.total_usd).toBe('number');
      expect(parsed.total_usd).toBeGreaterThan(0);
    });

    test('should have USD currency', async () => {
      await createPokemonCart({
        items: [{ product_id: '50', quantity: 1 }]
      });

      const result = await getCurrentCartTool();
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed.currency).toBe('USD');
    });

    test('should match sum of item prices', async () => {
      await createPokemonCart({
        items: [
          { product_id: '25', quantity: 1 },
          { product_id: '4', quantity: 1 }
        ]
      });

      const result = await getCurrentCartTool();
      const parsed = JSON.parse(result.content[0].text);

      const itemsSum = parsed.items.reduce((sum: number, item: any) => sum + item.price_usd, 0);
      expect(parsed.total_usd).toBe(itemsSum);
    });
  });

  describe('JSON Formatting', () => {
    test('should return properly formatted JSON for empty cart', async () => {
      const result = await getCurrentCartTool();

      expect(result.content[0].text).toContain('  "status"');
      expect(() => JSON.parse(result.content[0].text)).not.toThrow();
    });

    test('should return properly formatted JSON for active cart', async () => {
      await createPokemonCart({
        items: [{ product_id: '100', quantity: 1 }]
      });

      const result = await getCurrentCartTool();

      expect(result.content[0].text).toContain('  "status"');
      expect(() => JSON.parse(result.content[0].text)).not.toThrow();
    });

    test('should use 2-space indentation', async () => {
      await createPokemonCart({
        items: [{ product_id: '143', quantity: 1 }]
      });

      const result = await getCurrentCartTool();
      const lines = result.content[0].text.split('\n');
      const indentedLine = lines.find(line => line.startsWith('  "'));

      expect(indentedLine).toBeDefined();
    });
  });

  describe('Cart State Persistence', () => {
    test('should remember cart after creation', async () => {
      await createPokemonCart({
        items: [{ product_id: '25', quantity: 1 }]
      });

      const result1 = await getCurrentCartTool();
      const result2 = await getCurrentCartTool();

      const parsed1 = JSON.parse(result1.content[0].text);
      const parsed2 = JSON.parse(result2.content[0].text);

      expect(parsed1.cart_id).toBe(parsed2.cart_id);
    });

    test('should preserve all cart details', async () => {
      await createPokemonCart({
        items: [
          { product_id: '1', quantity: 1 },
          { product_id: '4', quantity: 1 },
          { product_id: '7', quantity: 1 }
        ]
      });

      const result = await getCurrentCartTool();
      const parsed = JSON.parse(result.content[0].text);

      expect(parsed.items).toHaveLength(3);
      expect(parsed.status).toBe('active');
      expect(parsed.ready_for_payment).toBe(true);
    });
  });
});

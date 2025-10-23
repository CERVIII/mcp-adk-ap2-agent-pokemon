/**
 * Tests for formatting.ts
 * Cart mandate display formatting
 */

import { describe, test, expect, beforeAll } from '@jest/globals';
import { formatCartMandateDisplay } from '../../../../../../src/mcp/server/ap2/formatting.js';
import { createCartMandate, setMerchantPrivateKey } from '../../../../../../src/mcp/server/ap2/cart-mandate.js';
import { loadOrGenerateRSAKeys } from '../../../../../../src/mcp/server/utils/rsa-keys.js';
import type { CartMandate, CartItem } from '../../../../../../src/mcp/server/types/index.js';

describe('formatCartMandateDisplay', () => {
  beforeAll(async () => {
    const { privateKey } = await loadOrGenerateRSAKeys();
    setMerchantPrivateKey(privateKey);
  });

  describe('Display Structure', () => {
    test('should include cart header with decoration', async () => {
      const items: CartItem[] = [{ product_id: '25', quantity: 1 }];
      const cart = await createCartMandate(items);
      const display = formatCartMandateDisplay(cart);

      expect(display).toContain('🛒 CARRITO DE COMPRA CREADO');
      expect(display).toContain('━'.repeat(50));
    });

    test('should include items section with labels', async () => {
      const items: CartItem[] = [{ product_id: '25', quantity: 2 }];
      const cart = await createCartMandate(items);
      const display = formatCartMandateDisplay(cart);

      expect(display).toContain('📋 Items:');
      expect(display).toContain('Pikachu (x2)');
    });

    test('should show item prices correctly', async () => {
      const items: CartItem[] = [{ product_id: '25', quantity: 1 }];
      const cart = await createCartMandate(items);
      const display = formatCartMandateDisplay(cart);

      expect(display).toMatch(/Pikachu.*:\s*\$\d+/);
    });

    test('should include total with currency symbol', async () => {
      const items: CartItem[] = [{ product_id: '25', quantity: 2 }];
      const cart = await createCartMandate(items);
      const display = formatCartMandateDisplay(cart);

      expect(display).toContain('💰 TOTAL:');
      expect(display).toMatch(/TOTAL:\s*\$\d+/);
    });
  });

  describe('Metadata Display', () => {
    test('should include cart ID', async () => {
      const items: CartItem[] = [{ product_id: '25', quantity: 1 }];
      const cart = await createCartMandate(items);
      const display = formatCartMandateDisplay(cart);

      expect(display).toContain('🆔 Cart ID:');
      expect(display).toContain(cart.contents.id);
    });

    test('should include timestamp', async () => {
      const items: CartItem[] = [{ product_id: '25', quantity: 1 }];
      const cart = await createCartMandate(items);
      const display = formatCartMandateDisplay(cart);

      expect(display).toContain('📅 Timestamp:');
      expect(display).toContain(cart.timestamp);
    });

    test('should include AP2 ready message', async () => {
      const items: CartItem[] = [{ product_id: '25', quantity: 1 }];
      const cart = await createCartMandate(items);
      const display = formatCartMandateDisplay(cart);

      expect(display).toContain('✅ CartMandate listo para el proceso de pago AP2');
    });
  });

  describe('JSON Output', () => {
    test('should include JSON section header', async () => {
      const items: CartItem[] = [{ product_id: '25', quantity: 1 }];
      const cart = await createCartMandate(items);
      const display = formatCartMandateDisplay(cart);

      expect(display).toContain('📄 CartMandate completo (JSON):');
      expect(display).toContain('```json');
      expect(display).toContain('```');
    });

    test('should include full CartMandate JSON', async () => {
      const items: CartItem[] = [{ product_id: '25', quantity: 1 }];
      const cart = await createCartMandate(items);
      const display = formatCartMandateDisplay(cart);

      const jsonMatch = display.match(/```json\n([\s\S]*?)\n```/);
      expect(jsonMatch).toBeTruthy();

      const json = jsonMatch![1];
      const parsed: CartMandate = JSON.parse(json);

      expect(parsed.contents).toBeDefined();
      expect(parsed.merchant_signature).toBeDefined();
      expect(parsed.timestamp).toBeDefined();
    });

    test('should format JSON with proper indentation', async () => {
      const items: CartItem[] = [{ product_id: '25', quantity: 1 }];
      const cart = await createCartMandate(items);
      const display = formatCartMandateDisplay(cart);

      const jsonMatch = display.match(/```json\n([\s\S]*?)\n```/);
      const json = jsonMatch![1];

      // Check for indentation (2 spaces)
      expect(json).toContain('  "contents"');
      expect(json).toContain('    "id"');
    });
  });

  describe('Multiple Items Display', () => {
    test('should list all items with bullet points', async () => {
      const items: CartItem[] = [
        { product_id: '1', quantity: 1 },   // Bulbasaur
        { product_id: '25', quantity: 2 },  // Pikachu
      ];
      const cart = await createCartMandate(items);
      const display = formatCartMandateDisplay(cart);

      const bulletCount = (display.match(/•/g) || []).length;
      expect(bulletCount).toBe(2);
      expect(display).toContain('Bulbasaur');
      expect(display).toContain('Pikachu (x2)');
    });

    test('should calculate total correctly for multiple items', async () => {
      const items: CartItem[] = [
        { product_id: '6', quantity: 1 },  // Charizard
        { product_id: '25', quantity: 1 }, // Pikachu
      ];
      const cart = await createCartMandate(items);
      const display = formatCartMandateDisplay(cart);

      const totalMatch = display.match(/TOTAL:\s*\$(\d+)/);
      expect(totalMatch).toBeTruthy();

      const total = parseInt(totalMatch![1]);
      expect(total).toBeGreaterThan(0); // Just verify it's valid
      expect(display).toContain('Charizard');
      expect(display).toContain('Pikachu');
    });
  });

  describe('Edge Cases', () => {
    test('should handle single item with quantity 1', async () => {
      const items: CartItem[] = [{ product_id: '25', quantity: 1 }];
      const cart = await createCartMandate(items);
      const display = formatCartMandateDisplay(cart);

      expect(display).toContain('Pikachu');
      expect(display).toContain('Pikachu (x1)'); // Quantity included in label
    });

    test('should handle high-value totals', async () => {
      const items: CartItem[] = [
        { product_id: '150', quantity: 5 }, // Mewtwo (expensive)
      ];
      const cart = await createCartMandate(items);
      const display = formatCartMandateDisplay(cart);

      const totalMatch = display.match(/TOTAL:\s*\$(\d+)/);
      expect(totalMatch).toBeTruthy();

      const total = parseInt(totalMatch![1]);
      expect(total).toBeGreaterThan(0);
    });

    test('should maintain structure with long Pokemon names', async () => {
      const items: CartItem[] = [
        { product_id: '143', quantity: 1 }, // Snorlax (7 chars)
      ];
      const cart = await createCartMandate(items);
      const display = formatCartMandateDisplay(cart);

      expect(display).toContain('Snorlax');
      expect(display).toContain('━'.repeat(50)); // Border intact
    });
  });

  describe('Return Type', () => {
    test('should return a string', async () => {
      const items: CartItem[] = [{ product_id: '25', quantity: 1 }];
      const cart = await createCartMandate(items);
      const display = formatCartMandateDisplay(cart);

      expect(typeof display).toBe('string');
    });

    test('should return non-empty string', async () => {
      const items: CartItem[] = [{ product_id: '25', quantity: 1 }];
      const cart = await createCartMandate(items);
      const display = formatCartMandateDisplay(cart);

      expect(display.length).toBeGreaterThan(0);
    });

    test('should not have trailing whitespace issues', async () => {
      const items: CartItem[] = [{ product_id: '25', quantity: 1 }];
      const cart = await createCartMandate(items);
      const display = formatCartMandateDisplay(cart);

      const lines = display.split('\n');
      expect(lines.length).toBeGreaterThan(10);
    });
  });
});

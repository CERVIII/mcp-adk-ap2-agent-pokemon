/**
 * Tests para cart-state.ts - Gestión de estado del carrito
 */
import { describe, it, expect, beforeEach } from '@jest/globals';
import { getCurrentCart, setCurrentCart, clearCart } from '../../../../../../src/mcp/server/ap2/cart-state.js';
import type { CartMandate } from '../../../../../../src/mcp/server/types/index.js';

describe('Cart State Management', () => {
  const createMockCart = (id: string, itemCount: number = 0): CartMandate => ({
    contents: {
      id,
      user_signature_required: false,
      user_cart_confirmation_required: false,
      merchant_name: 'PokeMart - Primera Generación',
      payment_request: {
        method_data: [{
          supported_methods: 'CARD',
          data: { payment_processor_url: 'http://localhost:8003/a2a/processor' },
        }],
        details: {
          id: `order_${id}`,
          displayItems: [],
          shipping_options: null,
          modifiers: null,
          total: { label: 'Total', amount: { currency: 'USD', value: itemCount * 51 } },
        },
        options: {
          requestPayerName: false,
          requestPayerEmail: false,
          requestPayerPhone: false,
          requestShipping: false,
          shippingType: null,
        },
      },
      items: [],
    },
    merchant_signature: `sig_merchant_pokemon_${id}`,
    timestamp: new Date().toISOString(),
  });

  beforeEach(() => {
    clearCart();
  });

  describe('getCurrentCart', () => {
    it('should return null when no cart is set', () => {
      expect(getCurrentCart()).toBeNull();
    });

    it('should return the current cart when set', () => {
      const mockCart = createMockCart('cart_test');
      setCurrentCart(mockCart);
      expect(getCurrentCart()).toEqual(mockCart);
    });
  });

  describe('setCurrentCart', () => {
    it('should set a cart', () => {
      const mockCart = createMockCart('cart_123', 1);
      setCurrentCart(mockCart);
      const result = getCurrentCart();
      
      expect(result).not.toBeNull();
      expect(result?.contents.id).toBe('cart_123');
      expect(result?.contents.payment_request.details.total.amount.value).toBe(51);
    });

    it('should update existing cart', () => {
      const cart1 = createMockCart('cart_1', 0);
      const cart2 = createMockCart('cart_2', 2);

      setCurrentCart(cart1);
      expect(getCurrentCart()?.contents.id).toBe('cart_1');
      
      setCurrentCart(cart2);
      expect(getCurrentCart()?.contents.id).toBe('cart_2');
      expect(getCurrentCart()?.contents.payment_request.details.total.amount.value).toBe(102);
    });

    it('should allow setting cart to null', () => {
      const mockCart = createMockCart('cart_temp');
      setCurrentCart(mockCart);
      expect(getCurrentCart()).not.toBeNull();
      
      setCurrentCart(null);
      expect(getCurrentCart()).toBeNull();
    });
  });

  describe('clearCart', () => {
    it('should clear the cart', () => {
      const mockCart = createMockCart('cart_clear_test', 2);
      setCurrentCart(mockCart);
      expect(getCurrentCart()).not.toBeNull();
      
      clearCart();
      expect(getCurrentCart()).toBeNull();
    });

    it('should be safe to call clearCart multiple times', () => {
      clearCart();
      expect(getCurrentCart()).toBeNull();
      
      clearCart();
      expect(getCurrentCart()).toBeNull();
    });
  });
});

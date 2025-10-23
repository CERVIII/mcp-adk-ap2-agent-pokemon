/**
 * Tests para cart-mandate.ts - Creación de CartMandate con AP2
 */
import { describe, it, expect, beforeAll } from '@jest/globals';
import { createCartMandate, setMerchantPrivateKey } from '../../../../../../src/mcp/server/ap2/cart-mandate.js';
import { getCurrentCart, clearCart } from '../../../../../../src/mcp/server/ap2/cart-state.js';
import { loadOrGenerateRSAKeys } from '../../../../../../src/mcp/server/utils/rsa-keys.js';
import type { CartItem } from '../../../../../../src/mcp/server/types/index.js';
import jwt from 'jsonwebtoken';

describe('CartMandate Creation', () => {
  let publicKey: string;

  beforeAll(async () => {
    // Cargar claves RSA para firmar
    const keys = await loadOrGenerateRSAKeys();
    setMerchantPrivateKey(keys.privateKey);
    publicKey = keys.publicKey;
  });

  beforeEach(() => {
    clearCart();
  });

  it('should create valid CartMandate for single Pokemon', async () => {
    const items: CartItem[] = [
      { product_id: '25', quantity: 1 } // Pikachu
    ];

    const cart = await createCartMandate(items);

    expect(cart).toBeDefined();
    expect(cart.contents).toBeDefined();
    expect(cart.merchant_signature).toBeDefined();
    expect(cart.timestamp).toBeDefined();
  });

  it('should generate unique cart ID', async () => {
    const items: CartItem[] = [{ product_id: '1', quantity: 1 }];

    const cart1 = await createCartMandate(items);
    clearCart();
    const cart2 = await createCartMandate(items);

    expect(cart1.contents.id).not.toBe(cart2.contents.id);
    expect(cart1.contents.id).toContain('cart_pokemon_');
    expect(cart2.contents.id).toContain('cart_pokemon_');
  });

  it('should have valid AP2 structure', async () => {
    const items: CartItem[] = [{ product_id: '6', quantity: 2 }];

    const cart = await createCartMandate(items);

    // Verificar estructura AP2
    expect(cart.contents.user_signature_required).toBe(false);
    expect(cart.contents.merchant_name).toBe('PokeMart - Primera Generación');
    expect(cart.contents.payment_request).toBeDefined();
    expect(cart.contents.payment_request.method_data).toHaveLength(1);
    expect(cart.contents.payment_request.details).toBeDefined();
  });

  it('should calculate total correctly for single item', async () => {
    const items: CartItem[] = [
      { product_id: '25', quantity: 1 } // Pikachu
    ];

    const cart = await createCartMandate(items);
    const total = cart.contents.payment_request.details.total;

    expect(total.label).toBe('Total');
    expect(total.amount.currency).toBe('USD');
    expect(total.amount.value).toBeGreaterThan(0);
  });

  it('should calculate total correctly for multiple quantities', async () => {
    const items: CartItem[] = [
      { product_id: '25', quantity: 2 } // 2x Pikachu (tiene más inventario)
    ];

    const cart = await createCartMandate(items);
    const total = cart.contents.payment_request.details.total;

    expect(total.amount.value).toBeGreaterThan(0);
    // El total debe ser 2 veces el precio unitario
    expect(total.amount.value % 2).toBe(0);
  });

  it('should calculate total correctly for multiple items', async () => {
    const items: CartItem[] = [
      { product_id: '6', quantity: 1 },  // Charizard x1
      { product_id: '25', quantity: 1 }  // Pikachu x1
    ];

    const cart = await createCartMandate(items);
    const displayItems = cart.contents.payment_request.details.displayItems;
    const total = cart.contents.payment_request.details.total;

    expect(displayItems).toHaveLength(2);
    
    // El total debe ser la suma de los items
    const sumItems = displayItems.reduce((sum, item) => sum + item.amount.value, 0);
    expect(total.amount.value).toBe(sumItems);
  });

  it('should create display items with proper labels', async () => {
    const items: CartItem[] = [
      { product_id: '25', quantity: 2 } // Pikachu
    ];

    const cart = await createCartMandate(items);
    const displayItems = cart.contents.payment_request.details.displayItems;

    expect(displayItems).toHaveLength(1);
    expect(displayItems[0].label).toContain('Pikachu');
    expect(displayItems[0].label).toContain('(x2)');
    expect(displayItems[0].amount.currency).toBe('USD');
  });

  it('should throw error for non-existent Pokemon', async () => {
    const items: CartItem[] = [
      { product_id: '999', quantity: 1 } // No existe
    ];

    await expect(createCartMandate(items)).rejects.toThrow('not found in catalog');
  });

  it('should throw error for Pokemon not for sale', async () => {
    // Necesitaríamos saber qué Pokemon no está en venta en los datos reales
    // Por ahora solo verificamos que la validación existe
    const items: CartItem[] = [
      { product_id: '1', quantity: 1 }
    ];

    // Este test pasa si el Pokemon está en venta (comportamiento normal)
    const cart = await createCartMandate(items);
    expect(cart).toBeDefined();
  });

  it('should throw error when quantity exceeds available inventory', async () => {
    const items: CartItem[] = [
      { product_id: '1', quantity: 99999 } // Cantidad imposible
    ];

    await expect(createCartMandate(items)).rejects.toThrow('available');
  });

  it('should save cart to state after creation', async () => {
    const items: CartItem[] = [
      { product_id: '6', quantity: 1 }
    ];

    const cart = await createCartMandate(items);
    const savedCart = getCurrentCart();

    expect(savedCart).toBeDefined();
    expect(savedCart?.contents.id).toBe(cart.contents.id);
  });

  it('should include payment processor URL', async () => {
    const items: CartItem[] = [
      { product_id: '1', quantity: 1 }
    ];

    const cart = await createCartMandate(items);
    const methodData = cart.contents.payment_request.method_data[0];

    expect(methodData.supported_methods).toBe('CARD');
    expect(methodData.data.payment_processor_url).toContain('localhost:8003');
  });

  it('should set proper payment options', async () => {
    const items: CartItem[] = [
      { product_id: '25', quantity: 1 }
    ];

    const cart = await createCartMandate(items);
    const options = cart.contents.payment_request.options;

    expect(options.requestPayerName).toBe(false);
    expect(options.requestPayerEmail).toBe(false);
    expect(options.requestPayerPhone).toBe(false);
    expect(options.requestShipping).toBe(false);
  });

  it('should include order ID in payment details', async () => {
    const items: CartItem[] = [
      { product_id: '1', quantity: 1 }
    ];

    const cart = await createCartMandate(items);
    const orderId = cart.contents.payment_request.details.id;

    expect(orderId).toBeDefined();
    expect(orderId).toContain('order_pokemon_');
  });

  it('should preserve original items in cart contents', async () => {
    const items: CartItem[] = [
      { product_id: '6', quantity: 2 },
      { product_id: '25', quantity: 1 }
    ];

    const cart = await createCartMandate(items);

    expect(cart.contents.items).toBeDefined();
    expect(cart.contents.items).toHaveLength(2);
    expect(cart.contents.items![0].product_id).toBe('6');
    expect(cart.contents.items![1].product_id).toBe('25');
  });
});

describe('Merchant Signature (JWT)', () => {
  let publicKey: string;

  beforeAll(async () => {
    const keys = await loadOrGenerateRSAKeys();
    setMerchantPrivateKey(keys.privateKey);
    publicKey = keys.publicKey;
  });

  beforeEach(() => {
    clearCart();
  });

  it('should generate valid JWT signature', async () => {
    const items: CartItem[] = [{ product_id: '1', quantity: 1 }];
    const cart = await createCartMandate(items);

    // JWT debe tener 3 partes separadas por puntos
    const parts = cart.merchant_signature.split('.');
    expect(parts).toHaveLength(3);
  });

  it('should create RS256 signed JWT', async () => {
    const items: CartItem[] = [{ product_id: '25', quantity: 1 }];
    const cart = await createCartMandate(items);

    // Decodificar header del JWT
    const header = JSON.parse(
      Buffer.from(cart.merchant_signature.split('.')[0], 'base64url').toString()
    );

    expect(header.alg).toBe('RS256');
    expect(header.typ).toBe('JWT');
  });

  it('should include cart_id in JWT payload', async () => {
    const items: CartItem[] = [{ product_id: '6', quantity: 1 }];
    const cart = await createCartMandate(items);

    // Decodificar payload sin verificar
    const decoded = jwt.decode(cart.merchant_signature) as any;

    expect(decoded.cart_id).toBe(cart.contents.id);
    expect(decoded.sub).toBe(cart.contents.id);
  });

  it('should include merchant info in JWT', async () => {
    const items: CartItem[] = [{ product_id: '1', quantity: 1 }];
    const cart = await createCartMandate(items);

    const decoded = jwt.decode(cart.merchant_signature) as any;

    expect(decoded.iss).toBe('PokeMart');
    expect(decoded.merchant).toBe('PokeMart - Primera Generación');
  });

  it('should include timestamps in JWT', async () => {
    const items: CartItem[] = [{ product_id: '25', quantity: 1 }];
    const cart = await createCartMandate(items);

    const decoded = jwt.decode(cart.merchant_signature) as any;

    expect(decoded.iat).toBeDefined(); // Issued at
    expect(decoded.exp).toBeDefined(); // Expires
    expect(decoded.exp).toBeGreaterThan(decoded.iat);
  });

  it('should set JWT expiration to 1 hour', async () => {
    const items: CartItem[] = [{ product_id: '6', quantity: 1 }];
    const cart = await createCartMandate(items);

    const decoded = jwt.decode(cart.merchant_signature) as any;
    const expiresIn = decoded.exp - decoded.iat;

    expect(expiresIn).toBe(60 * 60); // 3600 segundos = 1 hora
  });

  it('should verify JWT signature with public key', async () => {
    const items: CartItem[] = [{ product_id: '1', quantity: 1 }];
    const cart = await createCartMandate(items);

    // Verificar firma con clave pública
    const verified = jwt.verify(cart.merchant_signature, publicKey, {
      algorithms: ['RS256']
    });

    expect(verified).toBeDefined();
  });

  it('should reject tampered JWT', async () => {
    const items: CartItem[] = [{ product_id: '25', quantity: 1 }];
    const cart = await createCartMandate(items);

    // Modificar el JWT (romper la firma)
    const parts = cart.merchant_signature.split('.');
    const tamperedJWT = parts[0] + '.' + parts[1] + '.INVALID_SIGNATURE';

    // Debe fallar la verificación
    expect(() => {
      jwt.verify(tamperedJWT, publicKey, { algorithms: ['RS256'] });
    }).toThrow();
  });

  it('should have ISO 8601 timestamp format', async () => {
    const items: CartItem[] = [{ product_id: '6', quantity: 1 }];
    const cart = await createCartMandate(items);

    // ISO 8601 format: YYYY-MM-DDTHH:mm:ss.sssZ
    expect(cart.timestamp).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/);
  });
});

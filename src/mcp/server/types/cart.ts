/**
 * AP2 Protocol Types
 * Types for Agent Payments Protocol v2 (CartMandate, PaymentRequest, etc.)
 */

export interface PaymentAmount {
  currency: string;
  value: number;
}

export interface DisplayItem {
  label: string;
  amount: PaymentAmount;
}

export interface PaymentMethodData {
  supported_methods: string;
  data: {
    payment_processor_url: string;
  };
}

export interface PaymentDetails {
  id: string;
  displayItems: DisplayItem[];
  shipping_options: null;
  modifiers: null;
  total: {
    label: string;
    amount: PaymentAmount;
  };
}

export interface PaymentOptions {
  requestPayerName: boolean;
  requestPayerEmail: boolean;
  requestPayerPhone: boolean;
  requestShipping: boolean;
  shippingType: null;
}

export interface PaymentRequest {
  method_data: PaymentMethodData[];
  details: PaymentDetails;
  options: PaymentOptions;
}

export interface CartItem {
  product_id: string;
  quantity: number;
}

export interface CartMandateContents {
  id: string;
  user_signature_required: boolean;
  user_cart_confirmation_required: boolean;
  merchant_name: string;
  payment_request: PaymentRequest;
  cart_expiry?: string | null;
  items?: CartItem[];  // Extension: preserve original items for inventory management
}

export interface CartMandate {
  contents: CartMandateContents;
  merchant_signature: string;
  timestamp: string;
}

export interface Cart {
  id: string;
  items: CartItem[];
  total: number;
  currency: string;
  created_at: string;
}

---
title: "[Phase 6.1] Agent Discovery Protocol"
labels: enhancement, ap2, agent, phase-6
assignees: CERVIII
---

## 📋 Descripción

Implementar protocolo de descubrimiento de agentes (Agent Discovery Protocol) para que shopping agents puedan encontrar merchants dinámicamente vía `.well-known` endpoints y negociar capabilities.

## 🎯 Tipo de Issue

- [x] 🤖 AP2 Protocol
- [x] ✨ Nueva feature
- [x] 🌐 Microservices

## 📦 Fase del Roadmap

**Fase 6.1: Protocolo de Descubrimiento**

## ✅ Tareas

### .well-known Endpoint Implementation

#### Merchant Discovery Endpoint
```python
# ap2-integration/src/merchant_agent/server.py

@app.get("/.well-known/ap2-merchant")
async def ap2_discovery():
    """RFC 8615 compliant well-known endpoint"""
    return {
        "version": "1.0",
        "merchant": {
            "id": "pokemart-gen1",
            "name": "PokeMart - Primera Generación",
            "description": "Pokemon marketplace with Gen 1 catalog",
            "logo": "https://pokemart.example.com/logo.png",
            "url": "https://pokemart.example.com"
        },
        "endpoints": {
            "catalog": "https://pokemart.example.com/api/catalog",
            "search": "https://pokemart.example.com/api/search",
            "cart": "https://pokemart.example.com/api/cart",
            "checkout": "https://pokemart.example.com/api/cart/checkout",
            "payment": "https://pokemart.example.com/api/payment"
        },
        "capabilities": {
            "payment_methods": ["stripe", "paypal", "crypto", "apple_pay"],
            "currencies": ["USD"],
            "shipping": {
                "regions": ["US", "CA", "EU"],
                "methods": ["standard", "express", "overnight"]
            },
            "authentication": {
                "required": true,
                "methods": ["oauth2", "webauthn"]
            },
            "cart": {
                "session_based": true,
                "ttl": 86400  # 24 hours
            }
        },
        "mcp": {
            "available": true,
            "version": "1.0",
            "transport": "stdio",
            "tools": [
                "get_pokemon_info",
                "get_pokemon_price",
                "search_pokemon",
                "list_pokemon_types",
                "create_pokemon_cart",
                "get_pokemon_product"
            ]
        },
        "ap2": {
            "version": "2.0",
            "payment_processor": "https://pokemart.example.com/a2a/processor",
            "signature_required": true,
            "mandate_types": ["cart", "intent"]
        },
        "rate_limits": {
            "requests_per_minute": 60,
            "burst": 100
        },
        "contact": {
            "email": "support@pokemart.example.com",
            "support_url": "https://pokemart.example.com/support"
        }
    }
```

### Agent Registry Service

#### Centralized Registry
```python
# New service: ap2-integration/src/registry_service/server.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List, Dict

app = FastAPI(title="AP2 Agent Registry")

class MerchantRegistration(BaseModel):
    merchant_id: str
    name: str
    discovery_url: HttpUrl  # https://merchant.com/.well-known/ap2-merchant
    categories: List[str]  # ['pokemon', 'items', 'trading_cards']
    verified: bool = False

# In-memory registry (in production: use Redis or database)
merchants: Dict[str, MerchantRegistration] = {}

@app.post("/api/registry/merchants")
async def register_merchant(merchant: MerchantRegistration):
    """Register a new merchant in the registry"""
    # Verify discovery endpoint
    try:
        response = requests.get(str(merchant.discovery_url))
        response.raise_for_status()
        discovery_data = response.json()
        
        # Validate AP2 compliance
        assert "version" in discovery_data
        assert "merchant" in discovery_data
        assert "endpoints" in discovery_data
        
        merchants[merchant.merchant_id] = merchant
        return {"status": "registered", "merchant_id": merchant.merchant_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Discovery verification failed: {e}")

@app.get("/api/registry/merchants")
async def list_merchants(category: str = None):
    """List all registered merchants, optionally filtered by category"""
    result = list(merchants.values())
    if category:
        result = [m for m in result if category in m.categories]
    return result

@app.get("/api/registry/merchants/{merchant_id}")
async def get_merchant(merchant_id: str):
    """Get detailed merchant info"""
    if merchant_id not in merchants:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    merchant = merchants[merchant_id]
    
    # Fetch live discovery data
    response = requests.get(str(merchant.discovery_url))
    discovery_data = response.json()
    
    return {
        "merchant": merchant,
        "discovery": discovery_data
    }

@app.get("/api/registry/search")
async def search_merchants(
    query: str,
    category: str = None,
    payment_method: str = None,
    region: str = None
):
    """Search merchants by capabilities"""
    results = []
    
    for merchant_id, merchant in merchants.items():
        # Fetch discovery data
        try:
            response = requests.get(str(merchant.discovery_url))
            discovery = response.json()
            
            # Filter by query
            if query.lower() not in merchant.name.lower():
                continue
            
            # Filter by category
            if category and category not in merchant.categories:
                continue
            
            # Filter by payment method
            if payment_method:
                supported = discovery.get("capabilities", {}).get("payment_methods", [])
                if payment_method not in supported:
                    continue
            
            # Filter by region
            if region:
                regions = discovery.get("capabilities", {}).get("shipping", {}).get("regions", [])
                if region not in regions:
                    continue
            
            results.append({
                "merchant": merchant,
                "discovery": discovery
            })
        except:
            continue
    
    return results
```

### Shopping Agent Discovery Client

```python
# ap2-integration/src/shopping_agent/discovery.py

import requests
from typing import List, Dict, Optional

class MerchantDiscovery:
    def __init__(self, registry_url: str = "http://localhost:8002"):
        self.registry_url = registry_url
    
    def discover_merchant(self, merchant_url: str) -> Dict:
        """Fetch merchant capabilities via .well-known endpoint"""
        discovery_url = f"{merchant_url}/.well-known/ap2-merchant"
        response = requests.get(discovery_url)
        response.raise_for_status()
        return response.json()
    
    def search_merchants(
        self,
        query: str = "",
        category: str = None,
        payment_method: str = None,
        region: str = None
    ) -> List[Dict]:
        """Search for merchants in registry"""
        params = {"query": query}
        if category:
            params["category"] = category
        if payment_method:
            params["payment_method"] = payment_method
        if region:
            params["region"] = region
        
        response = requests.get(f"{self.registry_url}/api/registry/search", params=params)
        response.raise_for_status()
        return response.json()
    
    def negotiate_capabilities(self, merchant_discovery: Dict, requirements: Dict) -> bool:
        """Check if merchant meets agent requirements"""
        caps = merchant_discovery.get("capabilities", {})
        
        # Check payment methods
        if "payment_method" in requirements:
            supported = caps.get("payment_methods", [])
            if requirements["payment_method"] not in supported:
                return False
        
        # Check currency
        if "currency" in requirements:
            supported = caps.get("currencies", [])
            if requirements["currency"] not in supported:
                return False
        
        # Check shipping region
        if "region" in requirements:
            regions = caps.get("shipping", {}).get("regions", [])
            if requirements["region"] not in regions:
                return False
        
        # Check authentication
        if requirements.get("authentication_required"):
            if not caps.get("authentication", {}).get("required"):
                return False
        
        return True
```

### Frontend Merchant Selector

```html
<!-- New UI: Select merchant dynamically -->
<div class="merchant-selector">
  <h3>Choose Pokemon Marketplace</h3>
  <div id="merchants-grid"></div>
</div>

<script>
async function loadMerchants() {
    const response = await fetch('http://localhost:8002/api/registry/merchants?category=pokemon');
    const merchants = await response.json();
    
    const grid = document.getElementById('merchants-grid');
    merchants.forEach(merchant => {
        const card = document.createElement('div');
        card.className = 'merchant-card';
        card.innerHTML = `
            <img src="${merchant.logo}" alt="${merchant.name}" />
            <h4>${merchant.name}</h4>
            <p>${merchant.description}</p>
            <div class="badges">
                ${merchant.verified ? '<span class="badge">✓ Verified</span>' : ''}
            </div>
            <button onclick="selectMerchant('${merchant.merchant_id}')">
                Shop Now
            </button>
        `;
        grid.appendChild(card);
    });
}

async function selectMerchant(merchantId) {
    // Fetch discovery data
    const response = await fetch(`http://localhost:8002/api/registry/merchants/${merchantId}`);
    const data = await response.json();
    
    // Store merchant endpoints
    localStorage.setItem('selected_merchant', JSON.stringify(data.discovery));
    
    // Redirect to catalog
    window.location.href = '/catalog';
}
</script>
```

### Capability Negotiation Protocol

```python
# ap2-integration/src/common/negotiation.py

from typing import Dict, List

class CapabilityNegotiator:
    def __init__(self, agent_capabilities: Dict):
        self.agent_capabilities = agent_capabilities
    
    def negotiate(self, merchant_discovery: Dict) -> Dict:
        """Negotiate optimal configuration between agent and merchant"""
        merchant_caps = merchant_discovery.get("capabilities", {})
        
        negotiated = {
            "payment_method": self._negotiate_payment(merchant_caps),
            "currency": self._negotiate_currency(merchant_caps),
            "shipping": self._negotiate_shipping(merchant_caps),
            "authentication": self._negotiate_auth(merchant_caps)
        }
        
        return negotiated
    
    def _negotiate_payment(self, merchant_caps: Dict) -> str:
        """Select best available payment method"""
        agent_prefs = self.agent_capabilities.get("payment_methods", [])
        merchant_methods = merchant_caps.get("payment_methods", [])
        
        # Priority order
        priority = ["crypto", "stripe", "paypal", "apple_pay"]
        
        for method in priority:
            if method in agent_prefs and method in merchant_methods:
                return method
        
        # Fallback to first common method
        common = set(agent_prefs) & set(merchant_methods)
        return list(common)[0] if common else None
    
    def _negotiate_currency(self, merchant_caps: Dict) -> str:
        """Select currency"""
        agent_currency = self.agent_capabilities.get("currency", "USD")
        merchant_currencies = merchant_caps.get("currencies", [])
        
        return agent_currency if agent_currency in merchant_currencies else merchant_currencies[0]
    
    def _negotiate_shipping(self, merchant_caps: Dict) -> Dict:
        """Select shipping method and verify region"""
        agent_region = self.agent_capabilities.get("region", "US")
        merchant_shipping = merchant_caps.get("shipping", {})
        
        if agent_region not in merchant_shipping.get("regions", []):
            raise ValueError(f"Merchant does not ship to {agent_region}")
        
        # Prefer fastest method
        methods = merchant_shipping.get("methods", [])
        if "overnight" in methods:
            return {"method": "overnight", "region": agent_region}
        elif "express" in methods:
            return {"method": "express", "region": agent_region}
        else:
            return {"method": "standard", "region": agent_region}
    
    def _negotiate_auth(self, merchant_caps: Dict) -> Dict:
        """Negotiate authentication method"""
        merchant_auth = merchant_caps.get("authentication", {})
        
        if not merchant_auth.get("required"):
            return {"required": False}
        
        agent_methods = self.agent_capabilities.get("auth_methods", [])
        merchant_methods = merchant_auth.get("methods", [])
        
        # Prefer WebAuthn
        if "webauthn" in agent_methods and "webauthn" in merchant_methods:
            return {"required": True, "method": "webauthn"}
        elif "oauth2" in agent_methods and "oauth2" in merchant_methods:
            return {"required": True, "method": "oauth2"}
        else:
            raise ValueError("No compatible authentication method")
```

## 📝 Criterios de Aceptación

- [ ] `.well-known/ap2-merchant` endpoint funciona
- [ ] Registry service puede register merchants
- [ ] Registry search funciona
- [ ] Shopping agent puede discover merchants
- [ ] Capability negotiation funciona
- [ ] Frontend puede listar merchants
- [ ] Incompatible merchants son filtrados

## 🧪 Testing

```python
def test_discovery_endpoint():
    response = client.get("/.well-known/ap2-merchant")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "merchant" in data
    assert "capabilities" in data

def test_merchant_registration():
    merchant = {
        "merchant_id": "pokemart-test",
        "name": "Test PokeMart",
        "discovery_url": "http://localhost:8001/.well-known/ap2-merchant",
        "categories": ["pokemon"]
    }
    response = client.post("/api/registry/merchants", json=merchant)
    assert response.status_code == 200

def test_capability_negotiation():
    agent_caps = {
        "payment_methods": ["stripe", "crypto"],
        "currency": "USD",
        "region": "US"
    }
    merchant_discovery = client.get("/.well-known/ap2-merchant").json()
    
    negotiator = CapabilityNegotiator(agent_caps)
    result = negotiator.negotiate(merchant_discovery)
    
    assert result["payment_method"] in ["stripe", "crypto"]
    assert result["currency"] == "USD"
```

## ⏱️ Estimación

**Tiempo:** 2 semanas
**Prioridad:** High (prerequisite for Phase 6.2)
**Complejidad:** Medium-High

## 🔗 Issues Relacionados

Prerequisito para: #phase-6-2-intent-mandates, #phase-6-3-multi-merchant
Relacionado con: #phase-4-1-authentication

## 📚 Recursos

- [RFC 8615: Well-Known URIs](https://datatracker.ietf.org/doc/html/rfc8615)
- [OpenAPI Discovery](https://swagger.io/specification/)
- [Service Discovery Patterns](https://microservices.io/patterns/server-side-discovery.html)

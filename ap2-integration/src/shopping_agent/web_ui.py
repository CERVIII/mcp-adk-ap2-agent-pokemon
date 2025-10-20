"""
Shopping Agent Web UI - Interactive interface for Pokemon purchases with AP2
"""

import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn

from src.shopping_agent.agent import ShoppingAgent

app = FastAPI(title="Pokemon Shopping Agent", version="1.0.0")
agent = ShoppingAgent()

# In-memory shopping cart
shopping_cart: List[Dict[str, Any]] = []


class SearchRequest(BaseModel):
    query: Optional[str] = None
    type: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    only_available: bool = True
    limit: int = 20


class PurchaseRequest(BaseModel):
    pokemon_id: str
    quantity: int = 1


class CartItem(BaseModel):
    product_id: str
    quantity: int


class CartRequest(BaseModel):
    items: List[CartItem]


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main UI"""
    html_content = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🛍️ Pokemon Shopping Agent (AP2)</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .main-content {
            padding: 30px;
        }
        
        .search-section {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 30px;
        }
        
        .search-title {
            font-size: 1.5em;
            color: #333;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .search-form {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        
        .form-group {
            display: flex;
            flex-direction: column;
        }
        
        .form-group.full-width {
            grid-column: 1 / -1;
        }
        
        label {
            font-weight: 600;
            color: #555;
            margin-bottom: 5px;
            font-size: 0.9em;
        }
        
        input, select {
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.3s;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .search-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 1.1em;
            border-radius: 10px;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            font-weight: 600;
        }
        
        .search-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .search-btn:active {
            transform: translateY(0);
        }
        
        .results-section {
            margin-top: 30px;
        }
        
        .results-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .pokemon-card {
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 15px;
            padding: 20px;
            transition: transform 0.3s, box-shadow 0.3s;
            cursor: pointer;
        }
        
        .pokemon-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.2);
            border-color: #667eea;
        }
        
        .pokemon-image {
            width: 120px;
            height: 120px;
            margin: 0 auto 15px;
            display: block;
        }
        
        .pokemon-name {
            font-size: 1.4em;
            font-weight: bold;
            color: #333;
            text-align: center;
            margin-bottom: 10px;
            text-transform: capitalize;
        }
        
        .pokemon-number {
            text-align: center;
            color: #888;
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        
        .pokemon-types {
            display: flex;
            justify-content: center;
            gap: 8px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }
        
        .type-badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 600;
            text-transform: uppercase;
            color: white;
        }
        
        .pokemon-price {
            font-size: 1.8em;
            font-weight: bold;
            color: #27ae60;
            text-align: center;
            margin: 15px 0;
        }
        
        .pokemon-stock {
            text-align: center;
            margin-bottom: 15px;
        }
        
        .stock-available {
            color: #27ae60;
            font-weight: 600;
        }
        
        .stock-unavailable {
            color: #e74c3c;
            font-weight: 600;
        }
        
        .buy-btn {
            width: 100%;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            border: none;
            padding: 12px;
            border-radius: 8px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .buy-btn:hover {
            transform: scale(1.05);
        }
        
        .buy-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            font-size: 1.2em;
            color: #667eea;
        }
        
        .error {
            background: #fee;
            border: 2px solid #e74c3c;
            color: #c0392b;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
        }
        
        .success {
            background: #d4edda;
            border: 2px solid #28a745;
            color: #155724;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
        }
        
        .cart-summary {
            background: #fff3cd;
            border: 2px solid #ffc107;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.7);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }
        
        .modal.show {
            display: flex;
        }
        
        .modal-content {
            background: white;
            padding: 30px;
            border-radius: 15px;
            max-width: 600px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .modal-title {
            font-size: 1.8em;
            color: #333;
        }
        
        .close-btn {
            background: none;
            border: none;
            font-size: 2em;
            cursor: pointer;
            color: #999;
        }
        
        .close-btn:hover {
            color: #333;
        }
        
        pre {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 0.9em;
        }
        
        .quick-demo {
            background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .quick-demo h3 {
            margin-bottom: 15px;
            color: #2d3436;
        }
        
        .demo-btn {
            background: #2d3436;
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 1.1em;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            transition: transform 0.2s;
        }
        
        .demo-btn:hover {
            transform: scale(1.05);
        }
        
        .cart-icon {
            position: fixed;
            top: 20px;
            right: 20px;
            background: #f093fb;
            color: white;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5em;
            cursor: pointer;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            transition: transform 0.2s;
            z-index: 999;
        }
        
        .cart-icon:hover {
            transform: scale(1.1);
        }
        
        .cart-badge {
            position: absolute;
            top: -5px;
            right: -5px;
            background: #e74c3c;
            color: white;
            width: 25px;
            height: 25px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.7em;
            font-weight: bold;
        }
        
        .cart-panel {
            position: fixed;
            top: 0;
            right: -400px;
            width: 400px;
            height: 100%;
            background: white;
            box-shadow: -5px 0 15px rgba(0,0,0,0.3);
            transition: right 0.3s;
            z-index: 1001;
            display: flex;
            flex-direction: column;
        }
        
        .cart-panel.open {
            right: 0;
        }
        
        .cart-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .cart-body {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }
        
        .cart-item {
            display: flex;
            gap: 15px;
            padding: 15px;
            border-bottom: 1px solid #eee;
            align-items: center;
        }
        
        .cart-item-image {
            width: 60px;
            height: 60px;
        }
        
        .cart-item-info {
            flex: 1;
        }
        
        .cart-item-name {
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .cart-item-price {
            color: #27ae60;
        }
        
        .cart-item-remove {
            background: #e74c3c;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 5px;
            cursor: pointer;
        }
        
        .cart-footer {
            padding: 20px;
            border-top: 2px solid #eee;
            background: #f8f9fa;
        }
        
        .cart-total {
            font-size: 1.5em;
            font-weight: bold;
            margin-bottom: 15px;
            text-align: right;
        }
        
        .checkout-btn {
            width: 100%;
            background: linear-gradient(135deg, #27ae60 0%, #229954 100%);
            color: white;
            border: none;
            padding: 15px;
            font-size: 1.1em;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            transition: transform 0.2s;
        }
        
        .checkout-btn:hover {
            transform: translateY(-2px);
        }
        
        .checkout-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        
        .clear-cart-btn {
            width: 100%;
            background: #e74c3c;
            color: white;
            border: none;
            padding: 10px;
            font-size: 0.9em;
            border-radius: 8px;
            cursor: pointer;
            margin-top: 10px;
        }
        
        .cart-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
        }
        
        .cart-overlay.show {
            display: block;
        }
        
        .add-to-cart-btn {
            width: 100%;
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            color: white;
            border: none;
            padding: 12px;
            border-radius: 8px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
            margin-bottom: 8px;
        }
        
        .add-to-cart-btn:hover {
            transform: scale(1.05);
        }
        
        .add-to-cart-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
    </style>
</head>
<body>
    <!-- Cart Icon -->
    <div class="cart-icon" onclick="toggleCart()">
        🛒
        <span class="cart-badge" id="cartBadge">0</span>
    </div>
    
    <!-- Cart Overlay -->
    <div class="cart-overlay" id="cartOverlay" onclick="toggleCart()"></div>
    
    <!-- Cart Panel -->
    <div class="cart-panel" id="cartPanel">
        <div class="cart-header">
            <h2>🛒 Mi Carrito</h2>
            <button class="close-btn" onclick="toggleCart()">&times;</button>
        </div>
        <div class="cart-body" id="cartBody">
            <p style="text-align: center; color: #999; margin-top: 50px;">Carrito vacío</p>
        </div>
        <div class="cart-footer">
            <div class="cart-total">
                Total: <span id="cartTotal">$0</span> USD
            </div>
            <button class="checkout-btn" id="checkoutBtn" onclick="checkoutCart()" disabled>
                💳 Procesar Compra AP2
            </button>
            <button class="clear-cart-btn" onclick="clearCart()">
                🗑️ Vaciar Carrito
            </button>
        </div>
    </div>
    
    <div class="container">
        <div class="header">
            <h1>🛍️ Pokemon Shopping Agent</h1>
            <p>Protocolo AP2 - Agent Payments Protocol</p>
        </div>
        
        <div class="main-content">
            <div class="quick-demo">
                <h3>⚡ Demo Rápido</h3>
                <button class="demo-btn" onclick="quickPurchasePikachu()">
                    Comprar Pikachu (Demo AP2 Completo)
                </button>
            </div>
            
            <div class="search-section">
                <div class="search-title">
                    🔍 Buscar Pokemon
                </div>
                
                <form class="search-form" onsubmit="searchPokemon(event)">
                    <div class="form-group">
                        <label>Nombre o Número</label>
                        <input type="text" id="query" placeholder="ej: pikachu, 25">
                    </div>
                    
                    <div class="form-group">
                        <label>Tipo</label>
                        <select id="type">
                            <option value="">Todos los tipos</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Precio Mínimo (USD)</label>
                        <input type="number" id="minPrice" placeholder="0">
                    </div>
                    
                    <div class="form-group">
                        <label>Precio Máximo (USD)</label>
                        <input type="number" id="maxPrice" placeholder="999">
                    </div>
                    
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="onlyAvailable" checked>
                            Solo disponibles
                        </label>
                    </div>
                    
                    <div class="form-group">
                        <label>Límite de resultados</label>
                        <input type="number" id="limit" value="20" min="1" max="151">
                    </div>
                    
                    <div class="form-group full-width">
                        <button type="submit" class="search-btn">
                            🔍 Buscar Pokemon
                        </button>
                    </div>
                </form>
            </div>
            
            <div id="message"></div>
            
            <div class="results-section">
                <div id="results" class="results-grid"></div>
            </div>
        </div>
    </div>
    
    <div id="purchaseModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 class="modal-title">📋 Resultado de la Compra</h2>
                <button class="close-btn" onclick="closeModal()">&times;</button>
            </div>
            <div id="modalBody"></div>
        </div>
    </div>
    
    <script>
        const typeColors = {
            normal: '#A8A878', fighting: '#C03028', flying: '#A890F0',
            poison: '#A040A0', ground: '#E0C068', rock: '#B8A038',
            bug: '#A8B820', ghost: '#705898', steel: '#B8B8D0',
            fire: '#F08030', water: '#6890F0', grass: '#78C850',
            electric: '#F8D030', psychic: '#F85888', ice: '#98D8D8',
            dragon: '#7038F8', dark: '#705848', fairy: '#EE99AC'
        };
        
        async function loadTypes() {
            try {
                const response = await fetch('/api/types');
                const types = await response.json();
                const select = document.getElementById('type');
                types.forEach(type => {
                    const option = document.createElement('option');
                    option.value = type;
                    option.textContent = type.charAt(0).toUpperCase() + type.slice(1);
                    select.appendChild(option);
                });
            } catch (error) {
                console.error('Error loading types:', error);
            }
        }
        
        async function searchPokemon(event) {
            event.preventDefault();
            
            const query = document.getElementById('query').value;
            const type = document.getElementById('type').value;
            const minPrice = document.getElementById('minPrice').value;
            const maxPrice = document.getElementById('maxPrice').value;
            const onlyAvailable = document.getElementById('onlyAvailable').checked;
            const limit = document.getElementById('limit').value;
            
            showLoading();
            
            const params = new URLSearchParams();
            if (query) params.append('query', query);
            if (type) params.append('type', type);
            if (minPrice) params.append('min_price', minPrice);
            if (maxPrice) params.append('max_price', maxPrice);
            params.append('only_available', onlyAvailable);
            params.append('limit', limit);
            
            try {
                const response = await fetch(`/api/search?${params}`);
                const data = await response.json();
                
                if (!response.ok) {
                    showError(data.detail || 'Error al buscar Pokemon');
                    return;
                }
                
                displayResults(data);
            } catch (error) {
                showError('Error de conexión: ' + error.message);
            }
        }
        
        function displayResults(pokemon) {
            const resultsDiv = document.getElementById('results');
            const messageDiv = document.getElementById('message');
            
            messageDiv.innerHTML = '';
            
            if (pokemon.length === 0) {
                resultsDiv.innerHTML = '<div class="loading">No se encontraron Pokemon con esos criterios</div>';
                return;
            }
            
            resultsDiv.innerHTML = pokemon.map(p => {
                const types = p.types.map(t => 
                    `<span class="type-badge" style="background: ${typeColors[t] || '#777'}">${t}</span>`
                ).join('');
                
                const available = p.stock > 0;
                const stockClass = available ? 'stock-available' : 'stock-unavailable';
                const stockText = available ? `${p.stock} disponibles` : 'Agotado';
                
                return `
                    <div class="pokemon-card">
                        <img class="pokemon-image" src="${p.sprite}" alt="${p.name}">
                        <div class="pokemon-name">${p.name}</div>
                        <div class="pokemon-number">#${String(p.number).padStart(3, '0')}</div>
                        <div class="pokemon-types">${types}</div>
                        <div class="pokemon-price">$${p.price} USD</div>
                        <div class="pokemon-stock">
                            <span class="${stockClass}">${stockText}</span>
                        </div>
                        <button class="add-to-cart-btn" ${!available ? 'disabled' : ''} 
                                onclick="addToCart('${p.number}', '${p.name}')">
                            ${available ? '🛒 Añadir al Carrito' : 'No disponible'}
                        </button>
                        <button class="buy-btn" ${!available ? 'disabled' : ''} 
                                onclick="purchasePokemon('${p.number}', '${p.name}')">
                            ${available ? '⚡ Comprar Ahora' : 'No disponible'}
                        </button>
                    </div>
                `;
            }).join('');
        }
        
        async function purchasePokemon(pokemonId, pokemonName) {
            if (!confirm(`¿Confirmas la compra de ${pokemonName}?`)) {
                return;
            }
            
            showLoading('Procesando compra AP2...');
            
            try {
                const response = await fetch('/api/purchase', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        pokemon_id: pokemonId,
                        quantity: 1
                    })
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    showError(data.detail || 'Error al procesar la compra');
                    return;
                }
                
                showPurchaseResult(data);
            } catch (error) {
                showError('Error de conexión: ' + error.message);
            }
        }
        
        async function quickPurchasePikachu() {
            showLoading('Ejecutando demo de compra AP2...');
            
            try {
                const response = await fetch('/api/quick-demo');
                const data = await response.json();
                
                if (!response.ok) {
                    showError(data.detail || 'Error en el demo');
                    return;
                }
                
                showPurchaseResult(data);
            } catch (error) {
                showError('Error de conexión: ' + error.message);
            }
        }
        
        function showPurchaseResult(data) {
            const modalBody = document.getElementById('modalBody');
            
            let html = '<div class="success">✅ Compra completada exitosamente</div>';
            
            html += '<h3>📦 Productos</h3>';
            html += '<ul>';
            data.items.forEach(item => {
                html += `<li><strong>${item.name}</strong> - $${item.price} USD x ${item.quantity}</li>`;
            });
            html += '</ul>';
            
            html += `<h3>💰 Total: $${data.total} USD</h3>`;
            html += `<p><strong>ID de Transacción:</strong> ${data.payment_id}</p>`;
            html += `<p><strong>Estado:</strong> <span style="color: green">${data.status}</span></p>`;
            
            if (data.cart_mandate) {
                html += '<h3>🛒 CartMandate (AP2)</h3>';
                html += `<pre>${JSON.stringify(data.cart_mandate, null, 2)}</pre>`;
            }
            
            if (data.payment_mandate) {
                html += '<h3>💳 PaymentMandate (AP2)</h3>';
                html += `<pre>${JSON.stringify(data.payment_mandate, null, 2)}</pre>`;
            }
            
            modalBody.innerHTML = html;
            document.getElementById('purchaseModal').classList.add('show');
            
            // Clear loading
            document.getElementById('message').innerHTML = '';
        }
        
        function closeModal() {
            document.getElementById('purchaseModal').classList.remove('show');
        }
        
        function showLoading(message = 'Buscando...') {
            document.getElementById('message').innerHTML = 
                `<div class="loading">${message}</div>`;
            document.getElementById('results').innerHTML = '';
        }
        
        function showError(message) {
            document.getElementById('message').innerHTML = 
                `<div class="error">❌ ${message}</div>`;
            document.getElementById('results').innerHTML = '';
        }
        
        // Cart functions
        async function addToCart(pokemonId, pokemonName) {
            try {
                const response = await fetch('/api/cart/add', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        pokemon_id: pokemonId,
                        quantity: 1
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    updateCartDisplay();
                    showSuccess(`✅ ${pokemonName} añadido al carrito`);
                } else {
                    showError(data.detail || 'Error al añadir al carrito');
                }
            } catch (error) {
                showError('Error de conexión: ' + error.message);
            }
        }
        
        function toggleCart() {
            const panel = document.getElementById('cartPanel');
            const overlay = document.getElementById('cartOverlay');
            panel.classList.toggle('open');
            overlay.classList.toggle('show');
        }
        
        async function updateCartDisplay() {
            try {
                const response = await fetch('/api/cart');
                const data = await response.json();
                
                document.getElementById('cartBadge').textContent = data.item_count;
                document.getElementById('cartTotal').textContent = `$${data.total}`;
                
                const cartBody = document.getElementById('cartBody');
                const checkoutBtn = document.getElementById('checkoutBtn');
                
                if (data.items.length === 0) {
                    cartBody.innerHTML = '<p style="text-align: center; color: #999; margin-top: 50px;">Carrito vacío</p>';
                    checkoutBtn.disabled = true;
                } else {
                    cartBody.innerHTML = data.items.map(item => `
                        <div class="cart-item">
                            <img class="cart-item-image" src="${item.sprite}" alt="${item.name}">
                            <div class="cart-item-info">
                                <div class="cart-item-name">${item.name}</div>
                                <div class="cart-item-price">$${item.price} x ${item.quantity} = $${item.price * item.quantity}</div>
                            </div>
                            <button class="cart-item-remove" onclick="removeFromCart('${item.product_id}')">
                                🗑️
                            </button>
                        </div>
                    `).join('');
                    checkoutBtn.disabled = false;
                }
            } catch (error) {
                console.error('Error updating cart:', error);
            }
        }
        
        async function removeFromCart(productId) {
            try {
                const response = await fetch(`/api/cart/item/${productId}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    updateCartDisplay();
                }
            } catch (error) {
                console.error('Error removing item:', error);
            }
        }
        
        async function clearCart() {
            if (!confirm('¿Estás seguro de vaciar el carrito?')) {
                return;
            }
            
            try {
                const response = await fetch('/api/cart/clear', {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    updateCartDisplay();
                }
            } catch (error) {
                console.error('Error clearing cart:', error);
            }
        }
        
        async function checkoutCart() {
            if (!confirm('¿Proceder con la compra usando AP2?')) {
                return;
            }
            
            toggleCart();
            showLoading('Procesando compra AP2...');
            
            try {
                const response = await fetch('/api/cart/checkout', {
                    method: 'POST'
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    showError(data.detail || 'Error al procesar la compra');
                    return;
                }
                
                showPurchaseResult(data);
                updateCartDisplay();
            } catch (error) {
                showError('Error de conexión: ' + error.message);
            }
        }
        
        function showSuccess(message) {
            const messageDiv = document.getElementById('message');
            messageDiv.innerHTML = `<div class="success">${message}</div>`;
            setTimeout(() => {
                messageDiv.innerHTML = '';
            }, 3000);
        }
        
        // Initialize
        loadTypes();
        updateCartDisplay();
        
        // Load all Pokemon on startup
        window.addEventListener('load', () => {
            searchPokemon(new Event('submit'));
        });
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


@app.get("/api/types")
async def get_types():
    """Get all Pokemon types"""
    try:
        async with agent.get_mcp_client() as mcp:
            result = await mcp.list_pokemon_types()
        return result
    except Exception as e:
        import traceback
        print(f"Error in get_types: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/search")
async def search_pokemon(
    query: Optional[str] = None,
    type: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    only_available: bool = True,
    limit: int = 20
):
    """Search Pokemon"""
    try:
        # If query is provided, search for exact Pokemon first
        if query:
            async with agent.get_mcp_client() as mcp:
                try:
                    # Try to get exact Pokemon by name or number
                    pokemon_info = await mcp.get_pokemon_info(query)
                    price_info = await mcp.get_pokemon_price(query)
                    
                    # Return single Pokemon if found
                    formatted = [{
                        'number': price_info.get('numero'),
                        'name': pokemon_info.get('name'),
                        'price': price_info.get('precio'),
                        'stock': price_info.get('inventario', {}).get('disponibles', 0),
                        'types': pokemon_info.get('types', []),
                        'sprite': pokemon_info.get('sprites', {}).get('front_default', '')
                    }]
                    return formatted
                except:
                    # If exact match fails, fall through to general search
                    pass
        
        # General search with filters
        filters = {}
        if type:
            filters['type'] = type
        if min_price is not None:
            filters['min_price'] = min_price
        if max_price is not None:
            filters['max_price'] = max_price
        filters['only_available'] = only_available
        filters['limit'] = limit
        
        async with agent.get_mcp_client() as mcp:
            response = await mcp.search_pokemon(**filters)
        
        # Extract results from the response structure
        if isinstance(response, dict) and 'results' in response:
            results = response['results']
        else:
            results = response if isinstance(response, list) else []
        
        # Format results and fetch sprites
        formatted = []
        async with agent.get_mcp_client() as mcp:
            for p in results:
                pokemon_id = p.get('numero') or p.get('id')
                pokemon_name = p.get('nombre') or p.get('name')
                
                # Get sprite from PokeAPI
                sprite = ''
                if pokemon_id:
                    try:
                        pokemon_info = await mcp.get_pokemon_info(str(pokemon_id))
                        sprite = pokemon_info.get('sprites', {}).get('front_default', '')
                    except:
                        # If PokeAPI fails, use placeholder
                        sprite = f'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{pokemon_id}.png'
                
                formatted.append({
                    'number': pokemon_id,
                    'name': pokemon_name,
                    'price': p.get('precio') or p.get('price', 0),
                    'stock': p.get('inventario', {}).get('disponibles', 0) if 'inventario' in p else p.get('stock', 0),
                    'types': p.get('types', []),
                    'sprite': sprite
                })
        
        return formatted
    except Exception as e:
        import traceback
        print(f"Error in search_pokemon: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/cart/add")
async def add_to_cart(request: PurchaseRequest):
    """Add Pokemon to cart"""
    try:
        # Get Pokemon info
        async with agent.get_mcp_client() as mcp:
            pokemon_info = await mcp.get_pokemon_info(request.pokemon_id)
            price_info = await mcp.get_pokemon_price(request.pokemon_id)
        
        # Check if already in cart
        existing = None
        for item in shopping_cart:
            if item['product_id'] == str(price_info['numero']):
                existing = item
                break
        
        if existing:
            existing['quantity'] += request.quantity
        else:
            shopping_cart.append({
                'product_id': str(price_info['numero']),
                'name': pokemon_info['name'].capitalize(),
                'price': price_info['precio'],
                'quantity': request.quantity,
                'sprite': pokemon_info.get('sprites', {}).get('front_default', '')
            })
        
        return {
            "status": "success",
            "message": f"Added {pokemon_info['name'].capitalize()} to cart",
            "cart_items": len(shopping_cart),
            "cart": shopping_cart
        }
    except Exception as e:
        import traceback
        print(f"Error in add_to_cart: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/cart")
async def get_cart():
    """Get current shopping cart"""
    total = sum(item['price'] * item['quantity'] for item in shopping_cart)
    return {
        "items": shopping_cart,
        "total": total,
        "item_count": len(shopping_cart)
    }


@app.delete("/api/cart/clear")
async def clear_cart():
    """Clear shopping cart"""
    global shopping_cart
    shopping_cart = []
    return {"status": "success", "message": "Cart cleared"}


@app.delete("/api/cart/item/{product_id}")
async def remove_from_cart(product_id: str):
    """Remove item from cart"""
    global shopping_cart
    shopping_cart = [item for item in shopping_cart if item['product_id'] != product_id]
    return {"status": "success", "cart": shopping_cart}


@app.post("/api/cart/checkout")
async def checkout_cart():
    """Checkout current cart using AP2 protocol"""
    try:
        if not shopping_cart:
            raise HTTPException(status_code=400, detail="Cart is empty")
        
        # Convert cart to items format
        items = [
            {"product_id": item['product_id'], "quantity": item['quantity']}
            for item in shopping_cart
        ]
        
        # Create cart mandate
        cart_mandate = await agent.create_cart(items)
        
        # Get payment methods
        payment_methods = await agent.get_payment_methods()
        default_method = next(
            (m for m in payment_methods if m["is_default"]),
            payment_methods[0]
        )
        
        # Tokenize payment method
        payment_token = await agent.tokenize_payment_method(default_method["id"])
        
        # Create payment mandate
        payment_mandate = agent.create_payment_mandate(
            cart_mandate=cart_mandate,
            payment_token=payment_token,
            payment_method_name=default_method["type"],
            user_email="trainer@pokemon.com"
        )
        
        # Process payment
        receipt = await agent.process_payment(cart_mandate, payment_mandate)
        
        # Clear cart after successful purchase
        total = sum(item['price'] * item['quantity'] for item in shopping_cart)
        purchased_items = shopping_cart.copy()
        shopping_cart.clear()
        
        return {
            "status": receipt.get("status", "completed"),
            "payment_id": receipt.get("payment_id"),
            "total": total,
            "items": purchased_items,
            "cart_mandate": cart_mandate,
            "payment_mandate": payment_mandate,
            "receipt": receipt
        }
    except Exception as e:
        import traceback
        print(f"Error in checkout_cart: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/purchase")
async def purchase_pokemon(request: PurchaseRequest):
    """Purchase a Pokemon using AP2 protocol"""
    try:
        result = await agent.purchase_pokemon(
            pokemon_id=request.pokemon_id,
            quantity=request.quantity
        )
        return result
    except Exception as e:
        import traceback
        print(f"Error in purchase_pokemon: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/quick-demo")
async def quick_demo():
    """Quick Pikachu purchase demo"""
    try:
        result = await agent.purchase_pokemon(pokemon_id="25", quantity=1)
        return result
    except Exception as e:
        import traceback
        print(f"Error in quick_demo: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "message": "Pokemon Shopping Agent is running"}


def main():
    """Run the web UI server"""
    print("=" * 60)
    print("🛍️  Pokemon Shopping Agent - Web UI")
    print("=" * 60)
    print()
    print("🌐 Abriendo interfaz web en: http://localhost:8000")
    print("📋 API docs disponibles en: http://localhost:8000/docs")
    print()
    print("Presiona Ctrl+C para detener el servidor")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()

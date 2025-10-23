"""
Shopping Agent Web UI - Interactive interface for Pokemon purchases with AP2
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parents[3]))

from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import uvicorn

from ap2.agents.shopping.agent import ShoppingAgent
from database import SessionLocal, PokemonRepository, CartRepository, Pokemon

app = FastAPI(title="Pokemon Shopping Agent", version="1.0.0")
agent = ShoppingAgent()


# Session management helpers (TODO: move to separate module)
def get_or_create_session_id(request: Request, response: Response) -> str:
    """Get or create a session ID from cookies"""
    session_id = request.cookies.get("session_id")
    if not session_id:
        import uuid
        session_id = str(uuid.uuid4())
        response.set_cookie(key="session_id", value=session_id, httponly=True)
    return session_id


def get_session_id(request: Request) -> str:
    """Get session ID from cookies"""
    session_id = request.cookies.get("session_id")
    if not session_id:
        import uuid
        session_id = str(uuid.uuid4())
    return session_id


# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
async def add_to_cart(
    request_data: PurchaseRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Add Pokemon to cart (with database persistence)"""
    try:
        # Get or create session
        session_id = get_or_create_session_id(request, response)
        
        # Get repositories
        cart_repo = CartRepository(db)
        pokemon_repo = PokemonRepository(db)
        
        # Get or create cart for this session
        cart = cart_repo.get_or_create_cart(session_id)
        
        # Get Pokemon from database
        pokemon = pokemon_repo.get_by_numero(int(request_data.pokemon_id))
        if not pokemon:
            raise HTTPException(status_code=404, detail=f"Pokemon {request_data.pokemon_id} not found")
        
        # Check availability
        if not pokemon.en_venta:
            raise HTTPException(status_code=400, detail=f"{pokemon.nombre} is not for sale")
        if pokemon.inventario_disponible < request_data.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {pokemon.nombre}")
        
        # Add to cart
        cart_item = cart_repo.add_item(cart, pokemon, request_data.quantity)
        
        # Get Pokemon info for response (with sprite)
        async with agent.get_mcp_client() as mcp:
            pokemon_info = await mcp.get_pokemon_info(request_data.pokemon_id)
        
        return {
            "status": "success",
            "message": f"Added {pokemon.nombre.capitalize()} to cart",
            "cart_items": len(cart.items),
            "cart": cart.to_dict(),
            "sprite": pokemon_info.get('sprites', {}).get('front_default', '')
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in add_to_cart: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/cart")
async def get_cart(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Get current shopping cart from database"""
    try:
        session_id = get_or_create_session_id(request, response)
        cart_repo = CartRepository(db)
        
        cart = cart_repo.get_or_create_cart(session_id)
        cart_dict = cart.to_dict()
        
        # Get sprite URLs for items
        items_with_sprites = []
        async with agent.get_mcp_client() as mcp:
            for item in cart_dict['items']:
                pokemon_info = await mcp.get_pokemon_info(str(item['pokemon_numero']))
                items_with_sprites.append({
                    **item,
                    'sprite': pokemon_info.get('sprites', {}).get('front_default', ''),
                    'product_id': str(item['pokemon_numero']),
                    'name': item['pokemon_name'].capitalize(),
                    'price': item['unit_price']
                })
        
        return {
            "items": items_with_sprites,
            "total": cart_dict['total_amount'],
            "item_count": cart_dict['total_items'],
            "session_id": cart.session_id,
            "expires_at": cart_dict['expires_at']
        }
    except Exception as e:
        import traceback
        print(f"Error in get_cart: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/cart/clear")
async def clear_cart(
    request: Request,
    db: Session = Depends(get_db)
):
    """Clear shopping cart"""
    try:
        session_id = get_session_id(request)
        if not session_id:
            return {"status": "success", "message": "No cart to clear"}
        
        cart_repo = CartRepository(db)
        cart = cart_repo.get_cart_by_session(session_id)
        
        if cart:
            cart_repo.clear_cart(cart.id)
        
        return {"status": "success", "message": "Cart cleared"}
    except Exception as e:
        import traceback
        print(f"Error in clear_cart: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/cart/item/{product_id}")
async def remove_from_cart(
    product_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Remove item from cart"""
    try:
        session_id = get_session_id(request)
        if not session_id:
            raise HTTPException(status_code=400, detail="No active cart session")
        
        cart_repo = CartRepository(db)
        cart = cart_repo.get_cart_by_session(session_id)
        
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        
        # Find and remove item
        item_found = False
        for item in cart.items:
            if str(item.pokemon_numero) == product_id:
                cart_repo.remove_item(item.id)
                item_found = True
                break
        
        if not item_found:
            raise HTTPException(status_code=404, detail=f"Item {product_id} not in cart")
        
        # Get updated cart
        updated_cart = cart_repo.get_cart_by_session(session_id)
        return {
            "status": "success",
            "cart": updated_cart.to_dict() if updated_cart else {"items": [], "total_amount": 0}
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in remove_from_cart: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/cart/checkout")
async def checkout_cart(
    request: Request,
    db: Session = Depends(get_db)
):
    """Checkout current cart using AP2 protocol"""
    try:
        session_id = get_session_id(request)
        if not session_id:
            raise HTTPException(status_code=400, detail="No active cart session")
        
        cart_repo = CartRepository(db)
        cart = cart_repo.get_cart_by_session(session_id)
        
        if not cart or len(cart.items) == 0:
            raise HTTPException(status_code=400, detail="Cart is empty")
        
        # Mark cart as checkout
        cart_repo.mark_cart_as_checkout(cart.id)
        
        # Convert cart to items format for AP2
        items = [
            {"product_id": str(item.pokemon_numero), "quantity": item.quantity}
            for item in cart.items
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
        
        # Get cart info before clearing
        cart_dict = cart.to_dict()
        total = cart_dict['total_amount']
        purchased_items = cart_dict['items']
        
        # Mark cart as completed after successful purchase
        cart_repo.mark_cart_as_completed(cart.id)
        
        return {
            "status": receipt.get("status", "completed"),
            "payment_id": receipt.get("payment_id"),
            "total": total,
            "items": purchased_items,
            "cart_mandate": cart_mandate,
            "payment_mandate": payment_mandate,
            "receipt": receipt
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in checkout_cart: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
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


# Background task for cart expiration
import threading
import time

def cart_cleanup_worker():
    """Background worker to expire old carts"""
    while True:
        try:
            time.sleep(3600)  # Run every hour
            db = SessionLocal()
            try:
                cart_repo = CartRepository(db)
                expired_count = cart_repo.expire_old_carts(hours=24)
                if expired_count > 0:
                    print(f"🗑️  Expired {expired_count} old carts")
            finally:
                db.close()
        except Exception as e:
            print(f"Error in cart cleanup: {e}")


def start_cleanup_worker():
    """Start background cleanup worker"""
    worker_thread = threading.Thread(target=cart_cleanup_worker, daemon=True)
    worker_thread.start()
    print("🧹 Cart cleanup worker started (runs every hour)")


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
    
    # Start background cleanup worker
    start_cleanup_worker()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()

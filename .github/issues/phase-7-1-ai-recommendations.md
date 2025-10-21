---
title: "[Phase 7.1] AI-Powered Recommendations & Smart Search"
labels: enhancement, ai, ml, phase-7
assignees: CERVIII
---

## 📋 Descripción

Sistema de recomendaciones con AI: personalized suggestions basadas en historial, collaborative filtering, chatbot conversacional, y búsqueda semántica con NLP.

## 🎯 Tipo de Issue

- [x] 🤖 AI/ML
- [x] ✨ Nueva feature
- [x] 🔍 Search

## 📦 Fase del Roadmap

**Fase 7.1: Recomendaciones con IA**

## ✅ Tareas

### Recommendation Engine

#### Collaborative Filtering
```python
# ap2-integration/src/recommendations/engine.py

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict

class RecommendationEngine:
    def __init__(self, db: Session):
        self.db = db
        self.user_item_matrix = None
        self.item_similarity_matrix = None
    
    def build_user_item_matrix(self):
        """Build user-item interaction matrix"""
        # Get all transactions
        transactions = self.db.query(Transaction).all()
        
        # Get unique users and products
        users = set()
        products = set()
        interactions = []
        
        for tx in transactions:
            users.add(tx.user_id)
            for item in tx.items:
                products.add(item.pokemon_numero)
                interactions.append({
                    'user_id': tx.user_id,
                    'product_id': item.pokemon_numero,
                    'quantity': item.quantity
                })
        
        # Create matrix
        user_list = sorted(users)
        product_list = sorted(products)
        
        matrix = np.zeros((len(user_list), len(product_list)))
        
        user_idx = {u: i for i, u in enumerate(user_list)}
        product_idx = {p: i for i, p in enumerate(product_list)}
        
        for interaction in interactions:
            u = user_idx[interaction['user_id']]
            p = product_idx[interaction['product_id']]
            matrix[u, p] += interaction['quantity']
        
        self.user_item_matrix = matrix
        self.user_list = user_list
        self.product_list = product_list
        
        return matrix
    
    def build_item_similarity(self):
        """Calculate item-item similarity"""
        if self.user_item_matrix is None:
            self.build_user_item_matrix()
        
        # Transpose to get item-user matrix
        item_user_matrix = self.user_item_matrix.T
        
        # Calculate cosine similarity
        self.item_similarity_matrix = cosine_similarity(item_user_matrix)
        
        return self.item_similarity_matrix
    
    def recommend_for_user(
        self,
        user_id: int,
        n: int = 10,
        exclude_purchased: bool = True
    ) -> List[Dict]:
        """Get personalized recommendations for user"""
        
        if self.item_similarity_matrix is None:
            self.build_item_similarity()
        
        # Get user's purchase history
        user_transactions = self.db.query(Transaction).filter_by(user_id=user_id).all()
        purchased_products = set()
        
        for tx in user_transactions:
            for item in tx.items:
                purchased_products.add(item.pokemon_numero)
        
        # Calculate recommendation scores
        scores = {}
        
        for product_id in purchased_products:
            if product_id not in self.product_list:
                continue
            
            product_idx = self.product_list.index(product_id)
            
            # Get similar products
            similarities = self.item_similarity_matrix[product_idx]
            
            for i, similarity in enumerate(similarities):
                similar_product = self.product_list[i]
                
                # Skip if already purchased
                if exclude_purchased and similar_product in purchased_products:
                    continue
                
                # Skip self
                if similar_product == product_id:
                    continue
                
                # Accumulate score
                if similar_product not in scores:
                    scores[similar_product] = 0
                scores[similar_product] += similarity
        
        # Sort by score
        sorted_products = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:n]
        
        # Fetch product details
        recommendations = []
        for product_id, score in sorted_products:
            pokemon = get_pokemon_by_numero(product_id)
            recommendations.append({
                'product_id': product_id,
                'name': pokemon['nombre'],
                'price': pokemon['precio'],
                'score': float(score),
                'reason': f"Based on your purchase of similar Pokemon"
            })
        
        return recommendations
    
    def get_trending_products(self, days: int = 7, limit: int = 10) -> List[Dict]:
        """Get trending products based on recent sales"""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Query recent transactions
        result = self.db.query(
            TransactionItem.pokemon_numero,
            func.sum(TransactionItem.quantity).label('total_sold')
        ).join(Transaction).filter(
            Transaction.created_at >= cutoff
        ).group_by(
            TransactionItem.pokemon_numero
        ).order_by(
            func.sum(TransactionItem.quantity).desc()
        ).limit(limit).all()
        
        trending = []
        for product_id, total_sold in result:
            pokemon = get_pokemon_by_numero(product_id)
            trending.append({
                'product_id': product_id,
                'name': pokemon['nombre'],
                'price': pokemon['precio'],
                'total_sold': int(total_sold),
                'reason': f"🔥 {total_sold} sold this week!"
            })
        
        return trending
    
    def recommend_bundle(self, user_id: int) -> List[Dict]:
        """Recommend product bundles (frequently bought together)"""
        # Get user's cart
        cart = self.db.query(Cart).filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        if not cart or not cart.items:
            return []
        
        # Get products in cart
        cart_products = [item.pokemon_numero for item in cart.items]
        
        # Find products frequently bought with these
        # Query transactions containing any cart product
        related_transactions = self.db.query(Transaction).join(TransactionItem).filter(
            TransactionItem.pokemon_numero.in_(cart_products)
        ).all()
        
        # Count co-occurrences
        co_occurrence = {}
        for tx in related_transactions:
            tx_products = [item.pokemon_numero for item in tx.items]
            for product in tx_products:
                if product not in cart_products:
                    co_occurrence[product] = co_occurrence.get(product, 0) + 1
        
        # Sort by frequency
        sorted_products = sorted(
            co_occurrence.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        recommendations = []
        for product_id, count in sorted_products:
            pokemon = get_pokemon_by_numero(product_id)
            recommendations.append({
                'product_id': product_id,
                'name': pokemon['nombre'],
                'price': pokemon['precio'],
                'reason': f"Frequently bought with {cart.items[0].pokemon_name}"
            })
        
        return recommendations
```

### Semantic Search with Embeddings

```python
# ap2-integration/src/search/semantic_search.py

from sentence_transformers import SentenceTransformer
import numpy as np
import pickle

class SemanticSearch:
    def __init__(self):
        # Load pre-trained model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.product_embeddings = None
        self.product_index = None
    
    def build_index(self, products: List[Dict]):
        """Build embeddings for all products"""
        # Create text descriptions
        descriptions = []
        product_ids = []
        
        for product in products:
            # Combine name + type + description
            text = f"{product['nombre']} {' '.join(product.get('types', []))} {product.get('description', '')}"
            descriptions.append(text)
            product_ids.append(product['numero'])
        
        # Generate embeddings
        self.product_embeddings = self.model.encode(descriptions)
        self.product_index = product_ids
        
        # Save to disk
        with open('product_embeddings.pkl', 'wb') as f:
            pickle.dump({
                'embeddings': self.product_embeddings,
                'index': self.product_index
            }, f)
    
    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """Search products using semantic similarity"""
        if self.product_embeddings is None:
            self.load_index()
        
        # Encode query
        query_embedding = self.model.encode([query])[0]
        
        # Calculate cosine similarity
        similarities = np.dot(self.product_embeddings, query_embedding) / (
            np.linalg.norm(self.product_embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Get top-k results
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            product_id = self.product_index[idx]
            pokemon = get_pokemon_by_numero(product_id)
            results.append({
                'product_id': product_id,
                'name': pokemon['nombre'],
                'price': pokemon['precio'],
                'similarity': float(similarities[idx])
            })
        
        return results
    
    def load_index(self):
        """Load pre-built embeddings"""
        with open('product_embeddings.pkl', 'rb') as f:
            data = pickle.load(f)
            self.product_embeddings = data['embeddings']
            self.product_index = data['index']

# API endpoint
@app.get("/api/search/semantic")
async def semantic_search(q: str, limit: int = 10):
    """Natural language search"""
    searcher = SemanticSearch()
    results = searcher.search(q, top_k=limit)
    return results
```

### Conversational Shopping Assistant (Chatbot)

```python
# ap2-integration/src/chatbot/assistant.py

from google import genai
from google.genai.types import Tool, GenerateContentConfig

class ShoppingAssistant:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.conversation_history = []
    
    def chat(self, user_message: str, user_id: int) -> str:
        """Process user message and return AI response"""
        
        # Add to history
        self.conversation_history.append({
            'role': 'user',
            'content': user_message
        })
        
        # Get user context
        context = self._get_user_context(user_id)
        
        # Define tools
        tools = [
            Tool(function_declarations=[
                {
                    'name': 'search_pokemon',
                    'description': 'Search for Pokemon by name, type, or characteristics',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'query': {'type': 'string'},
                            'type': {'type': 'string'},
                            'max_price': {'type': 'number'}
                        }
                    }
                },
                {
                    'name': 'get_recommendations',
                    'description': 'Get personalized recommendations for user',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'user_id': {'type': 'integer'},
                            'limit': {'type': 'integer'}
                        }
                    }
                },
                {
                    'name': 'add_to_cart',
                    'description': 'Add Pokemon to shopping cart',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'pokemon_id': {'type': 'integer'},
                            'quantity': {'type': 'integer'}
                        },
                        'required': ['pokemon_id']
                    }
                }
            ])
        ]
        
        # System prompt
        system_prompt = f"""You are a helpful Pokemon shopping assistant.
        
User context:
- Previous purchases: {context['purchased']}
- Current cart: {context['cart']}
- Budget preferences: ${context.get('budget', 'not set')}

Your role:
- Help users find Pokemon they'll love
- Make personalized recommendations
- Answer questions about products
- Assist with purchases

Be friendly, knowledgeable, and concise."""
        
        # Generate response
        response = self.client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=[
                {'role': 'user', 'parts': [{'text': system_prompt}]},
                *self.conversation_history
            ],
            config=GenerateContentConfig(
                tools=tools,
                temperature=0.7
            )
        )
        
        # Handle function calls
        if response.candidates[0].content.parts[0].function_call:
            function_call = response.candidates[0].content.parts[0].function_call
            function_result = self._execute_function(function_call)
            
            # Send result back to model
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=[
                    *self.conversation_history,
                    {'role': 'model', 'parts': [{'function_call': function_call}]},
                    {'role': 'function', 'parts': [{'function_response': {
                        'name': function_call.name,
                        'response': function_result
                    }}]}
                ]
            )
        
        assistant_message = response.text
        
        # Add to history
        self.conversation_history.append({
            'role': 'assistant',
            'content': assistant_message
        })
        
        return assistant_message
    
    def _get_user_context(self, user_id: int) -> Dict:
        """Get user's shopping context"""
        # Recent purchases
        recent_txs = db.query(Transaction).filter_by(user_id=user_id).order_by(
            Transaction.created_at.desc()
        ).limit(5).all()
        
        purchased = [item.pokemon_name for tx in recent_txs for item in tx.items]
        
        # Current cart
        cart = db.query(Cart).filter_by(user_id=user_id, status='active').first()
        cart_items = [item.pokemon_name for item in cart.items] if cart else []
        
        return {
            'purchased': purchased,
            'cart': cart_items
        }
    
    def _execute_function(self, function_call) -> Dict:
        """Execute function called by AI"""
        name = function_call.name
        args = function_call.args
        
        if name == 'search_pokemon':
            results = search_pokemon(**args)
            return {'results': results}
        
        elif name == 'get_recommendations':
            engine = RecommendationEngine(db)
            recommendations = engine.recommend_for_user(**args)
            return {'recommendations': recommendations}
        
        elif name == 'add_to_cart':
            cart_item = add_item_to_cart(**args)
            return {'success': True, 'item': cart_item}
        
        return {'error': 'Unknown function'}

# WebSocket endpoint for real-time chat
from fastapi import WebSocket

@app.websocket("/ws/chat")
async def chat_websocket(websocket: WebSocket, user_id: int):
    await websocket.accept()
    
    assistant = ShoppingAssistant(GOOGLE_API_KEY)
    
    try:
        while True:
            # Receive message
            message = await websocket.receive_text()
            
            # Generate response
            response = assistant.chat(message, user_id)
            
            # Send response
            await websocket.send_text(response)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()
```

### Frontend UI

#### Recommendation Widgets

```html
<!-- Homepage recommendations -->
<div class="recommendations-section">
  <h3>Recommended for You</h3>
  <div class="pokemon-grid" id="recommendations"></div>
</div>

<script>
async function loadRecommendations() {
    const response = await fetch('/api/recommendations/for-me');
    const recommendations = await response.json();
    
    const grid = document.getElementById('recommendations');
    recommendations.forEach(rec => {
        const card = document.createElement('div');
        card.className = 'pokemon-card';
        card.innerHTML = `
            <img src="${rec.image_url}" alt="${rec.name}" />
            <h4>${rec.name}</h4>
            <p class="price">$${rec.price}</p>
            <p class="reason">${rec.reason}</p>
            <button onclick="addToCart(${rec.product_id})">Add to Cart</button>
        `;
        grid.appendChild(card);
    });
}
</script>

<!-- Chatbot widget -->
<div id="chatbot-widget" class="chatbot-closed">
  <button class="chatbot-toggle" onclick="toggleChatbot()">
    💬 Chat with AI Assistant
  </button>
  
  <div class="chatbot-window">
    <div class="chatbot-header">
      <h4>🤖 Pokemon Shopping Assistant</h4>
      <button onclick="toggleChatbot()">×</button>
    </div>
    
    <div class="chatbot-messages" id="chat-messages">
      <div class="message assistant">
        Hi! I'm your AI shopping assistant. How can I help you find the perfect Pokemon today?
      </div>
    </div>
    
    <div class="chatbot-input">
      <input 
        type="text" 
        id="chat-input" 
        placeholder="Ask me anything..."
        onkeypress="if(event.key==='Enter') sendMessage()"
      />
      <button onclick="sendMessage()">Send</button>
    </div>
  </div>
</div>

<script>
let ws = null;

function toggleChatbot() {
    const widget = document.getElementById('chatbot-widget');
    widget.classList.toggle('chatbot-closed');
    
    if (!widget.classList.contains('chatbot-closed') && !ws) {
        // Connect WebSocket
        ws = new WebSocket('ws://localhost:8001/ws/chat?user_id=1');
        
        ws.onmessage = (event) => {
            addMessage(event.data, 'assistant');
        };
    }
}

function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message to UI
    addMessage(message, 'user');
    
    // Send to server
    ws.send(message);
    
    // Clear input
    input.value = '';
}

function addMessage(text, role) {
    const messagesDiv = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    messageDiv.textContent = text;
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}
</script>

<!-- Semantic search -->
<div class="search-bar advanced">
  <input 
    type="text" 
    id="semantic-search" 
    placeholder="Describe what you're looking for... (e.g., 'cute yellow electric mouse')"
  />
  <button onclick="semanticSearch()">🔍 AI Search</button>
</div>

<script>
async function semanticSearch() {
    const query = document.getElementById('semantic-search').value;
    const response = await fetch(`/api/search/semantic?q=${encodeURIComponent(query)}`);
    const results = await response.json();
    
    displayResults(results);
}
</script>
```

## 📝 Criterios de Aceptación

- [ ] Collaborative filtering recommendations
- [ ] Trending products tracking
- [ ] "Frequently bought together" suggestions
- [ ] Semantic search con NLP
- [ ] Conversational chatbot con function calling
- [ ] WebSocket real-time chat
- [ ] Personalized homepage
- [ ] AI assistant can add to cart

## 🧪 Testing

```python
def test_recommendations():
    engine = RecommendationEngine(db)
    recommendations = engine.recommend_for_user(user_id=1, n=5)
    assert len(recommendations) == 5
    assert all('score' in rec for rec in recommendations)

def test_semantic_search():
    searcher = SemanticSearch()
    results = searcher.search("electric mouse pokemon", top_k=5)
    assert results[0]['name'] == 'Pikachu'  # Should find Pikachu

async def test_chatbot():
    assistant = ShoppingAssistant(API_KEY)
    response = assistant.chat("I want a fire type starter", user_id=1)
    assert 'Charmander' in response or 'fire' in response.lower()
```

## ⏱️ Estimación

**Tiempo:** 3-4 semanas
**Prioridad:** High (UX differentiator)
**Complejidad:** Very High

## 🔗 Issues Relacionados

Relacionado con: #phase-3-3-promotions (personalized promos)
Prerequisito para: #phase-7-3-gamification

## 📚 Recursos

- [Collaborative Filtering](https://realpython.com/build-recommendation-engine-collaborative-filtering/)
- [Sentence Transformers](https://www.sbert.net/)
- [Gemini Function Calling](https://ai.google.dev/gemini-api/docs/function-calling)
- [WebSocket FastAPI](https://fastapi.tiangolo.com/advanced/websockets/)

## 💡 ML Model Training

```bash
# Train recommendation model
python scripts/train_recommendations.py

# Build semantic search index
python scripts/build_search_index.py

# Evaluate model
python scripts/evaluate_recommendations.py
```

## 🚨 Privacy Considerations

- User purchase history used for recommendations
- Opt-out option for personalization
- Anonymous aggregated data for trending
- Chatbot conversations not stored permanently
- GDPR: Right to delete recommendation data

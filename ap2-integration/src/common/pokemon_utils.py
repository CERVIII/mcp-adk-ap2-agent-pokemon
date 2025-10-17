"""
Common utilities for AP2 Pokemon integration
"""

from typing import Any, Dict, List
import json
from pathlib import Path


def load_pokemon_catalog() -> List[Dict[str, Any]]:
    """Load Pokemon catalog from pokemon-gen1.json"""
    catalog_path = Path(__file__).parent.parent.parent.parent / "pokemon-gen1.json"
    
    with open(catalog_path, 'r') as f:
        return json.load(f)


def find_pokemon_by_name(name: str) -> Dict[str, Any] | None:
    """Find a Pokemon by name in the catalog"""
    catalog = load_pokemon_catalog()
    
    for pokemon in catalog:
        if pokemon['nombre'].lower() == name.lower():
            return pokemon
    
    return None


def find_pokemon_by_number(number: int) -> Dict[str, Any] | None:
    """Find a Pokemon by number in the catalog"""
    catalog = load_pokemon_catalog()
    
    for pokemon in catalog:
        if pokemon['numero'] == number:
            return pokemon
    
    return None


def search_pokemon(
    type_filter: str | None = None,
    max_price: float | None = None,
    min_price: float | None = None,
    only_available: bool = False,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Search Pokemon with filters
    
    Note: type_filter requires PokeAPI integration
    For now, we'll filter only by price and availability
    """
    catalog = load_pokemon_catalog()
    results = []
    
    for pokemon in catalog:
        # Check availability
        if only_available and not pokemon.get('enVenta', False):
            continue
        
        # Check price range
        price = pokemon.get('precio', 0)
        if max_price and price > max_price:
            continue
        if min_price and price < min_price:
            continue
        
        results.append(pokemon)
        
        if len(results) >= limit:
            break
    
    return results


def format_price(price: float) -> str:
    """Format price in USD"""
    return f"${price:.2f} USD"


def create_cart_item(pokemon: Dict[str, Any], quantity: int = 1) -> Dict[str, Any]:
    """Create a cart item from Pokemon data"""
    return {
        "product_id": str(pokemon['numero']),
        "name": pokemon['nombre'].capitalize(),
        "quantity": quantity,
        "price": pokemon['precio'],
        "total": pokemon['precio'] * quantity,
        "available": pokemon.get('enVenta', False) and pokemon['inventario']['disponibles'] >= quantity
    }

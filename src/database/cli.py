#!/usr/bin/env python3
"""
Database CLI for MCP Server

This script provides database access for the TypeScript MCP server.
It can be called from Node.js to query Pokemon data.
"""

import sys
import json
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.database import SessionLocal, Pokemon


def get_pokemon_by_numero(numero: int) -> dict:
    """Get Pokemon by numero"""
    with SessionLocal() as db:
        pokemon = db.query(Pokemon).filter(Pokemon.numero == numero).first()
        if not pokemon:
            return {"error": f"Pokemon {numero} not found"}
        
        return {
            "numero": pokemon.numero,
            "nombre": pokemon.nombre,
            "precio": pokemon.precio,
            "enVenta": pokemon.en_venta,
            "inventario": {
                "total": pokemon.inventario_total,
                "disponibles": pokemon.inventario_disponible,
                "vendidos": pokemon.inventario_vendido
            }
        }


def get_pokemon_by_name(nombre: str) -> dict:
    """Get Pokemon by name"""
    with SessionLocal() as db:
        pokemon = db.query(Pokemon).filter(
            Pokemon.nombre.ilike(nombre)
        ).first()
        
        if not pokemon:
            return {"error": f"Pokemon {nombre} not found"}
        
        return {
            "numero": pokemon.numero,
            "nombre": pokemon.nombre,
            "precio": pokemon.precio,
            "enVenta": pokemon.en_venta,
            "inventario": {
                "total": pokemon.inventario_total,
                "disponibles": pokemon.inventario_disponible,
                "vendidos": pokemon.inventario_vendido
            }
        }


def get_all_pokemon() -> list:
    """Get all Pokemon"""
    with SessionLocal() as db:
        pokemon_list = db.query(Pokemon).order_by(Pokemon.numero).all()
        
        return [
            {
                "numero": p.numero,
                "nombre": p.nombre,
                "precio": p.precio,
                "enVenta": p.en_venta,
                "inventario": {
                    "total": p.inventario_total,
                    "disponibles": p.inventario_disponible,
                    "vendidos": p.inventario_vendido
                }
            }
            for p in pokemon_list
        ]


def update_inventory(numero: int, cantidad_vendida: int) -> dict:
    """Update Pokemon inventory after a sale"""
    with SessionLocal() as db:
        pokemon = db.query(Pokemon).filter(Pokemon.numero == numero).first()
        
        if not pokemon:
            return {"error": f"Pokemon {numero} not found"}
        
        if pokemon.inventario_disponible < cantidad_vendida:
            return {"error": f"Insufficient stock for {pokemon.nombre}"}
        
        # Update inventory
        pokemon.inventario_disponible -= cantidad_vendida
        pokemon.inventario_vendido += cantidad_vendida
        db.commit()
        
        return {
            "success": True,
            "numero": pokemon.numero,
            "nombre": pokemon.nombre,
            "disponibles": pokemon.inventario_disponible,
            "vendidos": pokemon.inventario_vendido
        }


def main():
    """Main CLI function"""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No command specified"}))
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        if command == "get_by_numero":
            if len(sys.argv) < 3:
                print(json.dumps({"error": "Numero required"}))
                sys.exit(1)
            numero = int(sys.argv[2])
            result = get_pokemon_by_numero(numero)
            print(json.dumps(result))
        
        elif command == "get_by_name":
            if len(sys.argv) < 3:
                print(json.dumps({"error": "Name required"}))
                sys.exit(1)
            nombre = sys.argv[2]
            result = get_pokemon_by_name(nombre)
            print(json.dumps(result))
        
        elif command == "get_all":
            result = get_all_pokemon()
            print(json.dumps(result))
        
        elif command == "update_inventory":
            if len(sys.argv) < 4:
                print(json.dumps({"error": "Numero and quantity required"}))
                sys.exit(1)
            numero = int(sys.argv[2])
            cantidad = int(sys.argv[3])
            result = update_inventory(numero, cantidad)
            print(json.dumps(result))
        
        else:
            print(json.dumps({"error": f"Unknown command: {command}"}))
            sys.exit(1)
    
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()

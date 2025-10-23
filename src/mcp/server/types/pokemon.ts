/**
 * Pokemon Data Types
 * Local price and inventory types from pokemon-gen1.json
 */

export interface PokemonPrice {
  numero: number;
  nombre: string;
  precio: number;
  enVenta: boolean;
  estado: string;
  inventario: {
    total: number;
    disponibles: number;
    vendidos: number;
  };
}

export interface PokemonInfo {
  id: number;
  name: string;
  height: number;
  weight: number;
  types: Array<{ type: { name: string } }>;
  abilities: Array<{ ability: { name: string } }>;
  stats: Array<{ base_stat: number; stat: { name: string } }>;
  sprites: {
    front_default: string | null;
    front_shiny?: string | null;
  };
}

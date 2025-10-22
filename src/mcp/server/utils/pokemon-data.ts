/**
 * Pokemon Data Loading and Caching
 * Handles loading Pokemon data from database or JSON fallback
 */

import { readFile } from "fs/promises";
import { dirname, join } from "path";
import { fileURLToPath } from "url";
import type { PokemonPrice } from "../types/index.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Caché para los datos de precios
let pokemonPricesCache: PokemonPrice[] | null = null;

/**
 * Load Pokemon data from database via Python CLI
 * Falls back to JSON file if database is unavailable
 */
export async function loadPokemonPrices(): Promise<PokemonPrice[]> {
  if (pokemonPricesCache) {
    return pokemonPricesCache;
  }

  try {
    // Call Python CLI to get Pokemon data from database
    const { exec } = await import('child_process');
    const { promisify } = await import('util');
    const execAsync = promisify(exec);
    
    const cliPath = join(__dirname, "../../../..","ap2-integration/src/database/cli.py");
    const pythonPath = join(__dirname, "../../../..", ".venv/bin/python");
    const repoRoot = join(__dirname, "../../../..");
    
    const { stdout, stderr } = await execAsync(
      `cd "${repoRoot}" && PYTHONPATH=ap2-integration ${pythonPath} ${cliPath} get_all`,
      { maxBuffer: 10 * 1024 * 1024 } // 10MB buffer for large datasets
    );
    
    if (stderr && !stderr.includes('RuntimeWarning')) {
      console.error("⚠️  Database CLI stderr:", stderr);
    }
    
    const result = JSON.parse(stdout);
    if (result.error) {
      throw new Error(result.error);
    }
    
    pokemonPricesCache = result;
    console.error(`✅ Loaded ${result.length} Pokemon from database`);
    return pokemonPricesCache!;
  } catch (error) {
    console.error("❌ Error loading pokemon from database:", error);
    console.error("⚠️  Falling back to JSON file...");
    
    // Fallback to JSON file if database fails
    try {
      const pokemonDataPath = join(__dirname, "../../../..", "pokemon-gen1.json");
      const data = await readFile(pokemonDataPath, "utf-8");
      pokemonPricesCache = JSON.parse(data);
      const count = pokemonPricesCache?.length || 0;
      console.error(`✅ Loaded ${count} Pokemon from JSON file (fallback)`);
      return pokemonPricesCache!;
    } catch (fallbackError) {
      console.error("❌ Fallback also failed:", fallbackError);
      return [];
    }
  }
}

/**
 * Clear the Pokemon prices cache (useful for testing)
 */
export function clearPokemonCache(): void {
  pokemonPricesCache = null;
}

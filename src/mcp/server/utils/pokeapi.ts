/**
 * PokeAPI Integration
 * Handles API requests to pokeapi.co
 */

/**
 * Make a request to PokeAPI
 * @param endpoint - The API endpoint (e.g., "pokemon/25" or "type/fire")
 * @returns Promise with the JSON response
 */
export async function fetchPokeAPI(endpoint: string): Promise<any> {
  const response = await fetch(`https://pokeapi.co/api/v2/${endpoint}`);
  if (!response.ok) {
    throw new Error(`PokeAPI error: ${response.statusText}`);
  }
  return response.json();
}

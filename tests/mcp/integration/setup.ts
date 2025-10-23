/**
 * Setup and utilities for MCP integration tests
 * Provides common test fixtures and helpers
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema } from "@modelcontextprotocol/sdk/types.js";

/**
 * Create a mock MCP server for testing
 */
export function createTestServer(): Server {
  const server = new Server(
    {
      name: "test-pokemon-server",
      version: "1.0.0-test",
    },
    {
      capabilities: {
        tools: {},
      },
    }
  );
  
  return server;
}

/**
 * Mock tool execution helper
 */
export async function executeTool(
  server: Server,
  toolName: string,
  args: Record<string, unknown>
): Promise<any> {
  const handlers = (server as any)._requestHandlers.get("tools/call");
  
  if (!handlers || handlers.length === 0) {
    throw new Error("No tool handlers registered");
  }
  
  const handler = handlers[0];
  const response = await handler({
    method: "tools/call",
    params: {
      name: toolName,
      arguments: args,
    },
  });
  
  return response;
}

/**
 * Extract text content from tool response
 */
export function extractTextContent(response: any): string {
  if (!response.content || response.content.length === 0) {
    return "";
  }
  
  const textContent = response.content.find((c: any) => c.type === "text");
  return textContent?.text || "";
}

/**
 * Parse JSON from tool response
 */
export function parseToolResponse<T>(response: any): T {
  const text = extractTextContent(response);
  return JSON.parse(text) as T;
}

/**
 * Wait for async operations to complete
 */
export function wait(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Test data fixtures
 */
export const TEST_POKEMON = {
  pikachu: {
    name: "pikachu",
    number: "25",
  },
  charizard: {
    name: "charizard", 
    number: "6",
  },
  bulbasaur: {
    name: "bulbasaur",
    number: "1",
  },
  mew: {
    name: "mew",
    number: "151",
  },
};

/**
 * Test cart items
 */
export const TEST_CART_ITEMS = [
  { product_id: "25", quantity: 1 }, // Pikachu
  { product_id: "6", quantity: 2 },  // Charizard x2
];

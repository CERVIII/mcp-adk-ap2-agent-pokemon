# Pokemon MCP + AP2 Agent - AI Coding Instructions

## Language
When performing a code review, respond in Spanish.

## Project Overview
This is a Pokemon marketplace implementing **MCP (Model Context Protocol)** with **AP2 (Agent Payments Protocol)** support. The architecture combines a TypeScript MCP server exposing Pokemon catalog tools with Python-based shopping/merchant agents that coordinate purchases through the AP2 protocol.

## Architecture & Data Flow

### Core Components
1. **MCP Server** (`mcp-server/src/index.ts`) - Unified TypeScript server exposing 6 tools via stdio transport:
   - Pokemon catalog queries (PokeAPI integration)
   - Local pricing/inventory (`pokemon-gen1.json` - 151 Gen 1 Pokemon)
   - **AP2 CartMandate creation** with merchant signatures

2. **Data Source** (`pokemon-gen1.json`) - Single source of truth for pricing:
   - Each Pokemon has: `numero`, `nombre`, `precio`, `enVenta`, `inventario{total, disponibles, vendidos}`
   - Referenced by both `main.ts` (simple demo) and `mcp-server/src/index.ts` (full server)

3. **Client Implementations** (referenced but not in workspace):
   - ADK Shopping Agent (Python/Gemini) - Port 8000
   - AP2 Merchant Agent (FastAPI) - Port 8001
   - Claude Desktop / GitHub Copilot integration via `claude_desktop_config.json`

### Key Architectural Patterns

**Dual-Server Setup**: `main.ts` is a simplified demo server, while `mcp-server/src/index.ts` is the production server with full AP2 support. They share the same data file but expose different tool sets.

**AP2 CartMandate Flow**:
```typescript
// CartMandate structure follows AP2 spec exactly:
CartMandate {
  contents: { id, user_signature_required: false, payment_request }
  merchant_signature: "sig_merchant_pokemon_{cartId}"
  timestamp: ISO8601
  merchantName: "PokeMart - Primera Generación"
}
```
Created in `createCartMandate()` (line ~165), formatted in `formatCartMandateDisplay()` for agent consumption.

**Tool Registration Pattern**: All tools use `server.setRequestHandler(CallToolRequestSchema, ...)` with a switch-case dispatcher (line ~418). Each tool parses args with Zod schemas inline.

## Development Workflows

### Build & Run Commands
```bash
# Primary development commands (use these, not npm directly):
make setup           # Full install + build
make build           # Compile TypeScript only
./scripts/setup.sh   # Alternative to make setup

# Testing MCP server:
python tests/test_mcp_simple.py  # Quick validation
./tests/test_unified_mcp.sh      # Full integration test

# Running components (scripts handle env vars & ports):
./scripts/run-adk.sh        # Simple conversational agent
./scripts/run-ap2-demo.sh   # Full merchant + shopping demo
```

**Never run** `npm start` directly - MCP servers need careful stdio handling. Use test scripts or integration scripts.

### Environment Configuration
- Both `adk-agent/.env` and `ap2-integration/.env` need `GOOGLE_API_KEY` from AI Studio
- MCP server has NO environment dependencies - it's pure TypeScript with external API calls

## Project-Specific Conventions

### Pokemon Identification
Tools accept **flexible identifiers**: name ("pikachu") OR number ("25") OR zero-padded ("025"). Always normalize to lowercase and check all three formats:
```typescript
const pokemon = pokemonInventory.find(p => 
    p.nombre.toLowerCase() === query || 
    p.numero.toString() === query ||
    p.numero.toString().padStart(3, '0') === query
);
```

### Price Currency
All prices are **USD integers** (e.g., `"precio": 51` = $51.00). No decimal handling in data layer. Display with "USD" label in responses.

### Tool Response Format
Return **plain JSON strings** wrapped in `{ content: [{ type: "text", text: JSON.stringify(...) }] }`. Never return raw objects. Error responses set `isError: true`.

### AP2 Payment Processor URL
Hardcoded to `http://localhost:8003/a2a/processor` (line ~228) - this is the expected integration point for payment agents. Change if deploying to production.

## Critical Files & Their Roles

- **`mcp-server/src/index.ts`** (694 lines) - Main server implementation. Tools start at line ~270, AP2 helpers at line ~140
- **`pokemon-gen1.json`** - DO NOT modify structure. Agents depend on exact field names
- **`main.ts`** - Simplified 3-tool server for demos. Use for learning, not production
- **`Makefile`** - Orchestrates multi-language builds. Prefer this over individual package managers

## MCP Tools Exposed

1. `get_pokemon_info` - PokeAPI data (types, stats, abilities, sprites)
2. `get_pokemon_price` - Local inventory lookup
3. `search_pokemon` - Filter by type (PokeAPI) + price/availability (local)
4. `list_pokemon_types` - All types from PokeAPI (excludes "unknown", "shadow")
5. **`create_pokemon_cart`** - AP2 CartMandate with merchant signature
6. **`get_pokemon_product`** - Combined PokeAPI + pricing info (one-stop lookup)

### Common Integration Pattern
Shopping agents typically:
1. Search with `search_pokemon` (filters)
2. Get details with `get_pokemon_product` (full info)
3. Create cart with `create_pokemon_cart` (AP2 flow)
4. Process payment via merchant agent's AP2 endpoints (not in MCP scope)

## Testing & Debugging

When tools fail, check:
1. **PokeAPI availability** - External dependency may timeout
2. **Pokemon number range** - Only Gen 1 (1-151) in local catalog
3. **Inventory stock** - `create_pokemon_cart` validates `disponibles` count
4. **Transport setup** - Server must use `StdioServerTransport`, test with `python tests/test_mcp_simple.py`

## Key External Dependencies

- **PokeAPI** (`pokeapi.co/api/v2`) - Free, no auth required, rate-limited
- **MCP SDK** - `@modelcontextprotocol/sdk` v1.20.0+ required for server/stdio classes
- **Google ADK** - Used by Python agents (not MCP server itself)

## Adding New Tools

1. Add tool metadata to `TOOLS` array (line ~260)
2. Add case to switch statement in `CallToolRequestSchema` handler
3. Define Zod schema inline: `const schema = z.object({...}); const {...} = schema.parse(args);`
4. Return structured JSON wrapped in `content` array
5. Update `mcp-server/README.md` with tool documentation

## Common Pitfalls

- **Don't mix `main.ts` and `mcp-server/src/index.ts`** - they're separate servers with different tool sets
- **CartMandate `user_signature_required` is always `false`** - Pokemon purchases don't need user auth in this demo
- **Search by type is slow** - must fetch type data from PokeAPI then filter local inventory. Consider caching for production.
- **Scripts use `uv` not `pip`** - Python dependency manager preference in this project

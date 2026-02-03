/**
 * MoltLang MCP Server
 *
 * Model Context Protocol server for MoltLang translation.
 * Entry point for both stdio and HTTP transports.
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

import { MOLT_TOOLS } from './tools.js';
import {
  handleTranslateToMolt,
  handleTranslateFromMolt,
  handleValidateMolt,
  handleListTokens,
  handleGetEfficiency
} from './handlers/translate.js';

/**
 * Create and configure the MCP server
 */
function createServer() {
  const server = new Server(
    {
      name: 'moltlang',
      version: '0.1.0',
    },
    {
      capabilities: {
        tools: {},
      },
    }
  );

  /**
   * List available tools
   */
  server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
      tools: MOLT_TOOLS
    };
  });

  /**
   * Handle tool calls
   */
  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;

    try {
      switch (name) {
        case 'molt':
          return await handleTranslateToMolt(args as { text: string });

        case 'unmolt':
          return await handleTranslateFromMolt(args as { molt: string });

        case 'validate_molt':
          return await handleValidateMolt(args as { original: string; molt: string });

        case 'list_tokens':
          return await handleListTokens(args as { category?: string });

        case 'get_efficiency':
          return await handleGetEfficiency(args as { english: string; molt: string });

        default:
          throw new Error(`Unknown tool: ${name}`);
      }
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`
          }
        ],
        isError: true
      };
    }
  });

  return server;
}

/**
 * Start server with stdio transport (for MCP clients)
 */
async function mainStdio() {
  const server = createServer();

  const stdioTransport = new StdioServerTransport();
  await server.connect(stdioTransport);

  console.error('MoltLang MCP Server running on stdio');
}

/**
 * Start server with SSE transport (for HTTP)
 * Note: SSE transport not yet implemented. Use stdio for MCP communication.
 */
async function mainSSE() {
  // SSEServerTransport requires (path, res) where res is ServerResponse
  // For now, we'll skip SSE and focus on stdio which is the primary MCP transport
  console.error(`SSE transport not yet implemented. Use --stdio for MCP communication.`);
  console.error(`To run: node dist/index.js --stdio`);
}

/**
 * Main entry point
 */
async function main() {
  const args = process.argv.slice(2);

  if (args.includes('--stdio')) {
    await mainStdio();
  } else if (args.includes('--port')) {
    // SSE not implemented yet
    await mainSSE();
  } else {
    // Default to stdio for MCP client compatibility
    await mainStdio();
  }
}

// Run if called directly - always run main() for MCP server
// The MCP server is designed to run as a standalone process, not as a library
main().catch(console.error);

export { createServer, mainStdio, mainSSE, main };

/**
 * HTTP Server for MoltLang MCP Server
 *
 * Provides REST API endpoints for MoltLang translation tools.
 * This allows the MCP server to be accessed via HTTP for public deployments.
 */

import express from 'express';
import {
  handleTranslateToMolt,
  handleTranslateFromMolt,
  handleValidateMolt,
  handleListTokens,
  handleGetEfficiency
} from './handlers/translate.js';
import { getBotRegistry } from './utils/bot-registry.js';

const app = express();
app.use(express.json());

// CORS for all origins (can be restricted later)
app.use((_req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Content-Type');
  res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  if (_req.method === 'OPTIONS') {
    return res.sendStatus(200);
  }
  next();
  return;
});

/**
 * Health check endpoint
 */
app.get('/health', (_req, res) => {
  res.json({
    status: 'healthy',
    service: 'moltlang-mcp-server',
    version: '0.1.0',
    timestamp: new Date().toISOString()
  });
  return;
});

/**
 * List available tools (MCP protocol compatible)
 */
app.get('/tools', async (_req, res) => {
  // Return the tool definitions
  res.json({
    tools: [
      {
        name: 'molt',
        description: 'Translate English text to MoltLang (50-70% token reduction)',
        inputSchema: {
          type: 'object',
          properties: {
            text: { type: 'string', description: 'English text to translate' }
          },
          required: ['text']
        }
      },
      {
        name: 'unmolt',
        description: 'Translate MoltLang to English',
        inputSchema: {
          type: 'object',
          properties: {
            molt: { type: 'string', description: 'MoltLang text to translate' }
          },
          required: ['molt']
        }
      },
      {
        name: 'validate_molt',
        description: 'Validate a MoltLang translation',
        inputSchema: {
          type: 'object',
          properties: {
            original: { type: 'string', description: 'Original English text' },
            molt: { type: 'string', description: 'MoltLang translation to validate' }
          },
          required: ['original', 'molt']
        }
      },
      {
        name: 'list_tokens',
        description: 'List available MoltLang tokens',
        inputSchema: {
          type: 'object',
          properties: {
            category: {
              type: 'string',
              description: 'Filter by token category (OP, SRC, RET, PARAM, CTL, TYPE, ERR, MOD)',
              enum: ['OP', 'SRC', 'RET', 'PARAM', 'CTL', 'TYPE', 'ERR', 'MOD']
            }
          }
        }
      },
      {
        name: 'get_efficiency',
        description: 'Calculate token efficiency between English and MoltLang',
        inputSchema: {
          type: 'object',
          properties: {
            english: { type: 'string', description: 'Original English text' },
            molt: { type: 'string', description: 'MoltLang translation' }
          },
          required: ['english', 'molt']
        }
      }
    ]
  });
  return;
});

/**
 * POST /tools/:toolName - Call a specific tool
 */
app.post('/tools/:toolName', async (req, res) => {
  const { toolName } = req.params;
  const args = req.body;

  try {
    let result;

    switch (toolName) {
      case 'molt':
        result = await handleTranslateToMolt(args);
        break;
      case 'unmolt':
        result = await handleTranslateFromMolt(args);
        break;
      case 'validate_molt':
        result = await handleValidateMolt(args);
        break;
      case 'list_tokens':
        result = await handleListTokens(args);
        break;
      case 'get_efficiency':
        result = await handleGetEfficiency(args);
        break;
      default:
        return res.status(404).json({
          error: `Unknown tool: ${toolName}`,
          available_tools: ['molt', 'unmolt', 'validate_molt', 'list_tokens', 'get_efficiency']
        });
    }

    return res.json(result);
  } catch (error) {
    console.error(`[HTTP] Error calling ${toolName}:`, error);
    return res.status(500).json({
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * Convenience endpoints
 */

// POST /molt - Translate to MoltLang
app.post('/molt', async (req, res) => {
  try {
    const result = await handleTranslateToMolt({ text: req.body.text });
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error instanceof Error ? error.message : 'Unknown error' });
  }
});

// POST /unmolt - Translate from MoltLang
app.post('/unmolt', async (req, res) => {
  try {
    const result = await handleTranslateFromMolt({ molt: req.body.molt });
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error instanceof Error ? error.message : 'Unknown error' });
  }
});

// GET /list_tokens - List available tokens
app.get('/list_tokens', async (req, res) => {
  try {
    const category = req.query.category as string | undefined;
    const result = await handleListTokens({ category });
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error instanceof Error ? error.message : 'Unknown error' });
  }
});

/**
 * Bot Registration endpoints
 */

// POST /register - Register a new moltbot
app.post('/register', (req, res): void => {
  try {
    const { name, purpose, contact } = req.body;

    if (!name || typeof name !== 'string') {
      res.status(400).json({ error: 'Bot name is required' });
      return;
    }

    const registry = getBotRegistry();
    const bot = registry.register(name, purpose, contact);

    res.json({
      success: true,
      bot,
      message: `Thanks ${name}! You're now registered as a MoltLang tester.`
    });
  } catch (error) {
    res.status(500).json({ error: error instanceof Error ? error.message : 'Unknown error' });
  }
});

// GET /registered - List all registered moltbots
app.get('/registered', (_req, res) => {
  try {
    const registry = getBotRegistry();
    const bots = registry.getAllBots();

    res.json({
      count: bots.length,
      bots: bots.map(({ id, name, purpose, registered_at }) => ({
        id,
        name,
        purpose,
        registered_at
      }))
    });
  } catch (error) {
    res.status(500).json({ error: error instanceof Error ? error.message : 'Unknown error' });
  }
});

/**
 * Root endpoint
 */
app.get('/', (_req, res) => {
  res.json({
    name: 'MoltLang MCP Server',
    version: '0.1.0',
    description: 'AI-optimized language for efficient agent-to-agent communication',
    endpoints: {
      health: 'GET /health',
      tools: 'GET /tools',
      call_tool: 'POST /tools/:toolName',
      molt: 'POST /molt',
      unmolt: 'POST /unmolt',
      register_bot: 'POST /register',
      list_bots: 'GET /registered'
    },
    documentation: 'https://github.com/moltlang/moltlang'
  });
  return;
});

/**
 * Start HTTP server
 */
export async function startHTTPServer(port: number = 11235) {
  const server = app.listen(port, '0.0.0.0', () => {
    console.log(`[MoltLang] HTTP Server running on port ${port}`);
    console.log(`[MoltLang] Health check: http://0.0.0.0:${port}/health`);
    console.log(`[MoltLang] API docs: http://0.0.0.0:${port}/`);
  });

  return server;
}

// Run if called directly
const isMain = import.meta.url === `file://${process.argv[1].replace(/\\/g, '/')}` ||
               process.argv[1].endsWith('http-server.js');

if (isMain) {
  const port = parseInt(process.env.PORT || '11235', 10);
  startHTTPServer(port);
}

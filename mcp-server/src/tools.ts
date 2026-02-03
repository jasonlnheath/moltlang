/**
 * MCP Tool Definitions for MoltLang
 *
 * Designed to minimize token overhead while maintaining clarity.
 * Each tool description is <50 characters to reduce MCP token cost.
 */

import { Tool } from '@modelcontextprotocol/sdk/types.js';

/**
 * Core translation tools
 * Token cost goal: <500 tokens per tool (including description)
 */
export const MOLT_TOOLS: Tool[] = [
  {
    name: 'molt',
    description: 'English→MoltLang (50-70% token reduction)',
    inputSchema: {
      type: 'object',
      properties: {
        text: {
          type: 'string',
          description: 'Text to translate to MoltLang'
        }
      },
      required: ['text']
    }
  },
  {
    name: 'unmolt',
    description: 'MoltLang→English translation',
    inputSchema: {
      type: 'object',
      properties: {
        molt: {
          type: 'string',
          description: 'MoltLang text to translate'
        }
      },
      required: ['molt']
    }
  },
  {
    name: 'validate_molt',
    description: 'Validate MoltLang translation quality',
    inputSchema: {
      type: 'object',
      properties: {
        original: {
          type: 'string',
          description: 'Original text (before translation)'
        },
        molt: {
          type: 'string',
          description: 'MoltLang translation to validate'
        }
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
    description: 'Calculate token efficiency vs English',
    inputSchema: {
      type: 'object',
      properties: {
        english: {
          type: 'string',
          description: 'Original English text'
        },
        molt: {
          type: 'string',
          description: 'MoltLang translation'
        }
      },
      required: ['english', 'molt']
    }
  }
];

/**
 * Token type enum for validation
 */
export const TOKEN_CATEGORIES = {
  OPERATION: 'OP',
  SOURCE: 'SRC',
  RETURN: 'RET',
  PARAMETER: 'PARAM',
  CONTROL: 'CTL',
  TYPE: 'TYPE',
  ERROR: 'ERR',
  MODIFIER: 'MOD'
} as const;

/**
 * Validate MoltLang syntax
 * Returns true if the MoltLang string has valid syntax
 */
export function isValidMoltSyntax(molt: string): boolean {
  if (!molt || typeof molt !== 'string') return false;

  // Check bracket matching
  const openCount = (molt.match(/\[/g) || []).length;
  const closeCount = (molt.match(/\]/g) || []).length;
  if (openCount !== closeCount) return false;

  // Check token format: [CATEGORY:TYPE] or [CATEGORY:TYPE=VALUE]
  const tokenPattern = /\[([A-Z]+):([A-Z_]+)(?:=([^\]]+))?\]/g;
  const tokens = molt.match(tokenPattern);
  if (!tokens || tokens.length === 0) return false;

  // Validate categories
  const validCategories = Object.values(TOKEN_CATEGORIES);
  for (const token of tokens) {
    const match = token.match(/\[([A-Z]+):/);
    if (!match) continue;
    const [, category] = match;
    if (!validCategories.includes(category as any)) {
      return false;
    }
  }

  return true;
}

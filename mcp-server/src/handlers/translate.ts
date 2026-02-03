/**
 * MCP Tool Handlers for MoltLang
 *
 * Each handler wraps a Python subprocess call and formats the response
 * for minimal token overhead. Metadata is embedded in the response.
 */

import {
  translateToMolt,
  translateFromMolt,
  validateTranslation as validateTranslationPython,
  listTokens as listTokensPython
} from '../utils/python.js';

/**
 * Handler: Translate English to MoltLang
 */
export async function handleTranslateToMolt(args: { text: string }): Promise<{
  content: Array<{ type: string; text: string }>;
}> {
  try {
    console.error(`[MoltLang] Translating: ${args.text.substring(0, 50)}...`);
    const result = await translateToMolt(args.text);

    // Embed metadata in response for minimal token overhead
    const meta = ` | tokens:${result.token_count} eff:${Math.round(result.efficiency * 100)}% conf:${Math.round(result.confidence * 100)}%`;

    return {
      content: [
        {
          type: 'text',
          text: result.text + meta
        }
      ]
    };
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`
        }
      ]
    };
  }
}

/**
 * Handler: Translate MoltLang to English
 */
export async function handleTranslateFromMolt(args: { molt: string }): Promise<{
  content: Array<{ type: string; text: string }>;
}> {
  try {
    const result = await translateFromMolt(args.molt);

    return {
      content: [
        {
          type: 'text',
          text: result.text
        }
      ]
    };
  } catch (error) {
    console.error(`[MoltLang] Translation error:`, error);
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`
        }
      ]
    };
  }
}

/**
 * Handler: Validate MoltLang translation
 */
export async function handleValidateMolt(args: { original: string; molt: string }): Promise<{
  content: Array<{ type: string; text: string }>;
}> {
  try {
    const result = await validateTranslationPython(args.original, args.molt);

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }
      ]
    };
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`
        }
      ]
    };
  }
}

/**
 * Handler: List available tokens
 */
export async function handleListTokens(args: { category?: string }): Promise<{
  content: Array<{ type: string; text: string }>;
}> {
  try {
    const result = await listTokensPython(args.category);

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }
      ]
    };
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`
        }
      ]
    };
  }
}

/**
 * Handler: Get efficiency metrics
 */
export async function handleGetEfficiency(args: { english: string; molt: string }): Promise<{
  content: Array<{ type: string; text: string }>;
}> {
  try {
    const englishWords = args.english.split(/\s+/).length;
    const moltTokens = (args.molt.match(/\[.*?\]/g) || []).length;
    const efficiency = englishWords > 0 ? (1 - (moltTokens / englishWords)) * 100 : 0;

    return {
      content: [
        {
          type: 'text',
          text: `English: ${englishWords} words | Molt: ${moltTokens} tokens | Efficiency: ${efficiency.toFixed(1)}%`
        }
      ]
    };
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`
        }
      ]
    };
  }
}

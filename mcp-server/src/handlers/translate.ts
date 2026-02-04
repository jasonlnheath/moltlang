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
import { getLogger } from '../utils/logger.js';

const logger = getLogger();

/**
 * Handler: Translate English to MoltLang
 */
export async function handleTranslateToMolt(args: { text: string }): Promise<{
  content: Array<{ type: string; text: string }>;
}> {
  const inputLen = args.text.length;
  let outputLen = 0;
  let success = false;
  let errorMsg: string | undefined;

  try {
    console.error(`[MoltLang] Translating: ${args.text.substring(0, 50)}...`);
    const result = await translateToMolt(args.text);

    // Embed metadata in response for minimal token overhead
    const meta = ` | tokens:${result.token_count} eff:${Math.round(result.efficiency * 100)}% conf:${Math.round(result.confidence * 100)}%`;
    const responseText = result.text + meta;
    outputLen = responseText.length;
    success = true;

    // Log usage
    logger.log('molt', inputLen, outputLen, success);

    return {
      content: [
        {
          type: 'text',
          text: responseText
        }
      ]
    };
  } catch (error) {
    errorMsg = error instanceof Error ? error.message : 'Unknown error';
    logger.log('molt', inputLen, outputLen, false, errorMsg);

    return {
      content: [
        {
          type: 'text',
          text: `Error: ${errorMsg}`
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
  const inputLen = args.molt.length;
  let outputLen = 0;
  let success = false;
  let errorMsg: string | undefined;

  try {
    const result = await translateFromMolt(args.molt);
    outputLen = result.text.length;
    success = true;

    logger.log('unmolt', inputLen, outputLen, success);

    return {
      content: [
        {
          type: 'text',
          text: result.text
        }
      ]
    };
  } catch (error) {
    errorMsg = error instanceof Error ? error.message : 'Unknown error';
    logger.log('unmolt', inputLen, outputLen, false, errorMsg);

    return {
      content: [
        {
          type: 'text',
          text: `Error: ${errorMsg}`
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
  const inputLen = args.original.length + args.molt.length;
  let outputLen = 0;
  let success = false;
  let errorMsg: string | undefined;

  try {
    const result = await validateTranslationPython(args.original, args.molt);
    const responseText = JSON.stringify(result, null, 2);
    outputLen = responseText.length;
    success = true;

    logger.log('validate', inputLen, outputLen, success);

    return {
      content: [
        {
          type: 'text',
          text: responseText
        }
      ]
    };
  } catch (error) {
    errorMsg = error instanceof Error ? error.message : 'Unknown error';
    logger.log('validate', inputLen, outputLen, false, errorMsg);

    return {
      content: [
        {
          type: 'text',
          text: `Error: ${errorMsg}`
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
  const inputLen = args.category?.length || 0;
  let outputLen = 0;
  let success = false;
  let errorMsg: string | undefined;

  try {
    const result = await listTokensPython(args.category);
    const responseText = JSON.stringify(result, null, 2);
    outputLen = responseText.length;
    success = true;

    logger.log('list_tokens', inputLen, outputLen, success);

    return {
      content: [
        {
          type: 'text',
          text: responseText
        }
      ]
    };
  } catch (error) {
    errorMsg = error instanceof Error ? error.message : 'Unknown error';
    logger.log('list_tokens', inputLen, outputLen, false, errorMsg);

    return {
      content: [
        {
          type: 'text',
          text: `Error: ${errorMsg}`
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
  const inputLen = args.english.length + args.molt.length;
  let outputLen = 0;
  let success = false;
  let errorMsg: string | undefined;

  try {
    const englishWords = args.english.split(/\s+/).length;
    const moltTokens = (args.molt.match(/\[.*?\]/g) || []).length;
    const efficiency = englishWords > 0 ? (1 - (moltTokens / englishWords)) * 100 : 0;

    const responseText = `English: ${englishWords} words | Molt: ${moltTokens} tokens | Efficiency: ${efficiency.toFixed(1)}%`;
    outputLen = responseText.length;
    success = true;

    logger.log('efficiency', inputLen, outputLen, success);

    return {
      content: [
        {
          type: 'text',
          text: responseText
        }
      ]
    };
  } catch (error) {
    errorMsg = error instanceof Error ? error.message : 'Unknown error';
    logger.log('efficiency', inputLen, outputLen, false, errorMsg);

    return {
      content: [
        {
          type: 'text',
          text: `Error: ${errorMsg}`
        }
      ]
    };
  }
}

/**
 * Python Bridge for MoltLang
 *
 * This module handles communication between the TypeScript MCP server
 * and the Python MoltLang package. It spawns Python subprocesses to execute
 * translation logic.
 */

import { spawn, ChildProcess } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

/**
 * Result from a Python translation call
 */
export interface PythonTranslationResult {
  /** The translated text */
  text: string;
  /** Number of tokens used */
  token_count: number;
  /** Original token count (for efficiency calc) */
  original_count: number;
  /** Token efficiency (0-1) */
  efficiency: number;
  /** Confidence score (0-1) */
  confidence: number;
}

/**
 * Configuration for Python bridge
 */
export interface PythonBridgeConfig {
  /** Path to MoltLang source directory */
  moltlangPath: string;
  /** Python executable path */
  pythonPath?: string;
  /** Timeout in milliseconds */
  timeout?: number;
}

/**
 * Default configuration
 */
const DEFAULT_CONFIG: PythonBridgeConfig = {
  moltlangPath: join(__dirname, '../../..'),
  pythonPath: 'python',
  timeout: 30000
};

/**
 * Execute Python code and return the result
 */
async function executePython(
  code: string,
  config: PythonBridgeConfig = DEFAULT_CONFIG
): Promise<string> {
  return new Promise((resolve, reject) => {
    const python = config.pythonPath || DEFAULT_CONFIG.pythonPath!;
    const timeout = config.timeout || DEFAULT_CONFIG.timeout;
    const cwd = config.moltlangPath || DEFAULT_CONFIG.moltlangPath;

    const proc: ChildProcess = spawn(python, ['-c', code], {
      cwd: cwd,
      env: {
        ...process.env,
        PYTHONPATH: join(cwd, 'src')
      }
    });

    let stdout = '';
    let stderr = '';

    if (proc.stdout) {
      proc.stdout.on('data', (data: Buffer) => {
        stdout += data.toString();
      });
    }

    if (proc.stderr) {
      proc.stderr.on('data', (data: Buffer) => {
        stderr += data.toString();
      });
    }

    const timer = setTimeout(() => {
      if (proc.kill) {
        proc.kill();
      }
      reject(new Error(`Python execution timeout (${timeout}ms)`));
    }, timeout);

    proc.on('close', (code: number | null) => {
      clearTimeout(timer);
      if (code !== 0) {
        reject(new Error(`Python execution failed with code ${code}: ${stderr}`));
      } else {
        resolve(stdout.trim());
      }
    });
  });
}

/**
 * Translate English text to MoltLang
 */
export async function translateToMolt(
  text: string,
  config?: PythonBridgeConfig
): Promise<PythonTranslationResult> {
  const sanitizedText = text.replace(/"/g, '\\"').replace(/\n/g, '\\n');
  const pythonCode = `
import sys
import json

sys.path.insert(0, 'src')
from moltlang import translate_to_molt

result = translate_to_molt("${sanitizedText}")

output = {
    "text": result.text,
    "token_count": result.token_count,
    "original_count": result.original_token_count,
    "efficiency": result.token_efficiency,
    "confidence": result.confidence
}

print(json.dumps(output))
`;

  const output = await executePython(pythonCode, config);
  return JSON.parse(output) as PythonTranslationResult;
}

/**
 * Translate MoltLang to English
 */
export async function translateFromMolt(
  molt: string,
  config?: PythonBridgeConfig
): Promise<PythonTranslationResult> {
  const sanitizedMolt = molt.replace(/"/g, '\\"').replace(/\n/g, '\\n');
  const pythonCode = `
import sys
import json

sys.path.insert(0, 'src')
from moltlang import translate_from_molt

result = translate_from_molt("${sanitizedMolt}")

output = {
    "text": result.text,
    "token_count": result.token_count,
    "original_count": 0,
    "efficiency": 0,
    "confidence": result.confidence
}

print(json.dumps(output))
`;

  const output = await executePython(pythonCode, config);
  return JSON.parse(output) as PythonTranslationResult;
}

/**
 * Validate a MoltLang translation
 */
export async function validateTranslation(
  original: string,
  molt: string,
  config?: PythonBridgeConfig
): Promise<{
  is_valid: boolean;
  score: number;
  token_efficiency: number;
  confidence: number;
  issues: Array<{
    type: string;
    message: string;
    severity: string;
  }>;
}> {
  const sanitizedOriginal = original.replace(/"/g, '\\"').replace(/\n/g, '\\n');
  const sanitizedMolt = molt.replace(/"/g, '\\"').replace(/\n/g, '\\n');

  const pythonCode = `
import sys
import json

sys.path.insert(0, 'src')
from moltlang import validate_translation

quality = validate_translation("${sanitizedOriginal}", "${sanitizedMolt}")

output = {
    "is_valid": quality.is_valid,
    "score": quality.score,
    "token_efficiency": quality.token_efficiency,
    "confidence": quality.confidence,
    "issues": [
        {"type": issue.type.value, "message": issue.message, "severity": issue.severity}
        for issue in quality.issues
    ]
}

print(json.dumps(output))
`;

  const output = await executePython(pythonCode, config);
  return JSON.parse(output);
}

/**
 * List available MoltLang tokens
 */
export async function listTokens(
  category: string | undefined,
  config?: PythonBridgeConfig
): Promise<{
  tokens: Array<{ name: string; value: string }>;
  count: number;
  category?: string;
}> {
  const categoryFilter = category ? `token_type_prefix = "${category}"` : '';
  const categoryLogic = category ? `
tokens = [t for t in TokenType if t.name.startswith(token_type_prefix)]
` : 'tokens = list(TokenType)';
  const categoryOutput = category ? 'output["category"] = "${category}"' : '';

  const pythonCode = `
import sys
import json
sys.path.insert(0, 'src')
from moltlang.tokens import TokenType, TokenRegistry

registry = TokenRegistry()
${categoryFilter}

${categoryLogic}

output = {
    "tokens": [{"name": t.name, "value": t.value} for t in tokens],
    "count": len(tokens)
}
${categoryOutput}

print(json.dumps(output))
`;

  const output = await executePython(pythonCode, config);
  return JSON.parse(output);
}

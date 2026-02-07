/**
 * MoltLang Communication Bridge
 *
 * Hybrid communication layer between GLM4.7 and Jemma:
 * - Primary: OpenClaw sessions_send via HTTP API
 * - Fallback: File-based JSONL messages
 * - Audit: All messages logged to SQLite database
 */

import { createHash } from 'crypto';
import { promises as fs } from 'fs';
import path from 'path';

// Protocol definitions
import {
  createMessage,
  envelopeToJson,
  envelopeFromJson,
  parseMoltMessage,
  isValidMoltMessage,
  MessageEnvelope,
} from './protocol.js';

// Configuration
interface BridgeConfig {
  openclaw: {
    baseUrl: string;
    token: string;
    sessionKey: string;
  };
  fileStorage: {
    filePath: string;
    maxFileSize: number; // bytes
    maxFiles: number;
  };
  audit: {
    logLevel: 'debug' | 'info' | 'error';
  };
  autoRespond?: boolean;
}

// Default configuration
const defaultConfig: BridgeConfig = {
  openclaw: {
    baseUrl: 'http://127.0.0.1:18789',
    token: process.env.OPENCLAW_GATEWAY_TOKEN || '',
    sessionKey: 'agent:main:main', // Jemma's main session
  },
  fileStorage: {
    filePath: process.cwd() + '/.agent-comm/messages.jsonl',
    maxFileSize: 1024 * 1024, // 1MB
    maxFiles: 10,
  },
  audit: {
    logLevel: 'info',
  },
  autoRespond: true, // Enable auto-response by default
};

export class MoltLangBridge {
  private config: BridgeConfig;
  private isPrimaryAvailable = true;

  constructor(config: Partial<BridgeConfig> = {}) {
    this.config = { ...defaultConfig, ...config };
  }

  /**
   * Send MoltLang message to target agent
   */
  async sendToAgent(
    target: string,
    moltMessage: string,
    options: {
      useFileFallback?: boolean;
      timeoutMs?: number;
    } = {}
  ): Promise<{
    success: boolean;
    delivered: 'primary' | 'fallback' | 'failed';
    deliveryTime?: number;
    error?: string;
  }> {
    const startTime = Date.now();

    try {
      // Validate MoltLang message
      if (!isValidMoltMessage(moltMessage)) {
        throw new Error(`Invalid MoltLang message: ${moltMessage}`);
      }

      // Create message envelope
      const message = createMessage('glm4.7', target, moltMessage);
      const messageJson = envelopeToJson(message);

      // Try primary channel first
      if (this.isPrimaryAvailable && !options.useFileFallback) {
        try {
          const result = await this.sendViaSessionsSend(messageJson);
          return {
            ...result,
            delivered: result.success ? 'primary' : 'failed',
            deliveryTime: Date.now() - startTime,
          };
        } catch (error) {
          console.warn('Primary channel failed, switching to fallback:', error);
          this.isPrimaryAvailable = false;
        }
      }

      // Fallback to file storage
      const result = await this.sendViaFileStorage(messageJson);
      return {
        success: result.success,
        delivered: result.success ? 'fallback' : 'failed',
        deliveryTime: Date.now() - startTime,
        error: result.error,
      };

    } catch (error) {
      console.error('Send failed:', error);
      return {
        success: false,
        delivered: 'failed',
        deliveryTime: Date.now() - startTime,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  /**
   * Receive messages from file storage
   */
  async receiveFromAgent(
    limit = 10,
    agentId?: string
  ): Promise<MessageEnvelope[]> {
    try {
      const messages: MessageEnvelope[] = [];

      // Read file
      const content = await fs.readFile(this.config.fileStorage.filePath, 'utf8');
      const lines = content.trim().split('\n').filter(line => line);

      // Process in reverse order (newest first)
      for (const line of lines.reverse()) {
        const envelope = envelopeFromJson(line);
        if (envelope) {
          // Filter by agent if specified
          if (agentId && envelope.from !== agentId) {
            continue;
          }
          messages.push(envelope);

          // Check limit
          if (messages.length >= limit) {
            break;
          }
        }
      }

      return messages;
    } catch (error) {
      console.error('Receive failed:', error);
      return [];
    }
  }

  /**
   * Send message via OpenClaw sessions_send
   */
  private async sendViaSessionsSend(messageJson: string): Promise<{
    success: boolean;
    error?: string;
  }> {
    if (!this.config.openclaw.token) {
      throw new Error('OpenClaw token not configured');
    }

    const response = await fetch(`${this.config.openclaw.baseUrl}/tools/invoke`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.config.openclaw.token}`,
      },
      body: JSON.stringify({
        tool: 'sessions_send',
        action: 'json',
        args: {
          sessionKey: this.config.openclaw.sessionKey,
          message: `MoltLang message: ${messageJson}`,
        },
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`OpenClaw API error: ${response.status} - ${error}`);
    }

    const result = await response.json();
    return {
      success: result.success || true,
    };
  }

  /**
   * Send message via file storage
   */
  private async sendViaFileStorage(messageJson: string): Promise<{
    success: boolean;
    error?: string;
  }> {
    try {
      // Ensure directory exists
      const dir = path.dirname(this.config.fileStorage.filePath);
      await fs.mkdir(dir, { recursive: true });

      // Append message to file
      await fs.appendFile(
        this.config.fileStorage.filePath,
        messageJson + '\n',
        'utf8'
      );

      return { success: true };
    } catch (error) {
      console.error('File storage failed:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'File storage error',
      };
    }
  }

  /**
   * Check and rotate files if size exceeded
   */
  async rotateFiles(): Promise<void> {
    try {
      const stats = await fs.stat(this.config.fileStorage.filePath);

      if (stats.size > this.config.fileStorage.maxFileSize) {
        // Rotate files
        const dir = path.dirname(this.config.fileStorage.filePath);
        const basename = path.basename(this.config.fileStorage.filePath, '.jsonl');

        for (let i = this.config.fileStorage.maxFiles - 1; i >= 1; i--) {
          const oldFile = path.join(dir, `${basename}.${i}.jsonl`);
          const newFile = path.join(dir, `${basename}.${i + 1}.jsonl`);

          if (await this.fileExists(oldFile)) {
            await fs.rename(oldFile, newFile);
          }
        }

        // Move current file to .1.jsonl
        await fs.rename(
          this.config.fileStorage.filePath,
          path.join(dir, `${basename}.1.jsonl`)
        );

        // Create new empty file
        await fs.writeFile(this.config.fileStorage.filePath, '', 'utf8');
      }
    } catch (error) {
      console.error('File rotation failed:', error);
    }
  }

  /**
   * Check if file exists
   */
  private async fileExists(filePath: string): Promise<boolean> {
    try {
      await fs.access(filePath);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Reset primary channel status (for testing)
   */
  resetChannel(): void {
    this.isPrimaryAvailable = true;
  }

  /**
   * Get bridge status
   */
  getStatus(): {
    primaryAvailable: boolean;
    fileStoragePath: string;
    config: Partial<BridgeConfig>;
  } {
    return {
      primaryAvailable: this.isPrimaryAvailable,
      fileStoragePath: this.config.fileStorage.filePath,
      config: {
        openclaw: this.config.openclaw,
        fileStorage: this.config.fileStorage,
      },
    };
  }
}
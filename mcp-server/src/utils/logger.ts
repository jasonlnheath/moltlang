/**
 * Usage Logger for MoltLang MCP Server
 *
 * Tracks usage patterns for analytics and understanding user behavior.
 */

import fs from 'fs';
import path from 'path';

interface UsageLog {
  timestamp: string;
  request_type: string;
  user_id: string;
  input_length: number;
  output_length: number;
  success: boolean;
  error?: string;
}

class UsageLogger {
  private logFile: string;
  private userId: string;

  constructor() {
    // Use /tmp in production or local directory for development
    const logDir = process.env.RAILWAY_VOLUME_MOUNT_PATH || '/tmp';
    this.logFile = path.join(logDir, 'moltlang-usage.jsonl');
    this.userId = this.generateUserId();
  }

  /**
   * Generate a persistent user ID from session or create new one
   */
  private generateUserId(): string {
    // Try to use existing session ID or generate new one
    if (!(global as any).__moltlangUserId) {
      (global as any).__moltlangUserId = `user-${Date.now()}-${Math.random().toString(36).substring(2, 8)}`;
    }
    return (global as any).__moltlangUserId;
  }

  /**
   * Log a usage event
   */
  log(requestType: string, inputLength: number, outputLength: number, success: boolean, error?: string): void {
    const logEntry: UsageLog = {
      timestamp: new Date().toISOString(),
      request_type: requestType,
      user_id: this.userId,
      input_length: inputLength,
      output_length: outputLength,
      success: success,
      error: error
    };

    try {
      // Append to JSONL file (one JSON object per line)
      fs.appendFileSync(this.logFile, JSON.stringify(logEntry) + '\n');
    } catch (err) {
      // Silently fail if logging doesn't work - don't break the service
      console.error('[MoltLang] Failed to write usage log:', err);
    }
  }

  /**
   * Get log file path (for debugging)
   */
  getLogFilePath(): string {
    return this.logFile;
  }
}

// Singleton instance
let loggerInstance: UsageLogger | null = null;

export function getLogger(): UsageLogger {
  if (!loggerInstance) {
    loggerInstance = new UsageLogger();
  }
  return loggerInstance;
}

export { UsageLogger, UsageLog };

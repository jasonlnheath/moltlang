/**
 * Bot Registry for MoltLang
 *
 * Tracks moltbots that register to use/test MoltLang.
 * Simple file-based storage for deployment simplicity.
 */

import fs from 'fs';
import path from 'path';

export interface BotRegistration {
  id: string;
  name: string;
  purpose?: string;
  contact?: string;
  registered_at: string;
}

class BotRegistry {
  private registryFile: string;
  private bots: Map<string, BotRegistration>;

  constructor() {
    const registryDir = process.env.RAILWAY_VOLUME_MOUNT_PATH || '/tmp';
    this.registryFile = path.join(registryDir, 'bot-registry.jsonl');
    this.bots = new Map();
    this.loadRegistry();
  }

  /**
   * Load existing registry from file
   */
  private loadRegistry(): void {
    try {
      if (fs.existsSync(this.registryFile)) {
        const lines = fs.readFileSync(this.registryFile, 'utf-8').split('\n').filter(Boolean);
        for (const line of lines) {
          try {
            const bot: BotRegistration = JSON.parse(line);
            this.bots.set(bot.id, bot);
          } catch {
            // Skip malformed lines
          }
        }
      }
    } catch (err) {
      console.error('[BotRegistry] Failed to load registry:', err);
    }
  }

  /**
   * Save a bot registration to file
   */
  private saveBot(bot: BotRegistration): void {
    try {
      fs.appendFileSync(this.registryFile, JSON.stringify(bot) + '\n');
    } catch (err) {
      console.error('[BotRegistry] Failed to save bot:', err);
    }
  }

  /**
   * Register a new bot
   */
  register(name: string, purpose?: string, contact?: string): BotRegistration {
    const id = `bot-${Date.now()}-${Math.random().toString(36).substring(2, 8)}`;
    const bot: BotRegistration = {
      id,
      name,
      purpose,
      contact,
      registered_at: new Date().toISOString()
    };

    this.bots.set(id, bot);
    this.saveBot(bot);

    console.error(`[BotRegistry] Bot registered: ${name} (${id})`);
    return bot;
  }

  /**
   * Get all registered bots
   */
  getAllBots(): BotRegistration[] {
    return Array.from(this.bots.values()).sort((a, b) =>
      new Date(b.registered_at).getTime() - new Date(a.registered_at).getTime()
    );
  }

  /**
   * Get bot count
   */
  getCount(): number {
    return this.bots.size;
  }
}

// Singleton instance
let registryInstance: BotRegistry | null = null;

export function getBotRegistry(): BotRegistry {
  if (!registryInstance) {
    registryInstance = new BotRegistry();
  }
  return registryInstance;
}

export { BotRegistry };

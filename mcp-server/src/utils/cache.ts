/**
 * Translation Cache for MoltLang MCP Server
 *
 * Reduces redundant Python subprocess calls by caching common translations.
 * Two-tier cache: memory (hot) + TTL-based expiration.
 */

interface CachedTranslation {
  molt: string;
  token_count: number;
  efficiency: number;
  confidence: number;
  cached_at: number;
}

interface CacheEntry extends CachedTranslation {
  ttl: number; // Time to live in milliseconds
}

/**
 * In-memory cache store
 */
class TranslationCache {
  private cache = new Map<string, CacheEntry>();
  private defaultTTL = 3600000; // 1 hour in milliseconds

  /**
   * Generate cache key from input
   */
  private generateKey(text: string, direction: 'to_molt' | 'from_molt'): string {
    return `${direction}:${text}`;
  }

  /**
   * Get cached translation if available and not expired
   */
  get(text: string, direction: 'to_molt' | 'from_molt'): CachedTranslation | null {
    const key = this.generateKey(text, direction);
    const entry = this.cache.get(key);

    if (!entry) {
      return null;
    }

    // Check if expired
    const now = Date.now();
    if (now > entry.cached_at + entry.ttl) {
      this.cache.delete(key);
      return null;
    }

    return entry;
  }

  /**
   * Set cached translation
   */
  set(
    text: string,
    direction: 'to_molt' | 'from_molt',
    result: CachedTranslation,
    ttl?: number
  ): void {
    const key = this.generateKey(text, direction);
    const entry: CacheEntry = {
      ...result,
      cached_at: Date.now(),
      ttl: ttl || this.defaultTTL
    };
    this.cache.set(key, entry);
  }

  /**
   * Clear expired entries
   */
  clearExpired(): number {
    const now = Date.now();
    let cleared = 0;

    for (const [key, entry] of this.cache.entries()) {
      if (now > entry.cached_at + entry.ttl) {
        this.cache.delete(key);
        cleared++;
      }
    }

    return cleared;
  }

  /**
   * Clear all cache entries
   */
  clear(): void {
    this.cache.clear();
  }

  /**
   * Get cache statistics
   */
  getStats(): { size: number; keys: string[] } {
    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys())
    };
  }
}

// Singleton instance
const cache = new TranslationCache();

/**
 * Get cached translation
 */
export function getCachedTranslation(
  text: string,
  direction: 'to_molt' | 'from_molt'
): CachedTranslation | null {
  return cache.get(text, direction);
}

/**
 * Set cached translation
 */
export function setCachedTranslation(
  text: string,
  direction: 'to_molt' | 'from_molt',
  result: CachedTranslation,
  ttl?: number
): void {
  cache.set(text, direction, result, ttl);
}

/**
 * Clear expired cache entries
 */
export function clearExpiredCache(): number {
  return cache.clearExpired();
}

/**
 * Get cache statistics
 */
export function getCacheStats(): { size: number; keys: string[] } {
  return cache.getStats();
}

import crypto from "crypto";
import fs from "fs";
import path from "path";
import { SourceStateItem } from "../validators/schema.js";

const BASE_DIR = process.cwd();
const STATE_FILE = path.join(BASE_DIR, "data", "source-state.json");

export function loadSourceState(): Record<string, SourceStateItem> {
  if (!fs.existsSync(STATE_FILE)) return {};
  try {
    return JSON.parse(fs.readFileSync(STATE_FILE, "utf-8"));
  } catch {
    return {};
  }
}

export function saveSourceState(state: Record<string, SourceStateItem>) {
  fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2), "utf-8");
}

export function computeContentHash(content: string): string {
  return crypto.createHash("sha256").update(content, "utf-8").digest("hex");
}

export interface ChangeDetectionResult {
  hasChanged: boolean;
  contentHash: string;
  etag?: string;
  lastModified?: string;
}

/**
 * 변경 감지기 (Brief 제5조, 제8조)
 * 이전 수집 데이터의 hash/ETag와 비교하여 변경이 없으면 즉시 중단(STOP)
 */
export function detectContentChange(
  url: string,
  newContent: string,
  newEtag?: string,
  newLastModified?: string
): ChangeDetectionResult {
  const stateMap = loadSourceState();
  const prevState = stateMap[url];
  const newHash = computeContentHash(newContent);

  if (!prevState) {
    return {
      hasChanged: true,
      contentHash: newHash,
      etag: newEtag,
      lastModified: newLastModified
    };
  }

  // 1. ETag 비교
  if (newEtag && prevState.etag && newEtag === prevState.etag) {
    return { hasChanged: false, contentHash: newHash, etag: newEtag };
  }

  // 2. 콘텐츠 해시 비교
  if (prevState.content_hash && prevState.content_hash === newHash) {
    return { hasChanged: false, contentHash: newHash };
  }

  return {
    hasChanged: true,
    contentHash: newHash,
    etag: newEtag,
    lastModified: newLastModified
  };
}

import { URL } from "url";

/**
 * 도메인 허용 목록(Allowed Domains) 검증 및 오픈 리다이렉트 방어 (Brief 제10조)
 */
export function isDomainAllowed(rawUrl: string, allowedDomains: string[]): boolean {
  if (!rawUrl) return false;

  try {
    const parsed = new URL(rawUrl);

    // 1. 프로토콜 검사 (http, https 외 javascript:, data: 차단)
    if (parsed.protocol !== "http:" && parsed.protocol !== "https:") {
      return false;
    }

    const hostname = parsed.hostname.toLowerCase();

    // 2. 허용 도메인 목록과 대조 (정확 일치 또는 서브도메인 일치 허용)
    return allowedDomains.some(allowed => {
      const lowerAllowed = allowed.toLowerCase().trim();
      if (hostname === lowerAllowed) return true;
      if (hostname.endsWith("." + lowerAllowed)) return true;
      return false;
    });
  } catch {
    return false;
  }
}

/**
 * URL 정규화 (파라미터 정리 및 표준화)
 */
export function normalizeUrl(rawUrl: string): string {
  try {
    const parsed = new URL(rawUrl);
    // 위험 파라미터 제거
    parsed.hash = "";
    return parsed.toString();
  } catch {
    return rawUrl;
  }
}

// 런타임 제한값 정의 (Brief 제11조)
export const RUNTIME_LIMITS = {
  MAX_AI_CALLS_PER_RUN: 50,
  MAX_PAGE_BYTES: 500_000,
  HTTP_TIMEOUT_MS: 10_000,
  MAX_REDIRECTS: 3,
  MAX_RETRIES: 2,
  DEFAULT_CHECK_INTERVAL_HOURS: 6
};

// HTML 태그 제거 및 텍스트 새니타이저 (Brief 제10조 XSS/Prompt Injection 방어)
export function sanitizeRawContent(input: string, maxBytes: number = RUNTIME_LIMITS.MAX_PAGE_BYTES): string {
  if (!input) return "";

  // 1. 최대 바이트 제한 절삭
  let trimmed = input;
  if (Buffer.byteLength(trimmed, "utf-8") > maxBytes) {
    trimmed = trimmed.substring(0, maxBytes);
  }

  // 2. 스크립트, 스타일 태그 내용 제거
  trimmed = trimmed.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, " ");
  trimmed = trimmed.replace(/<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>/gi, " ");
  trimmed = trimmed.replace(/<!--[\s\S]*?-->/g, " ");

  // 3. HTML 태그 제거
  trimmed = trimmed.replace(/<[^>]+>/g, " ");

  // 4. 공백 및 엔티티 정규화
  trimmed = trimmed
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\s+/g, " ")
    .trim();

  return trimmed;
}

// 프롬프트 인젝션 방어 검사
export function detectSuspiciousPatterns(text: string): boolean {
  const suspiciousKeywords = [
    "ignore previous instructions",
    "system prompt",
    "disregard all prior",
    "reveal secret",
    "환경변수 출력",
    "api key 노출"
  ];
  const lower = text.toLowerCase();
  return suspiciousKeywords.some(kw => lower.includes(kw));
}

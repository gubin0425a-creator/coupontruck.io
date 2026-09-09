import { z } from "zod";

// 1. Offer 타입 및 상태 정의 (Brief 제2조, 제7조)
export const OfferTypeEnum = z.enum([
  "COUPON",      // 결제 시 입력하는 실제 쿠폰코드
  "AFFILIATE",   // 운영자에게 수수료가 귀속되는 추적 링크
  "REFERRAL",    // 운영자/사이트의 추천인 코드 또는 초대 링크
  "PROMOTION",   // 브랜드 공식 일반 프로모션
  "SALE"         // 상품/서비스 자체 가격 인하
]);
export type OfferType = z.infer<typeof OfferTypeEnum>;

export const OfferStatusEnum = z.enum([
  "PUBLISHED",   // 규칙 통과 (신뢰도 95점 이상) 자동 게시
  "REVIEW",      // 신뢰도 75~94점 승인 대기 큐
  "REJECTED"     // 75점 미만 또는 규칙 불통과 폐기
]);
export type OfferStatus = z.infer<typeof OfferStatusEnum>;

export const SourceKindEnum = z.enum([
  "API",
  "AFFILIATE_FEED",
  "RSS",
  "OFFERS_PAGE",
  "SITEMAP",
  "HTML",
  "MANUAL"
]);
export type SourceKind = z.infer<typeof SourceKindEnum>;

// 검증 근거 (Evidence)
export const OfferEvidenceSchema = z.object({
  code_in_source: z.boolean().default(false),
  discount_in_source: z.boolean().default(false),
  expiry_in_source: z.boolean().default(false),
  domain_allowed: z.boolean().default(false),
  affiliate_matched: z.boolean().default(false),
  notes: z.array(z.string()).default([])
});
export type OfferEvidence = z.infer<typeof OfferEvidenceSchema>;

// Offer 마스터 스키마 (Brief 제7조)
export const OfferSchema = z.object({
  id: z.string(),
  brand: z.string(),
  brand_id: z.string(),
  category: z.enum(["travel", "shopping", "sub", "fashion", "game", "guide"]),
  type: OfferTypeEnum,
  title: z.string().min(2),
  description: z.string().default(""),
  coupon_code: z.string().optional(),
  discount_percent: z.number().min(0).max(100).optional(),
  max_discount_percent: z.number().min(0).max(100).optional(),
  is_up_to: z.boolean().default(false), // '최대 70%' vs '70% 할인' 구분
  discount_amount_krw: z.number().min(0).optional(),
  start_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional(),
  end_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional(),
  conditions: z.array(z.string()).default([]), // 신규/기존회원, 최소결제금액 등
  countries: z.array(z.string()).default(["KR"]),
  source_url: z.string().url(),
  source_kind: SourceKindEnum,
  target_url: z.string().url(), // 최종 도착 공식/제휴 URL
  affiliate_url: z.string().url().optional(),
  referral_code: z.string().optional(),
  verified_at: z.string(), // ISO-8601
  evidence: OfferEvidenceSchema,
  confidence: z.number().min(0).max(100),
  status: OfferStatusEnum,
  badge: z.string().nullable().optional()
});
export type Offer = z.infer<typeof OfferSchema>;

// 2. BrandConfig 스키마 (Brief 제6조, 제16조)
export const SourceConfigSchema = z.object({
  type: SourceKindEnum,
  url: z.string().url(),
  priority: z.number().min(1).max(5), // 1: 최우선
  selector: z.string().optional(),
  country: z.string().default("KR")
});
export type SourceConfig = z.infer<typeof SourceConfigSchema>;

export const BrandConfigSchema = z.object({
  brand_id: z.string(),
  name: z.string(),
  category: z.enum(["travel", "shopping", "sub", "fashion", "game", "guide"]),
  type: OfferTypeEnum,
  allowed_domains: z.array(z.string()).min(1), // 오픈 리다이렉트 방지 허용 도메인
  sources: z.array(SourceConfigSchema).min(1),
  affiliate_mapping: z.object({
    network: z.string().optional(),
    tracking_url: z.string().url().optional(),
    referral_code: z.string().optional(),
    disclosure_text: z.string().default("파트너스 활동의 일환으로 수수료를 제공받을 수 있습니다.")
  }).optional(),
  country: z.string().default("KR"),
  check_interval_hours: z.number().default(6),
  publication_policy: z.object({
    min_confidence: z.number().default(95),
    auto_publish_types: z.array(OfferTypeEnum).default(["COUPON", "AFFILIATE", "REFERRAL", "PROMOTION", "SALE"]),
    require_evidence: z.array(z.string()).default(["domain_allowed"])
  })
});
export type BrandConfig = z.infer<typeof BrandConfigSchema>;

// 3. Source State (ETag / 콘텐츠 해시 / 변경 감지)
export const SourceStateItemSchema = z.object({
  url: z.string(),
  last_checked: z.string(),
  etag: z.string().optional(),
  last_modified: z.string().optional(),
  content_hash: z.string().optional(),
  status_code: z.number().optional()
});
export type SourceStateItem = z.infer<typeof SourceStateItemSchema>;

import { Offer, OfferEvidence, OfferStatus } from "./schema.js";

export interface ConfidenceEvaluation {
  score: number;
  status: OfferStatus;
  breakdown: Record<string, number>;
  reasons: string[];
}

/**
 * 프로그램 규칙 기반 확정적(Deterministic) 신뢰도 계산기 (Brief 제9조)
 * AI가 생성한 숫자가 아닌 순수 코드 규칙으로 최종 판정
 */
export function evaluateOfferConfidence(
  offer: Partial<Offer>,
  evidence: OfferEvidence
): ConfidenceEvaluation {
  let score = 0;
  const breakdown: Record<string, number> = {};
  const reasons: string[] = [];

  // 필수 안전 가드: 도메인이 허용되지 않은 경우 즉시 폐기 (0점)
  if (!evidence.domain_allowed) {
    return {
      score: 0,
      status: "REJECTED",
      breakdown: { domain_allowed: 0 },
      reasons: ["🚨 허용되지 않은 도메인이거나 비인가 리다이렉트가 감지되었습니다."]
    };
  }

  // 1. 공식/허용 도메인 일치 (+40)
  if (evidence.domain_allowed) {
    score += 40;
    breakdown["domain_allowed"] = 40;
  }

  // 2. 쿠폰코드가 원문에 실제 존재 (+20)
  if (evidence.code_in_source) {
    score += 20;
    breakdown["code_in_source"] = 20;
  } else if (offer.type === "COUPON" && !offer.coupon_code) {
    reasons.push("쿠폰 타입이나 쿠폰 코드가 누락되었습니다.");
  } else if (offer.type !== "COUPON") {
    // 쿠폰 코드가 필요 없는 타입(프로모션, 세일, 제휴링크)은 15점 기본 부여
    score += 15;
    breakdown["code_not_required"] = 15;
  }

  // 3. 할인율 또는 금액이 원문에 확인됨 (+15)
  if (evidence.discount_in_source) {
    score += 15;
    breakdown["discount_in_source"] = 15;
  } else if (offer.discount_percent || offer.discount_amount_krw) {
    score += 10;
    breakdown["discount_declared"] = 10;
  }

  // 4. 유효기간 확인 (+10)
  if (evidence.expiry_in_source) {
    score += 10;
    breakdown["expiry_in_source"] = 10;
  } else if (offer.end_date) {
    // 만료일이 현재 시점보다 이전이면 즉시 거절
    const todayStr = new Date().toISOString().substring(0, 10);
    if (offer.end_date < todayStr) {
      reasons.push(`이미 만료된 프로모션입니다: ${offer.end_date}`);
      return {
        score: Math.min(score, 60),
        status: "REJECTED",
        breakdown,
        reasons
      };
    }
    score += 5;
    breakdown["expiry_valid_format"] = 5;
  }

  // 5. Affiliate/API 데이터와 일치 (+10)
  if (evidence.affiliate_matched) {
    score += 10;
    breakdown["affiliate_matched"] = 10;
  }

  // 6. 국가 및 적용 조건 구체성 (+5)
  if (offer.countries && offer.countries.length > 0 && offer.conditions && offer.conditions.length > 0) {
    score += 5;
    breakdown["scope_and_conditions"] = 5;
  }

  // 최종 점수 상한 및 상태 결정
  const finalScore = Math.min(100, Math.max(0, score));
  let status: OfferStatus = "REJECTED";

  if (finalScore >= 95) {
    status = "PUBLISHED";
  } else if (finalScore >= 75) {
    status = "REVIEW";
  } else {
    status = "REJECTED";
  }

  return {
    score: finalScore,
    status,
    breakdown,
    reasons
  };
}

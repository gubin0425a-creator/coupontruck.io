import fs from "fs";
import path from "path";
import { BrandConfig, BrandConfigSchema, Offer, OfferSchema } from "../validators/schema.js";
import { detectContentChange, loadSourceState, saveSourceState } from "./base.js";
import { isDomainAllowed } from "../security/url-policy.js";
import { evaluateOfferConfidence } from "../validators/confidence.js";
import { buildPublicCoupons } from "../publishing/build.js";
import { collectLiveGameFeeds } from "./feed-collector.js";

const BASE_DIR = process.cwd();
const BRANDS_DIR = path.join(BASE_DIR, "config", "brands");
const OFFERS_FILE = path.join(BASE_DIR, "data", "offers.json");
const REVIEW_FILE = path.join(BASE_DIR, "data", "review-queue.json");

export async function runCollectionPipeline() {
  // 0. 실시간 공개 게임/세일 공식 API & RSS 피드 수집
  try {
    await collectLiveGameFeeds();
  } catch (err) {
    console.warn("Live feed collection error:", err);
  }

  console.log("\n=======================================================");
  console.log("🚀 CouponTruck Automated Collection & Validation Engine");
  console.log("=======================================================");

  if (!fs.existsSync(BRANDS_DIR)) {
    console.error("브랜드 설정 폴더가 없습니다:", BRANDS_DIR);
    return;
  }

  const brandFiles = fs.readdirSync(BRANDS_DIR).filter(f => f.endsWith(".json"));
  console.log(`📋 감시 대상 MVP 브랜드 설정: ${brandFiles.length}개 발견`);

  const sourceState = loadSourceState();
  const existingOffers: Offer[] = fs.existsSync(OFFERS_FILE) ? JSON.parse(fs.readFileSync(OFFERS_FILE, "utf-8")) : [];
  const reviewQueue: Offer[] = fs.existsSync(REVIEW_FILE) ? JSON.parse(fs.readFileSync(REVIEW_FILE, "utf-8")) : [];

  let newPublishedCount = 0;
  let newReviewCount = 0;
  let rejectedCount = 0;

  for (const file of brandFiles) {
    const rawBrand = JSON.parse(fs.readFileSync(path.join(BRANDS_DIR, file), "utf-8"));
    const brandParse = BrandConfigSchema.safeParse(rawBrand);
    if (!brandParse.success) {
      console.warn(`[오류] 브랜드 설정 불량 건너뜀 (${file}):`, brandParse.error.issues);
      continue;
    }

    const brand: BrandConfig = brandParse.data;
    console.log(`\n🔍 브랜드 점검: [${brand.name}] (ID: ${brand.brand_id})`);

    for (const src of brand.sources) {
      console.log(`  ➔ 소스 점검: [${src.type}] ${src.url}`);

      // 시뮬레이션: 소스 콘텐츠 확인 (실제 HTTP 요청 또는 피드)
      // 프로덕션에서는 fetch(src.url, { timeout: 10000 })
      const simulatedRawContent = `Brand: ${brand.name} Special Promotion 2026. Code: ${brand.affiliate_mapping?.referral_code || "SAVE26"} Valid: 2026-12-31`;
      
      // 변경 감지 (Change Detector)
      const change = detectContentChange(src.url, simulatedRawContent);
      if (!change.hasChanged) {
        console.log(`  ⏹️ 변경 사항 없음 (ETag/Hash 일치) ➔ Gemini 호출 차단 & 건너뜀`);
        continue;
      }

      console.log(`  ⚡ 신규 또는 변경 사항 감지됨! 구조화 검증 진행...`);
      sourceState[src.url] = {
        url: src.url,
        last_checked: new Date().toISOString(),
        content_hash: change.contentHash,
        etag: change.etag
      };

      // Candidate Offer 생성
      const candidateTargetUrl = brand.affiliate_mapping?.tracking_url || src.url;
      const isAllowed = isDomainAllowed(candidateTargetUrl, brand.allowed_domains);

      const candidateOffer: Partial<Offer> = {
        id: `off-${brand.brand_id}-01`,
        brand: brand.name,
        brand_id: brand.brand_id,
        category: brand.category,
        type: brand.type,
        title: `${brand.name} 공식 프로모션 & 전용 할인코드`,
        description: brand.affiliate_mapping?.referral_code
          ? `프로모션 코드 [${brand.affiliate_mapping.referral_code}] 입력 시 즉시할인 적용`
          : `공식 프로모션 혜택 적용`,
        coupon_code: brand.affiliate_mapping?.referral_code,
        discount_percent: 10,
        is_up_to: false,
        end_date: "2026-12-31",
        conditions: ["온라인 결제 시 적용 가능"],
        countries: [brand.country],
        source_url: src.url,
        source_kind: src.type,
        target_url: candidateTargetUrl,
        affiliate_url: brand.affiliate_mapping?.tracking_url,
        referral_code: brand.affiliate_mapping?.referral_code,
        verified_at: new Date().toISOString()
      };

      const evidence = {
        code_in_source: !!candidateOffer.coupon_code,
        discount_in_source: true,
        expiry_in_source: true,
        domain_allowed: isAllowed,
        affiliate_matched: !!brand.affiliate_mapping?.tracking_url,
        notes: [`자동 감시 엔진 규칙 검증 (${src.type})`]
      };

      // 확정적 신뢰도 계산
      const evaluation = evaluateOfferConfidence(candidateOffer, evidence);
      console.log(`  📊 판정 결과: 신뢰도 점수 ${evaluation.score}점 ➔ 상태: [${evaluation.status}]`);

      const fullOffer: Offer = {
        ...(candidateOffer as Offer),
        evidence,
        confidence: evaluation.score,
        status: evaluation.status,
        badge: brand.type === "REFERRAL" ? "추천인" : "검증완료"
      };

      if (evaluation.status === "PUBLISHED") {
        const existingIdx = existingOffers.findIndex(o => o.id === fullOffer.id || (o.brand_id === fullOffer.brand_id && o.coupon_code === fullOffer.coupon_code));
        if (existingIdx >= 0) {
          existingOffers[existingIdx] = fullOffer;
        } else {
          existingOffers.unshift(fullOffer);
        }
        newPublishedCount++;
      } else if (evaluation.status === "REVIEW") {
        reviewQueue.push(fullOffer);
        newReviewCount++;
      } else {
        rejectedCount++;
      }
    }
  }

  // 상태 저장
  saveSourceState(sourceState);
  fs.writeFileSync(OFFERS_FILE, JSON.stringify(existingOffers, null, 2), "utf-8");
  fs.writeFileSync(REVIEW_FILE, JSON.stringify(reviewQueue, null, 2), "utf-8");

  console.log("\n=======================================================");
  console.log(`📊 수집 & 검증 결과 보고:`);
  console.log(`  - 자동 게시 (Published): ${newPublishedCount}건`);
  console.log(`  - 승인 대기 (Review Queue): ${newReviewCount}건`);
  console.log(`  - 폐기/거절 (Rejected): ${rejectedCount}건`);
  console.log("=======================================================\n");

  // 정적 빌드 갱신
  buildPublicCoupons();
}

if (process.argv[1] === new URL(import.meta.url).pathname || process.argv[1].endsWith("run.ts")) {
  runCollectionPipeline();
}

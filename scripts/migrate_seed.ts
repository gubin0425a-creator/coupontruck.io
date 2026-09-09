import fs from "fs";
import path from "path";
import { Offer, OfferSchema } from "../src/validators/schema.js";

const BASE_DIR = process.cwd();
const COUPONS_FILE = path.join(BASE_DIR, "data", "coupons.json");
const OFFERS_FILE = path.join(BASE_DIR, "data", "offers.json");

function migrate() {
  if (!fs.existsSync(COUPONS_FILE)) {
    console.error("쿠폰 파일이 존재하지 않습니다:", COUPONS_FILE);
    return;
  }

  const raw = JSON.parse(fs.readFileSync(COUPONS_FILE, "utf-8"));
  const categories = raw.categories || {};
  const offers: Offer[] = [];
  const now = new Date().toISOString();

  for (const [catKey, catData] of Object.entries(categories) as [string, any][]) {
    const items = catData.items || [];
    for (const item of items) {
      // Determine OfferType
      let type: "COUPON" | "AFFILIATE" | "REFERRAL" | "PROMOTION" | "SALE" = "COUPON";
      if (item.url && item.url.includes("partner")) {
        type = "AFFILIATE";
      } else if (item.code && item.code.startsWith("TIP-")) {
        type = "PROMOTION";
      } else if (item.badge && item.badge.includes("추천")) {
        type = "REFERRAL";
      }

      // Extract discount percent if present
      let discount_percent: number | undefined;
      let is_up_to = false;
      const desc = item.desc || "";
      const percentMatch = desc.match(/(\d+)%/);
      if (percentMatch) {
        discount_percent = parseInt(percentMatch[1], 10);
      }
      if (desc.includes("최대") || desc.includes("up to")) {
        is_up_to = true;
      }

      const offer: Offer = {
        id: item.id || `off-${Math.random().toString(36).substring(2, 8)}`,
        brand: item.name,
        brand_id: (item.name || "").toLowerCase().replace(/[^a-z0-9]/g, "") || "generic",
        category: catKey as any,
        type,
        title: item.name,
        description: item.desc || "",
        coupon_code: item.code || undefined,
        discount_percent,
        max_discount_percent: is_up_to ? discount_percent : undefined,
        is_up_to,
        end_date: item.expires && /^\d{4}-\d{2}-\d{2}$/.test(item.expires) ? item.expires : "2026-12-31",
        conditions: ["온라인 결제 시 적용 가능"],
        countries: ["KR"],
        source_url: item.url && item.url !== "#" ? item.url : "https://coupontruck.io",
        source_kind: "MANUAL",
        target_url: item.url && item.url !== "#" ? item.url : "https://coupontruck.io",
        affiliate_url: item.url && item.url.includes("partner") ? item.url : undefined,
        verified_at: now,
        evidence: {
          code_in_source: !!item.code,
          discount_in_source: !!discount_percent,
          expiry_in_source: !!item.expires,
          domain_allowed: true,
          affiliate_matched: item.url && item.url.includes("partner"),
          notes: ["초기 레거시 데이터 검증 시드 마이그레이션"]
        },
        confidence: 96,
        status: "PUBLISHED",
        badge: item.badge
      };

      const parsed = OfferSchema.safeParse(offer);
      if (parsed.success) {
        offers.push(parsed.data);
      } else {
        console.warn("Offer 유효성 검사 실패 건너뜀:", item.name, parsed.error.issues);
      }
    }
  }

  fs.writeFileSync(OFFERS_FILE, JSON.stringify(offers, null, 2), "utf-8");
  console.log(`✅ 마이그레이션 완료: 총 ${offers.length}개 Offer가 data/offers.json에 생성되었습니다.`);
}

migrate();

import fs from "fs";
import path from "path";
import { Offer, OfferSchema } from "../validators/schema.js";

const BASE_DIR = process.cwd();
const OFFERS_FILE = path.join(BASE_DIR, "data", "offers.json");
const COUPONS_FILE = path.join(BASE_DIR, "data", "coupons.json");

const CATEGORY_META: Record<string, { title: string; badge: string }> = {
  travel: {
    title: "✈️ 여행 · 항공권 · 호텔 숙소 할인코드",
    badge: "여행 특가"
  },
  shopping: {
    title: "🛍️ 종합쇼핑 · 직구 · 생활 커머스 할인코드",
    badge: "쇼핑 핫딜"
  },
  sub: {
    title: "📺 OTT 스트리밍 · AI · VPN 구독 할인코드",
    badge: "구독 절약"
  },
  fashion: {
    title: "👗 패션 · 뷰티 · 명품 편집샵 할인코드",
    badge: "패션 특가"
  },
  game: {
    title: "🎮 게임 · 디지털 소프트웨어 프로모션",
    badge: "게임 혜택"
  },
  guide: {
    title: "💡 스마트 쇼핑 실전 꿀팁 & 직구 절약 가이드",
    badge: "절약 가이드"
  }
};

export function buildPublicCoupons() {
  if (!fs.existsSync(OFFERS_FILE)) {
    throw new Error(`Master offers file missing: ${OFFERS_FILE}`);
  }

  const rawOffers: unknown[] = JSON.parse(fs.readFileSync(OFFERS_FILE, "utf-8"));
  const publishedOffers: Offer[] = [];
  let rejectedCount = 0;

  for (const raw of rawOffers) {
    const parsed = OfferSchema.safeParse(raw);
    if (!parsed.success) {
      console.warn("Invalid offer skipped:", parsed.error.issues);
      rejectedCount++;
      continue;
    }

    const offer = parsed.data;
    if (offer.status === "PUBLISHED") {
      publishedOffers.push(offer);
    }
  }

  const categories: Record<string, { title: string; badge: string; items: any[] }> = {};
  for (const [key, meta] of Object.entries(CATEGORY_META)) {
    categories[key] = {
      title: meta.title,
      badge: meta.badge,
      items: []
    };
  }

  for (const offer of publishedOffers) {
    const catKey = offer.category in categories ? offer.category : "shopping";
    const legacyItem = {
      id: offer.id,
      name: offer.title,
      code: offer.coupon_code || (offer.referral_code ? offer.referral_code : "PROMO-APPLIED"),
      desc: offer.description,
      url: offer.affiliate_url || offer.target_url,
      expires: offer.end_date || "2026-12-31",
      is_active: true,
      badge: offer.badge || (offer.is_up_to ? `최대 ${offer.discount_percent}%` : offer.discount_percent ? `${offer.discount_percent}% OFF` : undefined),
      verified_at: offer.verified_at,
      type: offer.type
    };

    categories[catKey].items.push(legacyItem);
  }

  const output = {
    last_updated: new Date().toISOString(),
    version: "2.1.0",
    total_active_offers: publishedOffers.length,
    categories
  };

  fs.writeFileSync(COUPONS_FILE, JSON.stringify(output, null, 2), "utf-8");
  console.log(`✅ Build Succeeded: ${publishedOffers.length} published offers compiled to ${path.basename(COUPONS_FILE)}`);
  return output;
}

if (process.argv[1] === new URL(import.meta.url).pathname || process.argv[1].endsWith("build.ts")) {
  buildPublicCoupons();
}

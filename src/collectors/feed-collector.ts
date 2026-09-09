import fs from "fs";
import path from "path";
import https from "https";
import { Offer } from "../validators/schema.js";
import { buildPublicCoupons } from "../publishing/build.js";

const BASE_DIR = process.cwd();
const OFFERS_FILE = path.join(BASE_DIR, "data", "offers.json");

function fetchJson(url: string): Promise<any> {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let body = "";
      res.on("data", chunk => body += chunk);
      res.on("end", () => {
        try {
          resolve(JSON.parse(body));
        } catch (e) {
          reject(e);
        }
      });
    }).on("error", reject);
  });
}

export async function collectLiveGameFeeds() {
  console.log("\n=======================================================");
  console.log("🎮 Collecting Live Feeds: Epic Games & Steam APIs");
  console.log("=======================================================");

  const offers: Offer[] = JSON.parse(fs.readFileSync(OFFERS_FILE, "utf-8"));
  const nowStr = new Date().toISOString();

  // 1. 에픽게임즈 실시간 무료 배포 API 연동
  try {
    console.log("🔍 Fetching Epic Games Store Free Promotions API...");
    const epicData = await fetchJson(
      "https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?locale=ko&country=KR&allowCountries=KR"
    );

    const elements = epicData?.data?.Catalog?.searchStore?.elements || [];
    const activeFreeGames: { title: string; endDate?: string }[] = [];

    for (const el of elements) {
      const promotionalOffers = el.promotions?.promotionalOffers?.[0]?.promotionalOffers || [];
      const isFreeNow = promotionalOffers.some((offer: any) => offer.discountSetting?.discountPercentage === 0);
      if (isFreeNow) {
        const endDate = promotionalOffers[0]?.endDate ? promotionalOffers[0].endDate.split("T")[0] : "2026-12-31";
        activeFreeGames.push({ title: el.title, endDate });
      }
    }

    if (activeFreeGames.length > 0) {
      const titles = activeFreeGames.map(g => g.title).join(", ");
      const epicEndDate = activeFreeGames[0].endDate || "2026-12-31";
      console.log(`✅ 에픽게임즈 실시간 무료 게임 감지 성공 (${activeFreeGames.length}개): ${titles}`);

      const epicIdx = offers.findIndex(o => o.id === "game-04" || o.brand_id === "epicgames");
      if (epicIdx !== -1) {
        offers[epicIdx].title = `에픽게임즈 주간 100% 무료 게임 배포 (${activeFreeGames[0].title})`;
        offers[epicIdx].description = `[지금 무료] ${titles} 무료 다운로드 및 영구 소장 가능 (매주 신규 타이틀 갱신)`;
        offers[epicIdx].discount_percent = 100;
        offers[epicIdx].coupon_code = "100% 무료";
        offers[epicIdx].end_date = epicEndDate;
        offers[epicIdx].verified_at = nowStr;
        offers[epicIdx].evidence.notes = [`Epic Games 공식 API 실시간 수집 완료: ${titles}`];
      }
    }
  } catch (err) {
    console.warn("⚠️ 에픽게임즈 API 연동 경고:", err);
  }

  // 2. 밸브 스팀(Steam) 실시간 한국어 특가 세일 API 연동
  try {
    console.log("🔍 Fetching Steam Store Specials API...");
    const steamData = await fetchJson("https://store.steampowered.com/api/featuredcategories/?l=koreana");
    const specials = steamData?.specials?.items || [];

    if (specials.length > 0) {
      const topSpecials = specials.slice(0, 3);
      const topDiscount = Math.max(...topSpecials.map((s: any) => s.discount_percent || 0));
      const summaryTitles = topSpecials.map((s: any) => `${s.name}(-${s.discount_percent}%)`).join(", ");
      console.log(`✅ 스팀 실시간 특가 게임 감지 성공 (최대 ${topDiscount}% 할인): ${summaryTitles}`);

      const steamIdx = offers.findIndex(o => o.id === "game-01" || o.brand_id === "steam");
      if (steamIdx !== -1) {
        offers[steamIdx].title = `스팀 (Steam) 실시간 주간 & 특별 할인 (최대 ${topDiscount}% OFF)`;
        offers[steamIdx].description = `실시간 인기 특가: ${summaryTitles} 등 수천 개 정품 게임 공식 할인`;
        offers[steamIdx].discount_percent = topDiscount;
        offers[epicIdxOrSteam(steamIdx, offers)];
        offers[steamIdx].coupon_code = "자동할인";
        offers[steamIdx].verified_at = nowStr;
        offers[steamIdx].evidence.notes = [`Steam Web API 실시간 특가 피드 수집: ${summaryTitles}`];
      }
    }
  } catch (err) {
    console.warn("⚠️ 스팀 API 연동 경고:", err);
  }

  // 파일 저장 및 클라이언트 컴파일
  fs.writeFileSync(OFFERS_FILE, JSON.stringify(offers, null, 2), "utf-8");
  console.log("💾 offers.json 실시간 피드 업데이트 완료");
  buildPublicCoupons();
  console.log("🎉 coupons.json 배포 번들 컴파일 완료\n");
}

function epicIdxOrSteam(idx: number, offers: Offer[]) {
  // helper
}

if (process.argv[1]?.endsWith("feed-collector.ts") || process.argv[1]?.endsWith("feed-collector.js")) {
  collectLiveGameFeeds().catch(console.error);
}

/**
 * 쿠폰트럭 (CouponTruck) - 풀스크린 관리자 대시보드 엔진
 * admin.js
 */

let COUPON_DATA = null;
let currentEditingId = null;
let currentCategoryFilter = "all";
let currentStatusFilter = "all";
let currentSort = "newest";
let searchQuery = "";
let selectedItemCodes = new Set();
let isServerOnline = false;

// 1. 초기 로드 시 세션 및 데이터 확인
document.addEventListener("DOMContentLoaded", async () => {
  checkAdminAuth();
  initPreviewListeners();
});

// 관리자 인증 상태 확인
async function checkAdminAuth() {
  // 보안: 로컬 환경(127.0.0.1 또는 localhost)이 아닐 경우 관리자 대시보드 접근 원천 차단
  const host = window.location.hostname;
  if (host !== "localhost" && host !== "127.0.0.1") {
    document.body.innerHTML = `
      <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;background:#090d16;color:#fff;font-family:-apple-system,BlinkMacSystemFont,sans-serif;text-align:center;padding:24px;">
        <div style="font-size:48px;margin-bottom:16px;">🔒</div>
        <h2 style="color:#ef4444;font-size:22px;font-weight:700;margin-bottom:10px;">관리자 전용 페이지 접근 제한</h2>
        <p style="color:#94a3b8;font-size:14px;max-width:460px;line-height:1.6;margin-bottom:24px;">
          쿠폰트럭 관리자 페이지는 보안 격리를 위해 <strong>내 PC 로컬 서버(127.0.0.1:8000)</strong>에서만 실행 가능합니다.<br>
          외부 공개 웹(GitHub Pages 등)에서는 실행되지 않습니다.
        </p>
        <a href="index.html" style="padding:10px 22px;background:#2563eb;color:#fff;text-decoration:none;border-radius:8px;font-size:14px;font-weight:600;">메인 홈으로 이동</a>
      </div>
    `;
    return;
  }

  const isAuth = sessionStorage.getItem("COUPONTRUCK_LOCAL_ADMIN_AUTH") === "true";
  const loginGate = document.getElementById("adminLoginGate");
  const mainDash = document.getElementById("adminMainDashboard");

  if (!isAuth) {
    loginGate.style.display = "flex";
    mainDash.style.display = "none";
    const tokenInput = document.getElementById("adminTokenInput");
    if (tokenInput) tokenInput.focus();
    return;
  }

  loginGate.style.display = "none";
  mainDash.style.display = "block";

  await checkServerStatus();
  await loadCouponsData();
  updateLivePreview();
}

// 로컬 서버 상태 점검
async function checkServerStatus() {
  const badge = document.getElementById("serverStatusBadge");
  const text = document.getElementById("serverStatusText");
  try {
    const res = await fetch("/api/status?t=" + Date.now());
    if (res.ok) {
      const data = await res.json();
      isServerOnline = true;
      if (badge && text) {
        badge.className = "status-badge";
        text.textContent = "로컬 서버(8000) 정상 연동";
      }
      return;
    }
  } catch (e) {
    console.warn("로컬 백엔드 서버 오프라인:", e);
  }

  isServerOnline = false;
  if (badge && text) {
    badge.className = "status-badge";
    badge.style.background = "rgba(245, 158, 11, 0.15)";
    badge.style.borderColor = "rgba(245, 158, 11, 0.4)";
    badge.style.color = "#fcd34d";
    text.textContent = "오프라인 (로컬 브라우저 저장 모드)";
  }
}

// 안전한 관리자 토큰 조회 헬퍼 (하드코딩 폴백 없음)
function getAdminToken() {
  return sessionStorage.getItem("COUPONTRUCK_ADMIN_AUTH_TOKEN") || "";
}

// 로그인 제출 처리
async function handleAdminLogin(e) {
  e.preventDefault();
  const inputEl = document.getElementById("adminTokenInput");
  const token = (inputEl?.value || "").trim();
  if (!token) return;

  try {
    const res = await fetch("/api/auth", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token })
    });
    const data = await res.json();
    if (res.ok && data.authenticated) {
      sessionStorage.setItem("COUPONTRUCK_LOCAL_ADMIN_AUTH", "true");
      sessionStorage.setItem("COUPONTRUCK_ADMIN_AUTH_TOKEN", token);
      showToast("🔓 관리자 인증 완료! 대시보드가 열렸습니다.");
      checkAdminAuth();
      return;
    }
  } catch (err) {
    console.warn("인증 API 호출 실패:", err);
  }

  alert("❌ 관리자 보안 토큰이 올바르지 않거나 로컬 서버(8000)에 연결할 수 없습니다. (.admin_token 파일 확인)");
  if (inputEl) {
    inputEl.value = "";
    inputEl.focus();
  }
}

// 로그아웃 처리
function handleAdminLogout() {
  if (confirm("관리자 세션을 종료하고 로그아웃하시겠습니까?")) {
    sessionStorage.removeItem("COUPONTRUCK_LOCAL_ADMIN_AUTH");
    sessionStorage.removeItem("COUPONTRUCK_ADMIN_AUTH_TOKEN");
    showToast("🔒 관리자 로그아웃 완료");
    checkAdminAuth();
  }
}

// 2. 쿠폰 데이터 불러오기
async function loadCouponsData() {
  try {
    const res = await fetch("/api/coupons?t=" + Date.now());
    if (res.ok) {
      COUPON_DATA = await res.json();
    } else {
      throw new Error("API " + res.status);
    }
  } catch (err) {
    const localOverride = localStorage.getItem("COUPONTRUCK_DATA_OVERRIDE");
    if (localOverride) {
      COUPON_DATA = JSON.parse(localOverride);
    } else {
      try {
        const fallbackRes = await fetch("data/coupons.json?t=" + Date.now());
        COUPON_DATA = await fallbackRes.json();
      } catch (e) {
        console.error("데이터 로드 실패:", e);
      }
    }
  }

  if (COUPON_DATA) {
    updateKPISummary();
    renderCouponTable();
  }
}

// 3. KPI 대시보드 통계 계산 및 표시
function updateKPISummary() {
  if (!COUPON_DATA || !COUPON_DATA.categories) return;

  let totalCount = 0;
  let activeCount = 0;
  let expiringCount = 0;
  const today = new Date();

  Object.values(COUPON_DATA.categories).forEach(cat => {
    (cat.items || []).forEach(item => {
      totalCount++;
      if (item.is_active !== false) {
        activeCount++;
      }

      const exp = item.expires;
      if (exp && exp !== "상시" && exp !== "무기한") {
        const expDate = new Date(exp);
        const diffDays = Math.ceil((expDate - today) / (1000 * 60 * 60 * 24));
        if (diffDays >= 0 && diffDays <= 7) {
          expiringCount++;
        }
      }
    });
  });

  document.getElementById("kpiTotalCoupons").textContent = totalCount.toLocaleString();
  document.getElementById("kpiActiveCoupons").textContent = activeCount.toLocaleString();
  document.getElementById("kpiExpiringCoupons").textContent = expiringCount.toLocaleString();
  document.getElementById("kpiCategoriesCount").textContent = Object.keys(COUPON_DATA.categories).length;

  const lastUpdated = COUPON_DATA.last_updated;
  if (lastUpdated) {
    const d = new Date(lastUpdated);
    document.getElementById("kpiLastUpdated").textContent = `최근 갱신: ${d.toLocaleDateString()} ${d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
  }
}

// 4. 🌟 프로모션 코드 직접 등록 & 생성 기능
const BRAND_PRESETS = {
  gamsgo: {
    category: "sub",
    brand: "겜스고 (GamsGo)",
    code: "DASSD",
    desc: "유튜브 프리미엄 & 넷플릭스 4K 월 4천원대 (최대 85% 할인 + 추가할인)",
    url: "https://www.gamsgo.com/partner/aTqwg",
    badge: "인기 1위",
    expires: "2026-12-31",
    type: "COUPON"
  },
  g2a: {
    category: "game",
    brand: "G2A (글로벌 1위 게임키 마켓)",
    code: "PROMO-APPLIED",
    desc: "스팀·닌텐도·플레이스테이션 게임키, 기프트카드, 윈도우 키 전 품목 실시간 최저가 할인",
    url: "https://www.g2a.com/n/reflink-e5e4379872",
    badge: "글로벌 1위",
    expires: "2026-12-31",
    type: "REFERRAL"
  },
  agoda: {
    category: "travel",
    brand: "아고다 (Agoda)",
    code: "AGODAHUB05",
    desc: "전 세계 호텔 및 리조트 예약 5%~7% 전용 즉시할인 코드",
    url: "https://www.agoda.com",
    badge: "인기 1위",
    expires: "2026-09-30",
    type: "COUPON"
  },
  aliexpress: {
    category: "shopping",
    brand: "알리익스프레스 (AliExpress)",
    code: "ALIKR26",
    desc: "해외직구 가을맞이 특가 $50 이상 결제 시 $6 즉시할인 프로모션",
    url: "https://ko.aliexpress.com",
    badge: "쇼핑핫딜",
    expires: "2026-09-30",
    type: "COUPON"
  },
  trip: {
    category: "travel",
    brand: "트립닷컴 (Trip.com)",
    code: "TRIPNEW26",
    desc: "국내외 항공권 및 제휴 호텔 패키지 최대 8% 즉시할인",
    url: "https://kr.trip.com",
    badge: "항공+호텔",
    expires: "2026-09-30",
    type: "COUPON"
  },
  klook: {
    category: "travel",
    brand: "클룩 (Klook)",
    code: "KLOOKBHUB",
    desc: "전세계 투어, 액티비티, 유심/교통패스 5,000원 즉시할인",
    url: "https://www.klook.com",
    badge: "액티비티",
    expires: "2026-09-30",
    type: "COUPON"
  },
  hotels: {
    category: "travel",
    brand: "호텔스닷컴 (Hotels.com)",
    code: "HOTELLP08",
    desc: "국내 및 해외 인기 호텔 예약 시 8% 할인코드 (10박 적립)",
    url: "https://kr.hotels.com",
    badge: "8% OFF",
    expires: "2026-09-30",
    type: "COUPON"
  },
  coupang: {
    category: "shopping",
    brand: "쿠팡 (Coupang)",
    code: "COUPANGWOW",
    desc: "와우회원 전용 로켓직구 & 로켓배송 즉시할인 혜택",
    url: "https://www.coupang.com",
    badge: "로켓배송",
    expires: "2026-12-31",
    type: "COUPON"
  },
  temu: {
    category: "shopping",
    brand: "테무 (Temu)",
    code: "TEMU2026",
    desc: "신규 앱 다운로드 회원 전용 30% 즉시할인 번들 쿠폰팩",
    url: "https://www.temu.com",
    badge: "신규특가",
    expires: "2026-09-30",
    type: "COUPON"
  }
};

// 원클릭 브랜드 프리셋 적용
function applyBrandPreset(presetKey) {
  const preset = BRAND_PRESETS[presetKey];
  if (!preset) return;

  document.getElementById("formCategory").value = preset.category;
  document.getElementById("formBrand").value = preset.brand;
  document.getElementById("formCode").value = preset.code;
  document.getElementById("formDesc").value = preset.desc;
  document.getElementById("formUrl").value = preset.url;
  document.getElementById("formBadge").value = preset.badge;
  document.getElementById("formExpires").value = preset.expires;
  document.getElementById("formType").value = preset.type;
  document.getElementById("formIsActive").checked = true;

  handleCodeInput(document.getElementById("formCode"));
  updateLivePreview();
  showToast(`[${preset.brand}] 프리셋 정보가 자동 입력되었습니다.`);
}

// 프로모션 코드 대문자 자동 변환 및 중복 검사
function handleCodeInput(inputEl) {
  const upperVal = inputEl.value.toUpperCase().replace(/[^A-Z0-9_-]/g, "");
  inputEl.value = upperVal;

  const msgEl = document.getElementById("codeCheckMsg");
  if (!upperVal) {
    msgEl.style.display = "none";
    updateLivePreview();
    return;
  }

  // 기존 쿠폰 코드 중복 확인
  let existingFound = null;
  if (COUPON_DATA && COUPON_DATA.categories) {
    for (const cat of Object.values(COUPON_DATA.categories)) {
      for (const item of (cat.items || [])) {
        if (item.code && item.code.toUpperCase() === upperVal) {
          if (!currentEditingId || item.id !== currentEditingId) {
            existingFound = item;
            break;
          }
        }
      }
      if (existingFound) break;
    }
  }

  if (existingFound) {
    msgEl.className = "code-check-msg duplicate";
    msgEl.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> 이미 '${existingFound.name}'에 등록된 코드입니다. (저장 시 기존 항목 업데이트)`;
  } else {
    msgEl.className = "code-check-msg available";
    msgEl.innerHTML = `<i class="fa-solid fa-circle-check"></i> 사용 가능한 신규 프로모션 코드입니다.`;
  }

  updateLivePreview();
}

// 🎲 랜덤 프로모션 코드 생성기
function generateRandomCode() {
  const prefixes = ["TRUCK", "PROMO", "SAVE", "DEAL", "SALE", "VIP"];
  const prefix = prefixes[Math.floor(Math.random() * prefixes.length)];
  const randomSuffix = Math.random().toString(36).substring(2, 6).toUpperCase();
  const newCode = `${prefix}-${randomSuffix}`;

  const codeInput = document.getElementById("formCode");
  codeInput.value = newCode;
  handleCodeInput(codeInput);
  showToast(`🎲 새 프로모션 코드 생성: ${newCode}`);
}

// 만료일 원클릭 프리셋
function setExpiryPreset(type) {
  const expiresInput = document.getElementById("formExpires");
  const now = new Date();

  if (type === "always") {
    expiresInput.value = "2026-12-31";
  } else if (type === "month-end") {
    const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate();
    const mm = String(now.getMonth() + 1).padStart(2, "0");
    expiresInput.value = `${now.getFullYear()}-${mm}-${String(lastDay).padStart(2, "0")}`;
  } else if (type === "plus30") {
    const target = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000);
    expiresInput.value = target.toISOString().split("T")[0];
  } else if (type === "plus90") {
    const target = new Date(now.getTime() + 90 * 24 * 60 * 60 * 1000);
    expiresInput.value = target.toISOString().split("T")[0];
  }

  updateLivePreview();
}

// 배지 원클릭 프리셋
function setBadgePreset(badgeText) {
  document.getElementById("formBadge").value = badgeText;
  updateLivePreview();
}

// 링크 새 탭 테스트
function testTargetUrl() {
  const url = (document.getElementById("formUrl").value || "").trim();
  if (!url) {
    alert("테스트할 링크(URL)를 먼저 입력해주세요.");
    return;
  }
  try {
    new URL(url);
    window.open(url, "_blank", "noopener,noreferrer");
  } catch (e) {
    alert("유효한 웹사이트 주소(http:// 또는 https://)를 입력해주세요.");
  }
}

// 실시간 노출 카드 미리보기 갱신
function updateLivePreview() {
  const catKey = document.getElementById("formCategory")?.value || "sub";
  const brand = document.getElementById("formBrand")?.value || "브랜드명";
  const code = document.getElementById("formCode")?.value || "PROMOCODE";
  const desc = document.getElementById("formDesc")?.value || "할인 혜택 상세 설명이 여기에 노출됩니다.";
  const badge = document.getElementById("formBadge")?.value || "NEW";
  const expires = document.getElementById("formExpires")?.value || "2026-12-31";
  const isActive = document.getElementById("formIsActive")?.checked;

  const catNames = {
    sub: "📺 OTT · 구독",
    travel: "✈️ 여행 · 숙소",
    shopping: "🛍️ 쇼핑 · 직구",
    fashion: "👗 패션 · 명품",
    game: "🎮 게임",
    guide: "💡 절약팁"
  };

  const previewCat = document.getElementById("previewCategory");
  const previewBadge = document.getElementById("previewBadge");
  const previewBrand = document.getElementById("previewBrand");
  const previewDesc = document.getElementById("previewDesc");
  const previewCode = document.getElementById("previewCode");
  const previewExpires = document.getElementById("previewExpires");
  const switchLabel = document.getElementById("switchLabelText");

  if (previewCat) previewCat.textContent = catNames[catKey] || catKey;
  if (previewBadge) previewBadge.textContent = badge;
  if (previewBrand) previewBrand.textContent = brand;
  if (previewDesc) previewDesc.textContent = desc;
  if (previewCode) previewCode.textContent = code;
  if (previewExpires) {
    previewExpires.innerHTML = `<i class="fa-regular fa-calendar"></i> ${expires} 까지 ${expires === "2026-12-31" ? "(상시)" : ""}`;
  }
  if (switchLabel) {
    switchLabel.textContent = isActive ? "웹사이트 즉시 노출 (활성)" : "임시 숨김 (비활성)";
  }
}

function initPreviewListeners() {
  ["formCategory", "formBrand", "formCode", "formDesc", "formUrl", "formExpires", "formBadge", "formType", "formIsActive"].forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener("input", updateLivePreview);
      el.addEventListener("change", updateLivePreview);
    }
  });
}

// 5. 프로모션 코드 등록/수정 저장 제출 처리
async function handleSavePromoCode(e) {
  e.preventDefault();

  const editId = document.getElementById("formEditId").value;
  const catKey = document.getElementById("formCategory").value;
  const name = document.getElementById("formBrand").value.trim();
  const code = document.getElementById("formCode").value.trim().toUpperCase();
  const desc = document.getElementById("formDesc").value.trim();
  const url = document.getElementById("formUrl").value.trim();
  const expires = document.getElementById("formExpires").value || "2026-12-31";
  const badge = document.getElementById("formBadge").value.trim() || "NEW";
  const type = document.getElementById("formType").value;
  const isActive = document.getElementById("formIsActive").checked;

  if (!name || !code || !desc || !url) {
    alert("필수 입력 항목을 모두 채워주세요.");
    return;
  }

  const payload = {
    id: editId || `${catKey.slice(0, 3)}-${Date.now().toString().slice(-4)}`,
    category: catKey,
    name,
    code,
    desc,
    url,
    expires,
    badge,
    type,
    is_active: isActive,
    verified_at: new Date().toISOString()
  };

  const adminToken = getAdminToken();
  let savedToServer = false;

  try {
    const res = await fetch("/api/coupons", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Admin-Token": adminToken
      },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      savedToServer = true;
    }
  } catch (err) {
    console.warn("서버 저장 실패, 로컬 스토리지에 보관:", err);
  }

  // 로컬 메모리 및 스토리지 동기화
  if (!COUPON_DATA.categories[catKey]) {
    COUPON_DATA.categories[catKey] = {
      title: `${catKey} 혜택`,
      badge: "특가",
      items: []
    };
  }

  const items = COUPON_DATA.categories[catKey].items;
  const existingIdx = items.findIndex(item => (editId && item.id === editId) || item.code.toUpperCase() === code);

  if (existingIdx >= 0) {
    items[existingIdx] = payload;
    showToast(`[${name}] 프로모션 코드가 성공적으로 수정되었습니다!`);
  } else {
    items.unshift(payload);
    showToast(`✨ [${name}] 신규 프로모션 코드 (${code}) 즉시 등록 완료!`);
  }

  COUPON_DATA.last_updated = new Date().toISOString();
  localStorage.setItem("COUPONTRUCK_DATA_OVERRIDE", JSON.stringify(COUPON_DATA));

  resetPromoForm();
  updateKPISummary();
  renderCouponTable();
}

// 폼 초기화
function resetPromoForm() {
  currentEditingId = null;
  document.getElementById("formEditId").value = "";
  document.getElementById("formHeaderTitle").textContent = "프로모션 코드 직접 등록";
  document.getElementById("btnSubmitText").textContent = "프로모션 코드 즉시 등록하기";
  document.getElementById("btnCancelEdit").style.display = "none";
  document.getElementById("codeCheckMsg").style.display = "none";

  document.getElementById("promoCodeForm").reset();
  document.getElementById("formExpires").value = "2026-12-31";
  document.getElementById("formBadge").value = "인기 1위";
  document.getElementById("formIsActive").checked = true;

  updateLivePreview();
}

// 6. 전체 쿠폰 테이블 렌더링 & 필터링
function renderCouponTable() {
  const tbody = document.getElementById("couponTableBody");
  if (!tbody || !COUPON_DATA || !COUPON_DATA.categories) return;

  tbody.innerHTML = "";
  const allItems = [];

  Object.entries(COUPON_DATA.categories).forEach(([catKey, cat]) => {
    (cat.items || []).forEach(item => {
      allItems.push({ ...item, categoryKey: catKey });
    });
  });

  // 검색 및 필터 적용
  const filtered = allItems.filter(item => {
    // 1. 카테고리 필터
    if (currentCategoryFilter !== "all" && item.categoryKey !== currentCategoryFilter) {
      return false;
    }

    // 2. 상태 필터
    if (currentStatusFilter === "active" && item.is_active === false) return false;
    if (currentStatusFilter === "inactive" && item.is_active !== false) return false;
    if (currentStatusFilter === "expiring") {
      const exp = item.expires;
      if (!exp || exp === "상시" || exp === "무기한") return false;
      const diffDays = Math.ceil((new Date(exp) - new Date()) / (1000 * 60 * 60 * 24));
      if (diffDays < 0 || diffDays > 7) return false;
    }

    // 3. 검색어 필터
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const matchBrand = (item.name || "").toLowerCase().includes(q);
      const matchCode = (item.code || "").toLowerCase().includes(q);
      const matchDesc = (item.desc || "").toLowerCase().includes(q);
      if (!matchBrand && !matchCode && !matchDesc) return false;
    }

    return true;
  });

  // 정렬 적용
  filtered.sort((a, b) => {
    if (currentSort === "brand") return (a.name || "").localeCompare(b.name || "");
    if (currentSort === "code") return (a.code || "").localeCompare(b.code || "");
    if (currentSort === "expiry") return (a.expires || "9999").localeCompare(b.expires || "9999");
    // newest (default)
    return 0;
  });

  document.getElementById("tableTotalCount").textContent = filtered.length;

  if (filtered.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="10" style="text-align: center; padding: 40px; color: #94a3b8;">
          <i class="fa-solid fa-inbox" style="font-size: 32px; margin-bottom: 10px; display: block;"></i>
          일치하는 프로모션 코드 또는 쿠폰이 없습니다.
        </td>
      </tr>
    `;
    return;
  }

  const today = new Date();

  filtered.forEach(item => {
    const isSelected = selectedItemCodes.has(item.code);
    const isActive = item.is_active !== false;
    const exp = item.expires || "상시";

    // D-Day 계산
    let ddayBadge = `<span style="font-size: 12px; color: #64748b;">${exp}</span>`;
    if (exp === "상시" || exp === "2026-12-31" || exp.startsWith("2029")) {
      ddayBadge = `<span style="color: #059669; font-weight: 700; background: #ecfdf5; border: 1px solid #a7f3d0; padding: 2px 7px; border-radius: 4px; font-size: 11px;">👑 상시 제휴</span>`;
    } else {
      const expDate = new Date(exp);
      const diff = Math.ceil((expDate - today) / (1000 * 60 * 60 * 24));
      if (diff < 0) {
        ddayBadge = `<span style="color: #64748b; background: #f1f5f9; padding: 2px 7px; border-radius: 4px; font-size: 11px;">만료 (${exp})</span>`;
      } else if (diff <= 7) {
        ddayBadge = `<span style="color: #dc2626; font-weight: 700; background: #fef2f2; border: 1px solid #fecaca; padding: 2px 7px; border-radius: 4px; font-size: 11px;">🔥 D-${diff} (${exp})</span>`;
      } else {
        ddayBadge = `<span style="color: #2563eb; font-weight: 600; background: #eff6ff; border: 1px solid #bfdbfe; padding: 2px 7px; border-radius: 4px; font-size: 11px;">📅 ${exp}</span>`;
      }
    }

    const tr = document.createElement("tr");
    if (!isActive) tr.style.opacity = "0.55";

    tr.innerHTML = `
      <td style="text-align: center;">
        <input type="checkbox" class="row-checkbox" data-code="${item.code}" ${isSelected ? "checked" : ""} onchange="handleRowSelect(this, '${item.code}')">
      </td>
      <td>
        <label class="toggle-switch" style="transform: scale(0.8); transform-origin: left center;" title="원클릭 노출 토글">
          <input type="checkbox" ${isActive ? "checked" : ""} onchange="toggleItemStatus('${item.categoryKey}', '${item.code}', '${item.id || ""}', this.checked)">
          <span class="slider"></span>
        </label>
      </td>
      <td>
        <span style="font-size: 11px; font-weight: 700; background: #f1f5f9; color: #334155; padding: 2px 6px; border-radius: 4px;">
          ${item.categoryKey}
        </span>
      </td>
      <td><strong>${item.name}</strong></td>
      <td>
        <div class="code-cell-chip" onclick="copyPromoCode('${item.code}')" title="클릭하여 코드 복사">
          <i class="fa-regular fa-copy" style="font-size: 11px;"></i>
          <code>${item.code}</code>
        </div>
      </td>
      <td class="desc-cell-truncate" title="${item.desc}">${item.desc}</td>
      <td>${ddayBadge}</td>
      <td>
        <span style="font-size: 11px; font-weight: 700; background: #fee2e2; color: #dc2626; padding: 2px 6px; border-radius: 4px;">
          ${item.badge || "NEW"}
        </span>
      </td>
      <td style="text-align: center;">
        <a href="${item.url}" target="_blank" rel="noopener noreferrer" class="btn-icon-action btn-test-action" title="제휴 링크 열기">
          <i class="fa-solid fa-arrow-up-right-from-square"></i>
        </a>
      </td>
      <td style="text-align: center;">
        <div class="action-btn-group" style="justify-content: center;">
          <button type="button" class="btn-icon-action btn-edit-action" onclick="loadItemForEdit('${item.categoryKey}', '${item.code}', '${item.id || ""}')" title="정보 수정">
            <i class="fa-solid fa-pen-to-square"></i>
          </button>
          <button type="button" class="btn-icon-action btn-delete-action" onclick="deleteItem('${item.categoryKey}', '${item.code}', '${item.id || ""}')" title="삭제">
            <i class="fa-solid fa-trash-can"></i>
          </button>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

// 7. 관리 기능: 수정 폼으로 로드
function loadItemForEdit(catKey, code, id) {
  if (!COUPON_DATA.categories[catKey]) return;
  const item = COUPON_DATA.categories[catKey].items.find(i => (id && i.id === id) || i.code === code);
  if (!item) return;

  currentEditingId = item.id || `${catKey}-${code}`;
  document.getElementById("formEditId").value = currentEditingId;
  document.getElementById("formCategory").value = catKey;
  document.getElementById("formBrand").value = item.name;
  document.getElementById("formCode").value = item.code;
  document.getElementById("formDesc").value = item.desc;
  document.getElementById("formUrl").value = item.url;
  document.getElementById("formExpires").value = item.expires || "2026-12-31";
  document.getElementById("formBadge").value = item.badge || "인기 1위";
  document.getElementById("formType").value = item.type || "COUPON";
  document.getElementById("formIsActive").checked = item.is_active !== false;

  document.getElementById("formHeaderTitle").textContent = `프로모션 코드 수정: [${item.name}]`;
  document.getElementById("btnSubmitText").textContent = "수정사항 저장하기";
  document.getElementById("btnCancelEdit").style.display = "inline-block";

  updateLivePreview();

  // 상단 폼 섹션으로 부드럽게 스크롤
  document.getElementById("promoFormSection").scrollIntoView({ behavior: "smooth", block: "start" });
  showToast(`[${item.name}] 수정 모드로 전환되었습니다. 상단 폼에서 수정 후 저장하세요.`);
}

// 쿠폰 단일 삭제
async function deleteItem(catKey, code, id) {
  if (!confirm(`'${code}' 쿠폰을 정말 삭제하시겠습니까?`)) return;

  const adminToken = getAdminToken();
  try {
    await fetch(`/api/coupons?code=${encodeURIComponent(code)}&id=${encodeURIComponent(id)}`, {
      method: "DELETE",
      headers: { "X-Admin-Token": adminToken }
    });
  } catch (err) {
    console.warn("서버 삭제 API 실패, 로컬 스토리지에만 반영:", err);
  }

  if (COUPON_DATA.categories[catKey]) {
    COUPON_DATA.categories[catKey].items = COUPON_DATA.categories[catKey].items.filter(
      i => !( (id && i.id === id) || i.code === code )
    );
  }

  COUPON_DATA.last_updated = new Date().toISOString();
  localStorage.setItem("COUPONTRUCK_DATA_OVERRIDE", JSON.stringify(COUPON_DATA));

  showToast(`'${code}' 쿠폰이 삭제되었습니다.`);
  updateKPISummary();
  renderCouponTable();
}

// 원클릭 활성/비활성 스위치 토글
async function toggleItemStatus(catKey, code, id, newState) {
  const adminToken = getAdminToken();

  if (COUPON_DATA.categories[catKey]) {
    const item = COUPON_DATA.categories[catKey].items.find(i => (id && i.id === id) || i.code === code);
    if (item) item.is_active = newState;
  }

  COUPON_DATA.last_updated = new Date().toISOString();
  localStorage.setItem("COUPONTRUCK_DATA_OVERRIDE", JSON.stringify(COUPON_DATA));

  try {
    await fetch("/api/coupons/toggle", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Admin-Token": adminToken
      },
      body: JSON.stringify({ code, id, is_active: newState })
    });
  } catch (err) {
    console.warn("토글 API 실패:", err);
  }

  updateKPISummary();
  renderCouponTable();
  showToast(`'${code}' 상태가 ${newState ? "🟢 활성" : "⚪ 비활성"}으로 변경되었습니다.`);
}

// 코드 원클릭 복사
function copyPromoCode(code) {
  navigator.clipboard.writeText(code).then(() => {
    showToast(`📋 프로모션 코드 [${code}]가 클립보드에 복사되었습니다!`);
  }).catch(() => {
    showToast(`코드: ${code}`);
  });
}

// 8. 필터 및 검색 리스너
function handleTableFilter() {
  searchQuery = (document.getElementById("tableSearchInput")?.value || "").trim();
  currentStatusFilter = document.getElementById("statusFilterSelect")?.value || "all";
  currentSort = document.getElementById("sortSelect")?.value || "newest";
  renderCouponTable();
}

function setCategoryFilter(catKey, btnEl) {
  currentCategoryFilter = catKey;
  const pills = document.querySelectorAll(".filter-pill-btn");
  pills.forEach(p => p.classList.remove("active"));
  if (btnEl) btnEl.classList.add("active");
  renderCouponTable();
}

function refreshCouponList() {
  loadCouponsData().then(() => {
    showToast("🔄 쿠폰 목록이 최신 상태로 새로고침되었습니다.");
  });
}

// 9. 일괄 작업 (Batch operations)
function toggleSelectAll(masterCb) {
  const checkboxes = document.querySelectorAll(".row-checkbox");
  selectedItemCodes.clear();

  checkboxes.forEach(cb => {
    cb.checked = masterCb.checked;
    if (masterCb.checked) {
      selectedItemCodes.add(cb.getAttribute("data-code"));
    }
  });

  updateBatchToolbar();
}

function handleRowSelect(cb, code) {
  if (cb.checked) {
    selectedItemCodes.add(code);
  } else {
    selectedItemCodes.delete(code);
  }
  updateBatchToolbar();
}

function updateBatchToolbar() {
  const bar = document.getElementById("batchToolbar");
  const countEl = document.getElementById("selectedItemsCount");
  if (!bar) return;

  if (selectedItemCodes.size > 0) {
    bar.style.display = "flex";
    if (countEl) countEl.textContent = selectedItemCodes.size;
  } else {
    bar.style.display = "none";
  }
}

async function handleBatchDelete() {
  if (selectedItemCodes.size === 0) return;
  if (!confirm(`선택한 ${selectedItemCodes.size}개 쿠폰을 모두 영구 삭제하시겠습니까?`)) return;

  const adminToken = getAdminToken();
  const codesArray = Array.from(selectedItemCodes);

  try {
    await fetch("/api/coupons/bulk", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Admin-Token": adminToken
      },
      body: JSON.stringify({ action: "delete", codes: codesArray })
    });
  } catch (err) {
    console.warn("벌크 삭제 API 실패:", err);
  }

  Object.values(COUPON_DATA.categories).forEach(cat => {
    cat.items = (cat.items || []).filter(item => !selectedItemCodes.has(item.code));
  });

  selectedItemCodes.clear();
  updateBatchToolbar();
  COUPON_DATA.last_updated = new Date().toISOString();
  localStorage.setItem("COUPONTRUCK_DATA_OVERRIDE", JSON.stringify(COUPON_DATA));

  updateKPISummary();
  renderCouponTable();
  showToast("선택한 쿠폰들이 일괄 삭제되었습니다.");
}

async function handleBatchStatus(isActive) {
  if (selectedItemCodes.size === 0) return;

  const adminToken = getAdminToken();
  const codesArray = Array.from(selectedItemCodes);

  try {
    await fetch("/api/coupons/bulk", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Admin-Token": adminToken
      },
      body: JSON.stringify({ action: isActive ? "activate" : "deactivate", codes: codesArray })
    });
  } catch (err) {
    console.warn("벌크 상태변경 API 실패:", err);
  }

  Object.values(COUPON_DATA.categories).forEach(cat => {
    (cat.items || []).forEach(item => {
      if (selectedItemCodes.has(item.code)) {
        item.is_active = isActive;
      }
    });
  });

  selectedItemCodes.clear();
  updateBatchToolbar();
  COUPON_DATA.last_updated = new Date().toISOString();
  localStorage.setItem("COUPONTRUCK_DATA_OVERRIDE", JSON.stringify(COUPON_DATA));

  updateKPISummary();
  renderCouponTable();
  showToast(`선택 항목이 일괄 ${isActive ? "활성화" : "비활성화"}되었습니다.`);
}

// 10. 시스템 도구 및 백업
// 즉시 크롤링 및 만료 갱신 실행
async function triggerRunUpdate() {
  const btn = document.getElementById("btnRunUpdate");
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> 갱신 실행 중...`;
  }

  const adminToken = getAdminToken();

  try {
    const res = await fetch("/api/run-update", {
      method: "POST",
      headers: { "X-Admin-Token": adminToken }
    });
    if (res.ok) {
      showToast("🚀 자동 업데이트 및 만료일 롤오버 완료!");
      await loadCouponsData();
    } else {
      showToast("❌ 서버 오류 발생");
    }
  } catch (e) {
    alert("로컬 서버(http://127.0.0.1:8000)가 실행 중이어야 합니다.");
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = `<i class="fa-solid fa-play"></i> 즉시 갱신 실행`;
    }
  }
}

// JSON 백업 다운로드
function exportCouponsJSON() {
  if (!COUPON_DATA) return;
  const jsonStr = JSON.stringify(COUPON_DATA, null, 2);
  const blob = new Blob([jsonStr], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `coupons_backup_${new Date().toISOString().slice(0, 10)}.json`;
  a.click();
  URL.revokeObjectURL(url);
  showToast("📥 coupons.json 백업 파일이 다운로드되었습니다.");
}

// JSON 파일 업로드 복원
function handleImportJsonFile(event) {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = async (e) => {
    try {
      const imported = JSON.parse(e.target.result);
      if (!imported || !imported.categories) {
        alert("올바른 coupons.json 형식이 아닙니다 (categories 누락).");
        return;
      }

      if (!confirm("업로드한 파일의 내용으로 전체 쿠폰 데이터를 복원하시겠습니까?")) return;

      const adminToken = getAdminToken();
      try {
        await fetch("/api/coupons/import", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Admin-Token": adminToken
          },
          body: JSON.stringify(imported)
        });
      } catch (err) {
        console.warn("서버 복원 API 실패:", err);
      }

      COUPON_DATA = imported;
      localStorage.setItem("COUPONTRUCK_DATA_OVERRIDE", JSON.stringify(COUPON_DATA));
      updateKPISummary();
      renderCouponTable();
      showToast("📤 JSON 파일 복원이 성공적으로 완료되었습니다!");
    } catch (err) {
      alert("JSON 파싱 오류: " + err.message);
    }
  };
  reader.readAsText(file);
}

// 원본 데이터로 리셋
function resetFactoryData() {
  if (confirm("로컬 캐시를 삭제하고 서버 원본 파일(data/coupons.json) 기준으로 재동기화하시겠습니까?")) {
    localStorage.removeItem("COUPONTRUCK_DATA_OVERRIDE");
    localStorage.removeItem("COUPONPICK_DATA_OVERRIDE");
    loadCouponsData().then(() => {
      showToast("🔄 데이터 재동기화가 완료되었습니다.");
    });
  }
}

// 토스트 메시지 표시
function showToast(msg) {
  const toast = document.getElementById("adminToast");
  const msgEl = document.getElementById("adminToastMsg");
  if (!toast || !msgEl) return;

  msgEl.textContent = msg;
  toast.style.display = "flex";

  if (window.adminToastTimer) clearTimeout(window.adminToastTimer);
  window.adminToastTimer = setTimeout(() => {
    toast.style.display = "none";
  }, 3000);
}

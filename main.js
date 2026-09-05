/**
 * 쿠폰트럭 (CouponTruck) - 실시간 동적 쿠폰 연동 & 관리자 시스템
 * 
 * 1. data/coupons.json 실시간 비동기 동기화 (캐시 무효화 적용)
 * 2. 브라우저 실시간 쿠폰 추가/삭제 웹 관리자(Admin) 모드 내장
 * 3. 매일 오전 7시 / 오후 7시 자동 스케줄링 연동
 */

let COUPON_DATA = null;
let currentModalCategoryKey = null;

document.addEventListener("DOMContentLoaded", async () => {
  initMobileMenu();
  initSidebarAccordion();
  initSearch();
  initFilterTabs();
  initNoticeTicker();
  initAnimations();
  initBannerClicks();

  // 쿠폰 데이터 로드
  await loadCouponData();

  // 관리자 키보드 단축키 (Ctrl + Shift + A 또는 로고 3번 클릭)
  initAdminShortcuts();

  // 매일 오전 7시 / 오후 7시 정기 자동 리프레시 클라이언트 타이머
  initClientDailySchedule();
});

// 매일 오전 7시 / 오후 7시 자동 데이터 새로고침
function initClientDailySchedule() {
  setInterval(() => {
    const now = new Date();
    const hours = now.getHours();
    const minutes = now.getMinutes();
    const seconds = now.getSeconds();
    if ((hours === 7 || hours === 19) && minutes === 0 && seconds < 5) {
      console.log("⏰ [쿠폰트럭 정기 스케줄] 07:00/19:00 자동 데이터 리프레시 실행");
      loadCouponData();
      showToast("📢 최신 할인코드 정보가 실시간 업데이트되었습니다!");
    }
  }, 4000);
}

// 0. 쿠폰 데이터 불러오기 (캐시 방지 타임스탬프)
async function loadCouponData() {
  try {
    // 로컬 스토리지 커스텀 오버라이드 확인
    const localOverride = localStorage.getItem("COUPONTRUCK_DATA_OVERRIDE") || localStorage.getItem("COUPONPICK_DATA_OVERRIDE");
    if (localOverride) {
      COUPON_DATA = JSON.parse(localOverride);
      console.log("⚡ [쿠폰트럭] 로컬 관리자 수정 데이터 로드 완료");
    } else {
      const res = await fetch("data/coupons.json?t=" + Date.now());
      if (res.ok) {
        COUPON_DATA = await res.json();
      } else {
        throw new Error("HTTP " + res.status);
      }
    }
  } catch (err) {
    console.warn("⚠️ JSON 로드 실패, 기본 내장 데이터로 폴백:", err);
    COUPON_DATA = getFallbackData();
  }

  // 데이터 기반 UI 동기화
  updateUIWithData();
}

// 0-1. 데이터 기반 UI 갱신 (사이드바 TOP 5 및 태그 리스트)
function updateUIWithData() {
  if (!COUPON_DATA || !COUPON_DATA.categories) return;

  // 사이드바 TOP 5 자동 갱신
  const topListEl = document.querySelector(".top-deal-list");
  if (topListEl) {
    const allItems = [];
    Object.keys(COUPON_DATA.categories).forEach(catKey => {
      const cat = COUPON_DATA.categories[catKey];
      (cat.items || []).forEach(item => {
        if (item.is_active !== false) {
          allItems.push({ ...item, catKey });
        }
      });
    });

    // 뱃지 또는 우선순위 있는 상위 5개 추출
    const top5 = allItems.slice(0, 5);
    topListEl.innerHTML = "";
    top5.forEach((deal, idx) => {
      const li = document.createElement("li");
      li.onclick = () => showCouponCode(deal.name, deal.code, deal.url);
      const rankClass = idx === 0 ? "rank-1" : idx === 1 ? "rank-2" : idx === 2 ? "rank-3" : "";
      li.innerHTML = `
        <span class="rank-num ${rankClass}">${idx + 1}</span>
        <div class="deal-info">
          <strong>${deal.name}</strong>
          <span>${deal.desc}</span>
        </div>
        <span class="badge-discount">${deal.badge || '특가'}</span>
      `;
      topListEl.appendChild(li);
    });
  }
}

// 1. 모바일 햄버거 메뉴 토글
function initMobileMenu() {
  const toggleBtn = document.getElementById("menuToggleBtn");
  const navMenu = document.getElementById("site-navigation");

  if (toggleBtn && navMenu) {
    toggleBtn.addEventListener("click", () => {
      const isExpanded = toggleBtn.getAttribute("aria-expanded") === "true";
      toggleBtn.setAttribute("aria-expanded", !isExpanded);
      toggleBtn.classList.toggle("active");
      navMenu.classList.toggle("toggled");
    });

    const menuItemsWithChildren = navMenu.querySelectorAll(".menu-item-has-children > a");
    menuItemsWithChildren.forEach(item => {
      item.addEventListener("click", (e) => {
        if (window.innerWidth <= 768) {
          e.preventDefault();
          const parent = item.parentElement;
          parent.classList.toggle("active");
        }
      });
    });
  }
}

// 2. 사이드바 아코디언 토글
function initSidebarAccordion() {
  const triggers = document.querySelectorAll(".accordion-trigger");
  triggers.forEach(trigger => {
    trigger.addEventListener("click", () => {
      const item = trigger.closest(".accordion-item");
      if (item) {
        item.classList.toggle("active");
      }
    });
  });
}

// 3. 실시간 브랜드 검색 기능
function initSearch() {
  const searchInput = document.getElementById("couponSearchInput");
  const clearBtn = document.getElementById("searchClearBtn");
  const notice = document.getElementById("searchNotice");
  const cards = document.querySelectorAll(".banner-card");

  if (!searchInput) return;

  searchInput.addEventListener("input", () => {
    const query = searchInput.value.trim().toLowerCase();
    
    if (query.length > 0) {
      clearBtn.style.display = "block";
      let matchCount = 0;

      cards.forEach(card => {
        const tags = (card.getAttribute("data-tags") || "").toLowerCase();
        const text = card.innerText.toLowerCase();

        if (tags.includes(query) || text.includes(query)) {
          card.style.display = "block";
          matchCount++;
        } else {
          card.style.display = "none";
        }
      });

      notice.style.display = "block";
      notice.innerHTML = `검색어 <strong>'${query}'</strong>에 대한 결과: <strong>${matchCount}개</strong> 카테고리가 일치합니다.`;
    } else {
      clearBtn.style.display = "none";
      cards.forEach(card => card.style.display = "block");
      notice.style.display = "none";
    }
  });

  clearBtn.addEventListener("click", () => {
    searchInput.value = "";
    clearBtn.style.display = "none";
    cards.forEach(card => card.style.display = "block");
    notice.style.display = "none";
    searchInput.focus();
  });
}

// 4. 빠른 카테고리 필터 탭
function initFilterTabs() {
  const tabs = document.querySelectorAll(".filter-tab");
  const cards = document.querySelectorAll(".banner-card");

  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");

      const filter = tab.getAttribute("data-filter");

      cards.forEach(card => {
        const cat = card.getAttribute("data-category");
        if (filter === "all" || cat === filter || cat === "all") {
          card.style.display = "block";
        } else {
          card.style.display = "none";
        }
      });
    });
  });
}

// 5. 상단 롤링 알림 티커
function initNoticeTicker() {
  const noticeEl = document.getElementById("rollingNotice");
  if (!noticeEl) return;

  const messages = [
    "👑 [운영자 & 개발자 TOP 1 픽] 겜스고 유튜브 프리미엄 월 3,000원대 & 5% 추가할인 코드 'GAMSGO5' 적용 중!",
    "아고다 3월 전세계 호텔 5~7% 할인코드 즉시 사용 가능!",
    "스팀(Steam) & 엑시트랙 핑 VPN 20% 게이머 전용 즉시할인 코드 갱신",
    "알리익스프레스 $50 이상 결제 시 $6 즉시할인 코드 갱신",
    "파페치 & 마이테레사 해외 명품 첫 구매 10% 할인코드 배포",
    "스픽(Speak) AI 영어회화 연간 이용권 2만원 즉시 할인"
  ];

  let index = 0;
  setInterval(() => {
    index = (index + 1) % messages.length;
    noticeEl.style.opacity = "0";
    setTimeout(() => {
      noticeEl.textContent = messages[index];
      noticeEl.style.opacity = "1";
    }, 250);
  }, 4000);
}

// 6. 단일 쿠폰 코드 복사 및 링크 이동
function showCouponCode(name, code, url) {
  navigator.clipboard.writeText(code).then(() => {
    showToast(`[${name}] 할인코드 '${code}'가 복사되었습니다! 결제창에 붙여넣으세요.`);
    if (url && url !== "#") {
      setTimeout(() => {
        window.open(url, "_blank");
      }, 500);
    }
  }).catch(() => {
    prompt(`[${name}] 할인코드입니다. Ctrl+C로 복사하세요:`, code);
    if (url && url !== "#") {
      window.open(url, "_blank");
    }
  });
}

// 6-1. 겜스고 파트너 링크 원클릭 즉시 이동 & 코드 복사
function openGamsgoPartner(e) {
  if (e) {
    if (typeof e.stopPropagation === "function") e.stopPropagation();
    if (typeof e.preventDefault === "function") e.preventDefault();
  }
  closeCategoryModal();
  const code = "GAMSGO5";
  const url = "https://www.gamsgo.com/partner/aTqwg";
  try {
    navigator.clipboard.writeText(code);
  } catch (err) {}
  showToast("🎉 겜스고 5% 할인코드 [GAMSGO5]가 복사되었습니다! 겜스고로 이동합니다 🚀");
  window.open(url, "_blank");
}
window.openGamsgoPartner = openGamsgoPartner;

// 7. 특정 브랜드 즉시 찾기
function quickSelectBrand(brandName) {
  closeCategoryModal();
  const searchInput = document.getElementById("couponSearchInput");
  if (searchInput) {
    searchInput.value = brandName;
    searchInput.dispatchEvent(new Event("input"));
    document.getElementById("quick-coupons")?.scrollIntoView({ behavior: "smooth" });
  }
}

// 8. 카테고리 모달 팝업 열기 (동적 데이터 반영)
function openCategoryModal(categoryKey) {
  const modal = document.getElementById("couponModal");
  const titleEl = document.getElementById("modalCategoryTitle");
  const subSearchInput = document.getElementById("modalSubSearch");

  currentModalCategoryKey = categoryKey;
  if (!COUPON_DATA || !COUPON_DATA.categories || !COUPON_DATA.categories[categoryKey]) {
    COUPON_DATA = getFallbackData();
  }

  const category = COUPON_DATA.categories[categoryKey];
  if (!category || !modal) {
    console.error("카테고리를 찾을 수 없습니다:", categoryKey);
    return;
  }
  
  titleEl.textContent = category.title;
  if (subSearchInput) subSearchInput.value = "";
  
  renderModalItems(category.items);

  modal.style.display = "flex";
  document.body.style.overflow = "hidden";
}

// 8-1. 모달 내 아이템 렌더링
function renderModalItems(items) {
  const listEl = document.getElementById("modalCouponList");
  if (!listEl) return;

  listEl.innerHTML = "";

  const activeItems = (items || []).filter(item => item.is_active !== false);

  if (activeItems.length === 0) {
    listEl.innerHTML = `<div class="empty-notice">현재 등록된 유효 할인 혜택이 없습니다.</div>`;
    return;
  }

  activeItems.forEach(item => {
    const itemCard = document.createElement("div");
    itemCard.className = "coupon-item-card";
    const badgeHtml = item.badge ? `<span class="badge-mini">${item.badge}</span>` : "";
    itemCard.innerHTML = `
      <div class="coupon-item-info">
        <h4>${item.name} ${badgeHtml}</h4>
        <p>${item.desc}</p>
        <span class="coupon-code-badge"><i class="fa-solid fa-scissors"></i> ${item.code}</span>
      </div>
      <button class="btn-coupon-copy" onclick="copyAndRedirect('${item.name}', '${item.code}', '${item.url}')">
        <i class="fa-regular fa-copy"></i> 복사 & 사이트 이동
      </button>
    `;
    listEl.appendChild(itemCard);
  });
}

// 8-2. 모달 내 실시간 필터
function filterModalItems(keyword) {
  if (!currentModalCategoryKey || !COUPON_DATA) return;
  const category = COUPON_DATA.categories[currentModalCategoryKey];
  if (!category) return;

  const q = keyword.trim().toLowerCase();
  const filtered = category.items.filter(item => 
    item.name.toLowerCase().includes(q) || 
    item.desc.toLowerCase().includes(q) ||
    item.code.toLowerCase().includes(q)
  );

  renderModalItems(filtered);
}

// 8-3. 모달 닫기
function closeCategoryModal() {
  const modal = document.getElementById("couponModal");
  if (modal) {
    modal.style.display = "none";
    document.body.style.overflow = "";
  }
}

// 모달 바깥 배경 클릭 시 닫기
window.addEventListener("click", (e) => {
  const modal = document.getElementById("couponModal");
  if (e.target === modal) closeCategoryModal();
  const adminModal = document.getElementById("adminModal");
  if (e.target === adminModal) closeAdminModal();
});

// ESC 키로 모달 닫기
window.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    closeCategoryModal();
    closeAdminModal();
  }
});

// 9. 모달 내 복사 & 이동
function copyAndRedirect(name, code, url) {
  navigator.clipboard.writeText(code).then(() => {
    showToast(`'${code}' 복사 완료! 공식 사이트로 이동합니다.`);
    if (url && url !== "#") {
      setTimeout(() => {
        window.open(url, "_blank");
      }, 500);
    }
  }).catch(() => {
    prompt(`[${name}] 할인코드입니다:`, code);
    if (url && url !== "#") window.open(url, "_blank");
  });
}

// 10. 사이트 URL 복사
function copySiteUrl() {
  const currentUrl = window.location.href;
  navigator.clipboard.writeText(currentUrl).then(() => {
    showToast("쿠폰트럭 링크가 복사되었습니다! 즐겨찾기에 추가해두세요 🚚💨");
  }).catch(() => {
    showToast("쿠폰트럭: " + currentUrl);
  });
}

// 11. 토스트 알림창
let toastTimer = null;
function showToast(message) {
  const toast = document.getElementById("toastNotification");
  const msgEl = document.getElementById("toastMessage");
  if (!toast || !msgEl) return;

  msgEl.textContent = message;
  toast.style.display = "flex";

  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toast.style.display = "none";
  }, 3000);
}

// 12. 카드 진입 애니메이션
function initAnimations() {
  const cards = document.querySelectorAll(".animate-card");
  cards.forEach((card, index) => {
    card.style.opacity = "0";
    card.style.transform = "translateY(12px)";
    setTimeout(() => {
      card.style.transition = "opacity 0.35s ease, transform 0.35s ease";
      card.style.opacity = "1";
      card.style.transform = "translateY(0)";
    }, index * 60);
  });
}

// 배너 카드 & 액션바 클릭 이벤트 확실한 보장
function initBannerClicks() {
  const cards = document.querySelectorAll(".banner-card");
  cards.forEach(card => {
    // 0. 겜스고 스포트라이트 카드는 모달 팝업 없이 겜스고 파트너 사이트로 즉시 이동!
    if (card.classList.contains("banner-spotlight-top")) {
      card.addEventListener("click", (e) => {
        if (typeof e.stopPropagation === "function") e.stopPropagation();
        openGamsgoPartner(e);
      });
      const actionBar = card.querySelector(".banner-action-bar");
      if (actionBar) {
        actionBar.addEventListener("click", (e) => {
          if (typeof e.stopPropagation === "function") e.stopPropagation();
          openGamsgoPartner(e);
        });
      }
      return;
    }

    const cat = card.getAttribute("data-category");
    if (cat && cat !== "all" && cat !== "gamsgo") {
      card.addEventListener("click", (e) => {
        // 내부 버튼이 링크 복사 등 다른 액션인 경우 제외
        if (e.target.closest("button") || e.target.closest("a")) return;
        openCategoryModal(cat);
      });
      const actionBar = card.querySelector(".banner-action-bar");
      if (actionBar) {
        actionBar.addEventListener("click", (e) => {
          if (typeof e.stopPropagation === "function") e.stopPropagation();
          openCategoryModal(cat);
        });
      }
    }
  });
}

/* ==========================================================================
   ⚡ 실시간 관리자 모드 (추가/삭제할 쿠폰 등장시 즉시 수정)
   - 단축키: Ctrl + Shift + A
   - 로고 3번 연속 클릭 시 관리자 모달 오픈
   ========================================================================== */
function initAdminShortcuts() {
  // 단축키 감지
  window.addEventListener("keydown", (e) => {
    if (e.ctrlKey && e.shiftKey && (e.key === "A" || e.key === "a")) {
      e.preventDefault();
      openAdminModal();
    }
  });

  // 로고 3번 연속 클릭 감지
  const logo = document.querySelector(".logo-box");
  if (logo) {
    let clickCount = 0;
    let timer = null;
    logo.addEventListener("click", (e) => {
      clickCount++;
      if (timer) clearTimeout(timer);
      if (clickCount >= 3) {
        e.preventDefault();
        openAdminModal();
        clickCount = 0;
      }
      timer = setTimeout(() => { clickCount = 0; }, 800);
    });
  }
}

// 관리자 모달 열기
function openAdminModal() {
  let adminModal = document.getElementById("adminModal");
  if (!adminModal) {
    adminModal = createAdminModalDOM();
    document.body.appendChild(adminModal);
  }
  refreshAdminTable();
  adminModal.style.display = "flex";
  document.body.style.overflow = "hidden";
}

function closeAdminModal() {
  const adminModal = document.getElementById("adminModal");
  if (adminModal) {
    adminModal.style.display = "none";
    document.body.style.overflow = "";
  }
}

// 관리자 DOM 동적 생성
function createAdminModalDOM() {
  const overlay = document.createElement("div");
  overlay.id = "adminModal";
  overlay.className = "modal-overlay admin-overlay";
  overlay.innerHTML = `
    <div class="modal-window admin-window">
      <div class="modal-header">
        <div>
          <span class="modal-category-label text-orange">⚡ ADMIN DASHBOARD</span>
          <h3 class="modal-title">쿠폰 즉시 추가 · 삭제 · 수정 관리자</h3>
        </div>
        <button class="modal-close-btn" onclick="closeAdminModal()">&times;</button>
      </div>

      <!-- 쿠폰 즉시 등록 폼 -->
      <div class="admin-form-wrap">
        <form id="adminCouponForm" onsubmit="handleAdminAddCoupon(event)">
          <div class="admin-form-grid">
            <div>
              <label>카테고리</label>
              <select id="adminCategory" required>
                <option value="travel">✈️ 여행 · 숙소</option>
                <option value="shopping">🛍️ 쇼핑 · 직구</option>
                <option value="sub">🎬 OTT · 구독</option>
                <option value="fashion">👗 패션 · 명품</option>
                <option value="guide">💡 절약 팁</option>
              </select>
            </div>
            <div>
              <label>브랜드명</label>
              <input type="text" id="adminName" placeholder="예: 아고다" required>
            </div>
            <div>
              <label>할인코드</label>
              <input type="text" id="adminCode" placeholder="예: AGODASAVE" required>
            </div>
            <div>
              <label>만료일 (YYYY-MM-DD)</label>
              <input type="date" id="adminExpires" value="2026-12-31">
            </div>
          </div>
          <div class="admin-form-row">
            <label>혜택 설명</label>
            <input type="text" id="adminDesc" placeholder="예: 전세계 호텔 예약 시 7% 즉시할인" required>
          </div>
          <div class="admin-form-row">
            <label>제휴/공식 링크 (URL)</label>
            <input type="url" id="adminUrl" placeholder="https://..." required>
          </div>
          <div class="admin-form-actions">
            <button type="submit" class="btn-admin-submit"><i class="fa-solid fa-plus"></i> 쿠폰 즉시 추가</button>
            <button type="button" class="btn-admin-export" onclick="exportDataJSON()"><i class="fa-solid fa-download"></i> JSON 내보내기</button>
            <button type="button" class="btn-admin-reset" onclick="resetToDefaultData()"><i class="fa-solid fa-rotate-left"></i> 기본값 복원</button>
          </div>
        </form>
      </div>

      <!-- 등록된 쿠폰 테이블 -->
      <div class="admin-table-wrap">
        <table class="admin-table">
          <thead>
            <tr>
              <th>카테고리</th>
              <th>브랜드</th>
              <th>코드</th>
              <th>설명</th>
              <th>만료일</th>
              <th>관리</th>
            </tr>
          </thead>
          <tbody id="adminCouponTableBody">
            <!-- JS 동적 생성 -->
          </tbody>
        </table>
      </div>
    </div>
  `;
  return overlay;
}

// 관리자 테이블 새로고침
function refreshAdminTable() {
  const tbody = document.getElementById("adminCouponTableBody");
  if (!tbody || !COUPON_DATA) return;

  tbody.innerHTML = "";
  Object.keys(COUPON_DATA.categories).forEach(catKey => {
    const cat = COUPON_DATA.categories[catKey];
    (cat.items || []).forEach(item => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><span class="badge-cat">${catKey}</span></td>
        <td><strong>${item.name}</strong></td>
        <td><code>${item.code}</code></td>
        <td class="cell-desc">${item.desc}</td>
        <td>${item.expires || '무기한'}</td>
        <td>
          <button class="btn-del-mini" onclick="handleAdminDeleteCoupon('${catKey}', '${item.code}')">
            <i class="fa-solid fa-trash-can"></i> 삭제
          </button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  });
}

// 쿠폰 추가 처리
function handleAdminAddCoupon(e) {
  e.preventDefault();
  const catKey = document.getElementById("adminCategory").value;
  const name = document.getElementById("adminName").value.trim();
  const code = document.getElementById("adminCode").value.trim();
  const desc = document.getElementById("adminDesc").value.trim();
  const url = document.getElementById("adminUrl").value.trim();
  const expires = document.getElementById("adminExpires").value.trim();

  if (!COUPON_DATA.categories[catKey]) {
    alert("존재하지 않는 카테고리입니다.");
    return;
  }

  // 중복 체크 및 업데이트
  const existingIdx = COUPON_DATA.categories[catKey].items.findIndex(
    item => item.code.toUpperCase() === code.toUpperCase()
  );

  const newItem = {
    id: `${catKey.slice(0, 3)}-${Date.now().toString().slice(-4)}`,
    name,
    code,
    desc,
    url,
    expires: expires || "2026-12-31",
    is_active: true,
    badge: "NEW"
  };

  if (existingIdx >= 0) {
    COUPON_DATA.categories[catKey].items[existingIdx] = newItem;
    showToast(`[${name}] 쿠폰 정보가 수정되었습니다!`);
  } else {
    COUPON_DATA.categories[catKey].items.unshift(newItem);
    showToast(`[${name}] 신규 쿠폰이 즉시 등록되었습니다!`);
  }

  // 저장 & UI 갱신
  persistDataChanges(newItem, catKey);
  refreshAdminTable();
  updateUIWithData();
  document.getElementById("adminCouponForm").reset();
}

// 쿠폰 삭제 처리
function handleAdminDeleteCoupon(catKey, code) {
  if (!confirm(`'${code}' 쿠폰을 정말 삭제하시겠습니까?`)) return;

  if (COUPON_DATA.categories[catKey]) {
    COUPON_DATA.categories[catKey].items = COUPON_DATA.categories[catKey].items.filter(
      item => item.code.toUpperCase() !== code.toUpperCase()
    );
    persistDataChanges();
    refreshAdminTable();
    updateUIWithData();

    // 서버 파일에 실시간 반영 시도
    fetch(`/api/coupons?code=${encodeURIComponent(code)}`, { method: "DELETE" })
      .then(res => res.json())
      .then(data => console.log("💾 [서버 반영] 쿠폰 삭제 완료:", code))
      .catch(err => console.log("로컬 모드로 동작 중"));

    showToast(`'${code}' 쿠폰이 삭제되었습니다.`);
  }
}

// 변경사항 영구 저장 (localStorage + server.py API 실시간 동기화)
function persistDataChanges(newItem, catKey) {
  COUPON_DATA.last_updated = new Date().toISOString();
  localStorage.setItem("COUPONPICK_DATA_OVERRIDE", JSON.stringify(COUPON_DATA));

  // 서버 API가 살아있는 경우 data/coupons.json 파일에도 즉시 저장
  if (newItem && catKey) {
    fetch("/api/coupons", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...newItem, category: catKey })
    })
    .then(res => res.json())
    .then(data => console.log("💾 [서버 반영] data/coupons.json에 영구 저장 완료!"))
    .catch(err => console.log("로컬 스토리지에 저장됨"));
  }
}

// 기본값 복원
function resetToDefaultData() {
  if (confirm("모든 수동 변경 사항을 취소하고 원본 JSON 파일 기준으로 복원하시겠습니까?")) {
    localStorage.removeItem("COUPONPICK_DATA_OVERRIDE");
    loadCouponData().then(() => {
      refreshAdminTable();
      showToast("원본 데이터로 복원 완료되었습니다.");
    });
  }
}

// 수정된 데이터 JSON 다운로드
function exportDataJSON() {
  const jsonStr = JSON.stringify(COUPON_DATA, null, 2);
  const blob = new Blob([jsonStr], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "coupons.json";
  a.click();
  URL.revokeObjectURL(url);
  showToast("coupons.json 파일이 다운로드되었습니다. data/ 폴더에 덮어씌울 수 있습니다!");
}

// 오프라인/비상용 폴백 데이터
function getFallbackData() {
  return {
  "last_updated": "2026-09-05T12:57:50.714455",
  "version": "2.0.0",
  "categories": {
    "travel": {
      "title": "✈️ 여행 · 항공권 · 호텔 숙소 할인코드",
      "badge": "여행 특가",
      "items": [
        {
          "id": "trv-01",
          "name": "아고다 (Agoda)",
          "code": "AGODAHUB05",
          "desc": "전 세계 호텔 및 리조트 예약 5%~7% 전용 즉시할인 코드",
          "url": "https://www.agoda.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "인기 1위"
        },
        {
          "id": "trv-02",
          "name": "트립닷컴 (Trip.com)",
          "code": "TRIPNEW26",
          "desc": "국내외 항공권 및 제휴 호텔 패키지 최대 8% 즉시할인",
          "url": "https://kr.trip.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "항공+호텔"
        },
        {
          "id": "trv-03",
          "name": "클룩 (Klook)",
          "code": "KLOOKBHUB",
          "desc": "전세계 투어, 액티비티, 유심/교통패스 5,000원 즉시할인",
          "url": "https://www.klook.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "액티비티"
        },
        {
          "id": "trv-04",
          "name": "KKday (케이케이데이)",
          "code": "KKDAYSPRING",
          "desc": "일본/대만/동남아 필수 입장권 및 공항철도 즉시할인 바우처",
          "url": "https://www.kkday.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "해외교통"
        },
        {
          "id": "trv-05",
          "name": "호텔스닷컴 (Hotels.com)",
          "code": "HOTELLP08",
          "desc": "국내 및 해외 인기 호텔 예약 시 8% 할인코드 (10박 적립)",
          "url": "https://kr.hotels.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "8% OFF"
        },
        {
          "id": "trv-06",
          "name": "익스피디아 (Expedia)",
          "code": "EXPEDIA8",
          "desc": "전 세계 엄선된 숙소 예약 시 8% 추가 할인 프로모션",
          "url": "https://www.expedia.co.kr",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "호텔할인"
        },
        {
          "id": "trv-07",
          "name": "마이리얼트립",
          "code": "MYREAL2026",
          "desc": "국내외 투어, 항공권, 숙소 첫 결제 시 3,000원 즉시할인",
          "url": "https://www.myrealtrip.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "국내외투어"
        },
        {
          "id": "trv-08",
          "name": "부킹닷컴 (Booking.com)",
          "code": "BOOK10SAVE",
          "desc": "Genius 회원 전 세계 숙박 최대 15% 전용 혜택",
          "url": "https://www.booking.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "15% 혜택"
        },
        {
          "id": "trv-09",
          "name": "트래블로카 (Traveloka)",
          "code": "TVLKSPRING",
          "desc": "동남아 항공권 및 인기 리조트 예약 특별 프로모션 코드",
          "url": "https://www.traveloka.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "동남아특화"
        },
        {
          "id": "trv-10",
          "name": "라쿠텐 트래블 (Rakuten)",
          "code": "RAKUTENJP",
          "desc": "일본 전역 료칸, 특급 호텔 예약 5%~10% 전용 쿠폰",
          "url": "https://travel.rakuten.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "일본료칸"
        },
        {
          "id": "trv-11",
          "name": "돈키호테 (Don Quijote)",
          "code": "DONKI5OFF",
          "desc": "일본 돈키호테 매장 면세 10% + 추가 5% 모바일 바코드 쿠폰",
          "url": "https://www.donki.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "면세+5%"
        },
        {
          "id": "trv-12",
          "name": "유심사 (USIMSA)",
          "code": "USIMSA2026",
          "desc": "전세계 무제한 로밍 eSIM 전 국가 10% 즉시할인 코드",
          "url": "https://www.usimsa.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "eSIM추천"
        },
        {
          "id": "trv-13",
          "name": "에어알로 (Airalo)",
          "code": "AIRALO3OFF",
          "desc": "글로벌 200+ 국가 지원 1위 eSIM 첫 구매 $3 즉시할인",
          "url": "https://www.airalo.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "글로벌eSIM"
        },
        {
          "id": "trv-14",
          "name": "로밍도깨비 (Ggabi eSIM)",
          "code": "ROAMINGDOK",
          "desc": "일본/동남아/미주 로밍도깨비 eSIM 1,000원 할인 쿠폰",
          "url": "https://rokebi.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "eSIM할인"
        },
        {
          "id": "trv-15",
          "name": "와이파이도시락",
          "code": "DOSIRAK10",
          "desc": "해외 포켓와이파이 및 도시락eSIM 상시 10% 할인 예약",
          "url": "https://www.wifidosirak.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "포켓와이파이"
        },
        {
          "id": "trv-16",
          "name": "인터파크투어 (Interpark)",
          "code": "INTPARKTOUR",
          "desc": "국내외 패키지, 땡처리 항공권, 호텔 전용 할인 바우처",
          "url": "https://tour.interpark.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "땡처리항공"
        },
        {
          "id": "trv-17",
          "name": "야놀자 (NOL)",
          "code": "NOLYJ2026",
          "desc": "국내 호텔, 풀빌라, 레저, KTX 최대 10% 쿠폰팩",
          "url": "https://www.yanolja.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "국내숙박"
        },
        {
          "id": "trv-18",
          "name": "여기어때",
          "code": "YEOGIPRO26",
          "desc": "해외숙소 최대 8% 즉시할인 + 국내 숙박 10만원 쿠폰팩",
          "url": "https://www.goodchoice.kr",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "해외/국내"
        },
        {
          "id": "trv-19",
          "name": "제주패스 (JEJUPASS)",
          "code": "JEJUPASSRENT",
          "desc": "제주도 렌터카 가격비교 최저가 예약 + 5% 추가할인",
          "url": "https://www.jejupass.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "제주렌터카"
        },
        {
          "id": "trv-20",
          "name": "트립비토즈 (Tripbtoz)",
          "code": "TRIPBTOZ5",
          "desc": "영상 리뷰 기반 국내외 호텔 예약 5% 즉시할인 코드",
          "url": "https://www.tripbtoz.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": null
        },
        {
          "id": "trv-21",
          "name": "와그 (WAUG)",
          "code": "WAUGNEW",
          "desc": "국내외 테마파크, 뮤지컬 티켓, 투어 액티비티 첫구매 할인",
          "url": "https://www.waug.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": null
        },
        {
          "id": "trv-22",
          "name": "민다 (Minda)",
          "code": "MINDASTAY",
          "desc": "유럽, 미주 전세계 검증된 한인민박 예약 5,000원 할인",
          "url": "https://www.theminda.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "한인민박"
        },
        {
          "id": "trv-23",
          "name": "오미오 (Omio)",
          "code": "OMIOEUROPE",
          "desc": "유럽 기차(유로스타/이탈로/TGV), 플릭스버스 예약 10유로 할인",
          "url": "https://www.omio.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "유럽교통"
        },
        {
          "id": "trv-24",
          "name": "렌터카스닷컴",
          "code": "RENTALCARS",
          "desc": "전세계 글로벌 렌터카 Hertz, Avis, Enterprise 5% 할인",
          "url": "https://www.rentalcars.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": null
        },
        {
          "id": "trv-25",
          "name": "IHG 호텔 & 리조트",
          "code": "IHGDIRECT",
          "desc": "인터컨티넨탈, 홀리데이인 공식 홈페이지 직영 최저가 보장",
          "url": "https://www.ihg.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "특급호텔"
        }
      ]
    },
    "shopping": {
      "title": "🛍️ 해외직구 & 국내 쇼핑몰 할인코드",
      "badge": "쇼핑 특가",
      "items": [
        {
          "id": "shp-01",
          "name": "알리익스프레스 (AliExpress)",
          "code": "ALI26SAVE",
          "desc": "$50 이상 결제 시 $6, $100 이상 결제 시 $15 프로모션 코드",
          "url": "https://ko.aliexpress.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "직구 1위"
        },
        {
          "id": "shp-02",
          "name": "테무 (Temu)",
          "code": "TEMU90OFF",
          "desc": "신규 앱 설치 & 가입 시 최대 90% 할인 및 13만원 쿠폰세트",
          "url": "https://www.temu.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "초특가"
        },
        {
          "id": "shp-03",
          "name": "아이허브 (iHerb)",
          "code": "HUB9999",
          "desc": "영양제, 오메가3, 보충제, 웰니스 전 품목 5%~10% 상시할인",
          "url": "https://kr.iherb.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "영양제필수"
        },
        {
          "id": "shp-04",
          "name": "오늘의집",
          "code": "OHOU10000",
          "desc": "가구, 조명, 인테리어 소품 첫 결제 10,000원 웰컴 쿠폰",
          "url": "https://ohou.se",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "인테리어"
        },
        {
          "id": "shp-05",
          "name": "쿠팡 (Coupang)",
          "code": "COUPANGWOW",
          "desc": "로켓와우 골든박스 단독특가 및 로켓직구 무료배송",
          "url": "https://www.coupang.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "로켓배송"
        },
        {
          "id": "shp-06",
          "name": "아마존 (Amazon)",
          "code": "AMZKR20",
          "desc": "한국 직배송 $100 이상 결제 시 $15 즉시할인 프로모션",
          "url": "https://www.amazon.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "미국직구"
        },
        {
          "id": "shp-07",
          "name": "케이스티파이 (CASETiFY)",
          "code": "CASEVIP15",
          "desc": "아이폰 & 갤럭시 케이스, 테크 액세서리 전 품목 15% VIP 할인",
          "url": "https://www.casetify.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "15% 할인"
        },
        {
          "id": "shp-08",
          "name": "올리브영 (Olive Young)",
          "code": "OLIVEBIG",
          "desc": "올영세일 인기 뷰티, 스킨케어 10% 장바구니 보너스 쿠폰",
          "url": "https://www.oliveyoung.co.kr",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "K-뷰티"
        },
        {
          "id": "shp-09",
          "name": "크림 (KREAM)",
          "code": "KREAMSPRING",
          "desc": "한정판 스니커즈, 스트릿웨어, 럭셔리 배송비 무료 쿠폰",
          "url": "https://kream.co.kr",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "스니커즈"
        },
        {
          "id": "shp-10",
          "name": "큐텐 (Qoo10)",
          "code": "QOO10GLOBAL",
          "desc": "일본/아시아 직구 화장품 및 전자기기 $10 장바구니 쿠폰",
          "url": "https://www.qoo10.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "아시아직구"
        },
        {
          "id": "shp-11",
          "name": "11번가 아마존",
          "code": "11STAMZ",
          "desc": "우주패스 전용 5,000원 장바구니 쿠폰 + 무료배송",
          "url": "https://www.11st.co.kr",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "우주패스"
        },
        {
          "id": "shp-12",
          "name": "마켓컬리 (Kurly)",
          "code": "KURLY5000",
          "desc": "샛별배송 첫 주문 100원딜 혜택 + 5,000원 할인 쿠폰",
          "url": "https://www.kurly.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "신규100원"
        },
        {
          "id": "shp-13",
          "name": "CJ더마켓 (CJ Market)",
          "code": "CJMARKET40",
          "desc": "비비고, 햇반, 고메 등 가공식품 공식몰 최대 45% 쿠폰",
          "url": "https://www.cjthemarket.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "비비고할인"
        },
        {
          "id": "shp-14",
          "name": "풀무원 공식몰 (#풀무원)",
          "code": "PULMUONE10",
          "desc": "바른먹거리 풀무원 신선식품 신규가입 1만원 쿠폰팩",
          "url": "https://shop.pulmuone.co.kr",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": null
        },
        {
          "id": "shp-15",
          "name": "미트리 (Metree)",
          "code": "METREESAVE",
          "desc": "닭가슴살, 식단 도시락, 소고기 VIP 추천인 특가 (최대 56% 할인)",
          "url": "https://metree.co.kr",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "닭가슴살"
        },
        {
          "id": "shp-16",
          "name": "랭킹닭컴 (Rankingdak)",
          "code": "RANKINGDAK",
          "desc": "맛있닭, 잇메이트 닭가슴살 특급배송 전용 5,000원 쿠폰",
          "url": "https://www.rankingdak.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": null
        },
        {
          "id": "shp-17",
          "name": "펫프렌즈 (Pet Friends)",
          "code": "PETFRIENDS",
          "desc": "강아지/고양이 사료, 간식, 용품 첫구매 5,000원 쿠폰",
          "url": "https://pet-friends.co.kr",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "반려동물"
        },
        {
          "id": "shp-18",
          "name": "레고 공식몰 (LEGO)",
          "code": "LEGOBRICKS",
          "desc": "공식 스토어 한정판 브릭 세트 사은품 증정 프로모션",
          "url": "https://www.lego.com/ko-kr",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": null
        },
        {
          "id": "shp-19",
          "name": "레노버 (Lenovo)",
          "code": "LENOVO8",
          "desc": "ThinkPad, Legion 게이밍 노트북 공식몰 5% 추가할인",
          "url": "https://www.lenovo.com/kr",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "노트북"
        },
        {
          "id": "shp-20",
          "name": "다이슨 공식몰 (Dyson)",
          "code": "DYSONSPECIAL",
          "desc": "에어랩, 청소기, 공기청정기 공식몰 전용 거치대 사은품 혜택",
          "url": "https://www.dyson.co.kr",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "에어랩"
        },
        {
          "id": "shp-21",
          "name": "예스24 (YES24)",
          "code": "YES24BOOKS",
          "desc": "도서, 음반, e-book 장바구니 3,000원 상품권",
          "url": "https://www.yes24.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "도서할인"
        },
        {
          "id": "shp-22",
          "name": "교보문고",
          "code": "KYOBO2026",
          "desc": "온라인 교보문고 도서 결제 2,000원 앱 다운로드 쿠폰",
          "url": "https://www.kyobobook.co.kr",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": null
        },
        {
          "id": "shp-23",
          "name": "솔드아웃 (sold out)",
          "code": "SOLDOUT50",
          "desc": "무신사 한정판 거래 플랫폼 수수료 무료 쿠폰",
          "url": "https://www.soldout.co.kr",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": null
        }
      ]
    },
    "sub": {
      "title": "🎬 OTT 계정공유 · VPN · 소프트웨어 구독 할인",
      "badge": "초특가 구독",
      "items": [
        {
          "id": "sub-01",
          "name": "겜스고 (GamsGo)",
          "code": "GAMSGO5",
          "desc": "유튜브 프리미엄, 넷플릭스 70% 계정공유 5% 추가할인 코드 (월 3천원대)",
          "url": "https://www.gamsgo.com/partner/aTqwg",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "인기 1위"
        },
        {
          "id": "sub-02",
          "name": "스픽 (Speak)",
          "code": "SPEAKSAVE",
          "desc": "AI 영어회화 1위 스픽 프리미엄 연간 구독권 20,000원 즉시할인",
          "url": "https://www.usespeak.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "2만원 할인"
        },
        {
          "id": "sub-03",
          "name": "노드VPN (NordVPN)",
          "code": "NORD70OFF",
          "desc": "보안 1위 VPN 2년 플랜 최대 72% 할인 + 3개월 추가 무료 증정",
          "url": "https://nordvpn.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "72% OFF"
        },
        {
          "id": "sub-04",
          "name": "서프샤크 (Surfshark VPN)",
          "code": "SURF85OFF",
          "desc": "무제한 기기 동시접속 가성비 VPN 85% 특별할인 + 2개월 무료",
          "url": "https://surfshark.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "85% OFF"
        },
        {
          "id": "sub-05",
          "name": "익스프레스VPN (ExpressVPN)",
          "code": "EXPRESS3M",
          "desc": "초고속 스트리밍 최적화 VPN 12개월 결제 시 3개월 무료 연장",
          "url": "https://www.expressvpn.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "+3개월"
        },
        {
          "id": "sub-06",
          "name": "프로톤VPN (ProtonVPN)",
          "code": "PROTONSAVE",
          "desc": "스위스 기반 강력한 개인정보 보호 VPN 50% 할인 프로모션",
          "url": "https://protonvpn.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "보안최강"
        },
        {
          "id": "sub-07",
          "name": "어도비 (Adobe CC)",
          "code": "ADOBE60",
          "desc": "포토샵, 일러스트레이터, 프리미어 프로 학생/교직원 60% 특별할인",
          "url": "https://www.adobe.com/kr",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "학생60%"
        },
        {
          "id": "sub-08",
          "name": "우버택시 (Uber)",
          "code": "UBERKR2026",
          "desc": "첫 탑승 요금 50% 즉시 할인쿠폰 (최대 10,000원 할인)",
          "url": "https://www.uber.com/kr",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "50% 할인"
        },
        {
          "id": "sub-09",
          "name": "틱톡 라이트 (TikTok Lite)",
          "code": "TIKTOKLITE",
          "desc": "친구 초대 신규 가입 시 현금 출금 가능한 포인트 즉시 지급",
          "url": "https://www.tiktok.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "포인트증정"
        },
        {
          "id": "sub-10",
          "name": "크몽 (Kmong)",
          "code": "KMONG10000",
          "desc": "디자인, 프로그래밍, 번역 등 전문가 외주 첫 의뢰 1만원 할인",
          "url": "https://kmong.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "1만원 할인"
        },
        {
          "id": "sub-11",
          "name": "숨고 (Soomgo)",
          "code": "SOOMGO5000",
          "desc": "생활 서비스, 인테리어, 과외 견적 요청 5,000원 쿠폰",
          "url": "https://soomgo.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": null
        },
        {
          "id": "sub-12",
          "name": "밀리의 서재",
          "code": "MILLIEFIRST",
          "desc": "전자책 16만 권 무제한 첫 달 무료 구독 혜택",
          "url": "https://www.millie.co.kr",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "첫달무료"
        },
        {
          "id": "sub-13",
          "name": "윌라 오디오북",
          "code": "WELAAROCKS",
          "desc": "베스트셀러 오디오북 & 클래스 2주 무료 체험 + 3개월 50%",
          "url": "https://www.welaaa.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": null
        },
        {
          "id": "sub-14",
          "name": "링글 (Ringle)",
          "code": "RINGLEPOINT",
          "desc": "아이비리그 튜터 1:1 화상영어 20분 무료 수업권 + 포인트",
          "url": "https://www.ringleplus.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "아이비리그"
        },
        {
          "id": "sub-15",
          "name": "캔바 프로 (Canva Pro)",
          "code": "CANVAPRO30",
          "desc": "디자인 템플릿 & AI 도구 30일 무료 체험 프로모션",
          "url": "https://www.canva.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "무료체험"
        },
        {
          "id": "sub-16",
          "name": "마이크로소프트 365",
          "code": "MS365FAMILY",
          "desc": "Word, Excel, PowerPoint 1개월 무료체험 + 1TB 클라우드",
          "url": "https://www.microsoft.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": null
        }
      ]
    },
    "fashion": {
      "title": "👗 해외 럭셔리 & 패션 브랜드 할인코드",
      "badge": "패션 특가",
      "items": [
        {
          "id": "fas-01",
          "name": "파페치 (Farfetch)",
          "code": "FARFETCH10",
          "desc": "글로벌 디자이너 명품 브랜드 첫 구매 10% 정가품 할인코드",
          "url": "https://www.farfetch.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "명품1위"
        },
        {
          "id": "fas-02",
          "name": "마이테레사 (Mytheresa)",
          "code": "MYT15FIRST",
          "desc": "독일 명품 직구 공식몰 첫 주문 10%~15% 웰컴 바우처",
          "url": "https://www.mytheresa.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "15% 할인"
        },
        {
          "id": "fas-03",
          "name": "룰루레몬 (Lululemon)",
          "code": "LULU10KR",
          "desc": "요가복 & 프리미엄 애슬레저 공식 스토어 전 상품 무료배송",
          "url": "https://www.lululemon.co.kr",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "요가복"
        },
        {
          "id": "fas-04",
          "name": "세타이어 (Cettire)",
          "code": "CETTIRE10",
          "desc": "호주 명품 플랫폼 세일 상품 추가 10% 프로모션 코드",
          "url": "https://www.cettire.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "추가10%"
        },
        {
          "id": "fas-05",
          "name": "COS (코스)",
          "code": "COSHELLO10",
          "desc": "미니멀 패션 COS 공식 온라인몰 신규 가입 10% 웰컴 쿠폰",
          "url": "https://www.cos.com/ko-kr",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "10% 쿠폰"
        },
        {
          "id": "fas-06",
          "name": "아르켓 (ARKET)",
          "code": "ARKET10HELLO",
          "desc": "노르딕 라이프스타일 브랜드 ARKET 첫 구매 10% 할인코드",
          "url": "https://www.arket.com/ko-kr",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": null
        },
        {
          "id": "fas-07",
          "name": "W컨셉 (W Concept)",
          "code": "WCONCEPT10",
          "desc": "국내 최고 디자이너 편집몰 10% 앱 전용 장바구니 쿠폰",
          "url": "https://www.wconcept.co.kr",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "디자이너몰"
        },
        {
          "id": "fas-08",
          "name": "무신사 (Musinsa)",
          "code": "MUSINSA7",
          "desc": "무신사 스토어 전 브랜드 7% 쿠폰 및 회원등급 추가할인",
          "url": "https://www.musinsa.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "국내 1위"
        },
        {
          "id": "fas-09",
          "name": "지그재그 (Zigzag)",
          "code": "ZIGZAG20",
          "desc": "2030 여성 쇼핑몰 통합 첫 구매 20,000원 웰컴 쿠폰팩",
          "url": "https://zigzag.kr",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "쿠폰팩"
        },
        {
          "id": "fas-10",
          "name": "에이블리 (ABLY)",
          "code": "ABLYSAVE",
          "desc": "전 상품 무료배송 스타일 커머스 첫 쇼핑 지원금 쿠폰",
          "url": "https://a-bly.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": null
        },
        {
          "id": "fas-11",
          "name": "SSENSE (에센스)",
          "code": "SSENSESALE",
          "desc": "캐나다 명품 편집숍 스트릿웨어 & 하이엔드 시즌 오프 세일",
          "url": "https://www.ssense.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "스트릿명품"
        },
        {
          "id": "fas-12",
          "name": "24S (24세브르)",
          "code": "24SFIRST15",
          "desc": "LVMH 루이비통 모회사 공식 럭셔리몰 첫 구매 15% 할인",
          "url": "https://www.24s.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "LVMH공식"
        },
        {
          "id": "fas-13",
          "name": "조마샵 (Jomashop)",
          "code": "JOMAFAST20",
          "desc": "명품 시계, 선글라스, 향수 직구 $200 이상 결제 시 $20 할인",
          "url": "https://www.jomashop.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "명품시계"
        },
        {
          "id": "fas-14",
          "name": "조말론 런던 (Jo Malone)",
          "code": "JOMALONEGIFT",
          "desc": "공식 온라인 부티크 향수 구매 시 미니어처 코롱 증정",
          "url": "https://www.jomalone.co.kr",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "향수증정"
        },
        {
          "id": "fas-15",
          "name": "띠어리 (Theory)",
          "code": "THEORY15",
          "desc": "미니멀 컨템포러리 브랜드 띠어리 공식몰 신규 15% 바우처",
          "url": "https://www.theory.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": null
        },
        {
          "id": "fas-16",
          "name": "알로요가 (Alo Yoga)",
          "code": "ALOYOGA15",
          "desc": "글로벌 셀럽들의 워너비 애슬레저 첫 주문 15% 할인코드",
          "url": "https://www.aloyoga.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "셀럽애슬레저"
        },
        {
          "id": "fas-17",
          "name": "크록스 공식몰 (Crocs)",
          "code": "CROCS20KR",
          "desc": "클로그, 샌들, 지비츠 참 공식몰 클럽 회원 20% 할인",
          "url": "https://www.crocs.co.kr",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "20% 할인"
        },
        {
          "id": "fas-18",
          "name": "H&M 공식 온라인스토어",
          "code": "HMAPP15",
          "desc": "H&M 멤버십 신규 가입 & 앱 첫 구매 시 15% 즉시할인",
          "url": "https://www2.hm.com/ko_kr",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": null
        },
        {
          "id": "fas-19",
          "name": "스와로브스키 (Swarovski)",
          "code": "SWAROVSKI10",
          "desc": "크리스털 주얼리, 목걸이, 귀걸이 클럽 회원 10% 바우처",
          "url": "https://www.swarovski.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "주얼리"
        },
        {
          "id": "fas-20",
          "name": "나이키 공식몰 (Nike)",
          "code": "NIKEWELCOME",
          "desc": "나이키 멤버 가입 시 웰컴 1만원 쿠폰 및 전 상품 무료배송/반품",
          "url": "https://www.nike.com/kr",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "무료반품"
        },
        {
          "id": "fas-21",
          "name": "아디다스 공식몰 (Adidas)",
          "code": "ADICLUB10",
          "desc": "아디클럽 신규 가입 시 10% 웰컴 쿠폰 및 한정판 래플 응모",
          "url": "https://www.adidas.co.kr",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": null
        }
      ]
    },
    "guide": {
      "title": "💡 스마트 소비 & 직구 절약 백서",
      "badge": "절약 가이드",
      "items": [
        {
          "id": "gde-01",
          "name": "해외 원화결제(DCC) 차단법",
          "code": "TIP-DCC",
          "desc": "해외 결제 시 3~8% 불필요한 이중 환전 수수료 아끼는 카드사 세팅 방법",
          "url": "#",
          "expires": "2029-12-31",
          "is_active": true,
          "badge": "필독"
        },
        {
          "id": "gde-02",
          "name": "해외직구 관부가세 면세 한도 계산법",
          "code": "TIP-TAX",
          "desc": "미국 $200(목록통관), 일반 국가 $150 관세 면제 기준과 합산과세 주의사항",
          "url": "#",
          "expires": "2029-12-31",
          "is_active": true,
          "badge": "세금절약"
        },
        {
          "id": "gde-03",
          "name": "호텔 최저가 예약 노하우 5가지",
          "code": "TIP-HOTEL",
          "desc": "브라우저 시크릿 모드 검색, 통화 설정(현지통화 vs USD) 비교법",
          "url": "#",
          "expires": "2029-12-31",
          "is_active": true,
          "badge": "여행꿀팁"
        },
        {
          "id": "gde-04",
          "name": "제휴 캐시백 사이트 중복 적립법",
          "code": "TIP-CASHBACK",
          "desc": "할인코드 적용 후 추가로 결제액의 3~5% 캐시백 돌려받는 노하우",
          "url": "#",
          "expires": "2029-12-31",
          "is_active": true,
          "badge": "페이백"
        },
        {
          "id": "gde-05",
          "name": "항공권 가장 저렴하게 예매하는 요일/시간",
          "code": "TIP-FLIGHT",
          "desc": "출발 6주 전 화요일/수요일 예매가 가장 저렴한 데이터 분석 결과",
          "url": "#",
          "expires": "2029-12-31",
          "is_active": true,
          "badge": "항공권"
        },
        {
          "id": "gde-06",
          "name": "해외여행자보험 5분 만에 최저가 가입 팁",
          "code": "TIP-INSUR",
          "desc": "항공기 지연, 휴대품 파손 보장 필수 특약만 골라 반값에 가입하는 법",
          "url": "#",
          "expires": "2029-12-31",
          "is_active": true,
          "badge": "여행자보험"
        },
        {
          "id": "gde-07",
          "name": "글로벌 직구 블랙프라이데이 세일 캘린더",
          "code": "TIP-SALE-CAL",
          "desc": "알리 광군제, 미국 블프, 사이버먼데이, 여름 정기 세일 일정 총정리",
          "url": "#",
          "expires": "2029-12-31",
          "is_active": true,
          "badge": "세일캘린더"
        },
        {
          "id": "gde-08",
          "name": "환전 수수료 100% 우대받는 트래블로그/트래블월렛 비교",
          "code": "TIP-FXCARD",
          "desc": "해외 ATM 출금 수수료 무료 및 환전 수수료 0원 혜택 카드 완벽 분석",
          "url": "#",
          "expires": "2029-12-31",
          "is_active": true,
          "badge": "환전꿀팁"
        }
      ]
    },
    "game": {
      "title": "🎮 게임 · 게이밍 기어 · 스팀 할인",
      "badge": "게이밍 특가",
      "items": [
        {
          "id": "gam-01",
          "name": "스팀 (Steam)",
          "code": "STEAMSALE",
          "desc": "스팀 계절 정기 세일 및 주말 특가 최대 90% 할인",
          "url": "https://store.steampowered.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "스팀특가"
        },
        {
          "id": "gam-02",
          "name": "엑시트랙 (ExitLag)",
          "code": "EXITLAG20",
          "desc": "배그/롤 해외서버 핑(Ping) 렉 감소 VPN 20% 즉시할인",
          "url": "https://www.exitlag.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "핑VPN 1위"
        },
        {
          "id": "gam-03",
          "name": "그린맨게이밍 (GMG)",
          "code": "GMG15OFF",
          "desc": "정품 스팀 CD키 공식 리셀러 신작 및 예약구매 15% 할인",
          "url": "https://www.greenmangaming.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "정품키 15%"
        },
        {
          "id": "gam-04",
          "name": "에픽게임즈 (Epic Games)",
          "code": "EPICFREE",
          "desc": "매주 목요일 업데이트되는 인기 PC 게임 100% 무료 배포",
          "url": "https://store.epicgames.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "매주무료"
        },
        {
          "id": "gam-05",
          "name": "레이저 (Razer)",
          "code": "RAZER10KR",
          "desc": "게이밍 마우스, 기계식 키보드 공식몰 첫 구매 10% 쿠폰",
          "url": "https://www.razer.com/kr-kr",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "게이밍기어"
        },
        {
          "id": "gam-06",
          "name": "로지텍 G (Logitech G)",
          "code": "LOGITECHG",
          "desc": "G PRO 무선 마우스, 헤드셋 공식 인증 스토어 특가 쿠폰",
          "url": "https://www.logitechg.com/ko-kr",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "G-PRO"
        },
        {
          "id": "gam-07",
          "name": "Xbox Game Pass",
          "code": "XBOXPASS",
          "desc": "PC 및 콘솔 수백 개 명작 게임 첫 달 1,000원 무제한 플레이",
          "url": "https://www.xbox.com/ko-KR/xbox-game-pass",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "첫달천원"
        },
        {
          "id": "gam-08",
          "name": "닌텐도 e숍 (Nintendo)",
          "code": "NINTENDOJP",
          "desc": "닌텐도 스위치 디지털 다운로드 타이틀 정기 골드포인트 적립",
          "url": "https://www.nintendo.co.kr",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "스위치"
        },
        {
          "id": "gam-09",
          "name": "험블번들 (Humble Bundle)",
          "code": "HUMBLECHOICE",
          "desc": "인기 게임 패키지 초특가 번들 구매 + 자선 기부",
          "url": "https://www.humblebundle.com",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "번들세일"
        },
        {
          "id": "gam-10",
          "name": "미꾸라지 VPN (Mudfish)",
          "code": "MUDFISHBOOST",
          "desc": "종량제 최저가 게임 가속 VPN 종량제 크레딧 충전 혜택",
          "url": "https://mudfish.net",
          "expires": "2026-12-31",
          "is_active": true,
          "badge": "종량제VPN"
        }
      ]
    }
  }
};
}

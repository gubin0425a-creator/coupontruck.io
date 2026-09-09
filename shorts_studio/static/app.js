// WonkaShorts Studio Frontend Application Logic

let currentBatchId = "";
let currentBatchData = null;
let pollTimer = null;

document.addEventListener("DOMContentLoaded", () => {
  initUI();
  checkInitialStatus();
  loadBatches();
});

function initUI() {
  const themeSelect = document.getElementById("theme-select");
  const customThemeInput = document.getElementById("custom-theme-input");
  const btnStartBatch = document.getElementById("btn-start-batch");
  const batchSelector = document.getElementById("batch-selector");
  const btnDownloadCsv = document.getElementById("btn-download-csv");
  const btnYoutubeUpload = document.getElementById("btn-youtube-upload");

  // 테마 선택에 따른 사용자 정의 입력창 표시
  themeSelect.addEventListener("change", () => {
    if (themeSelect.value === "custom") {
      customThemeInput.classList.remove("hidden");
      customThemeInput.focus();
    } else {
      customThemeInput.classList.add("hidden");
    }
  });

  // 원클릭 제작 시작 버튼
  btnStartBatch.addEventListener("click", startBatchCreation);

  // 배치 선택 변경 시 상세 로드
  batchSelector.addEventListener("change", (e) => {
    if (e.target.value) {
      loadBatchDetail(e.target.value);
    }
  });

  // CSV 다운로드
  btnDownloadCsv.addEventListener("click", () => {
    if (currentBatchId) {
      window.location.href = `/api/download_csv/${currentBatchId}`;
    }
  });

  // 유튜브 일괄 예약 업로드
  btnYoutubeUpload.addEventListener("click", triggerYoutubeUpload);
}

async function checkInitialStatus() {
  try {
    const res = await fetch("/api/status");
    const data = await res.json();
    if (data.is_running) {
      setRunningState(true);
      startStatusPolling();
    }
  } catch (err) {
    console.error("초기 상태 확인 실패:", err);
  }
}

async function startBatchCreation() {
  const themeSelect = document.getElementById("theme-select");
  const customThemeInput = document.getElementById("custom-theme-input");
  const voiceSelect = document.getElementById("voice-select");
  const countInput = document.getElementById("count-input");
  const apiKeyInput = document.getElementById("api-key-input");
  const styleSelect = document.getElementById("style-select");

  let theme = themeSelect.value;
  if (theme === "custom") {
    theme = customThemeInput.value.trim() || "신비한 세계 건축과 토목의 비밀";
  }

  const payload = {
    theme: theme,
    count: parseInt(countInput.value) || 14,
    voice: voiceSelect.value,
    api_key: apiKeyInput.value.trim() || null,
    visual_style: styleSelect ? styleSelect.value : "hybrid"
  };

  try {
    const res = await fetch("/api/start_batch", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const err = await res.json();
      alert("오류: " + (err.detail || "작업을 시작할 수 없습니다."));
      return;
    }

    setRunningState(true);
    startStatusPolling();
  } catch (err) {
    alert("서버 통신 실패: " + err.message);
  }
}

function setRunningState(isRunning) {
  const badge = document.getElementById("global-status-badge");
  const btn = document.getElementById("btn-start-batch");
  const progressContainer = document.getElementById("progress-container");

  if (isRunning) {
    badge.textContent = "대량 제작 중...";
    badge.className = "status-indicator status-running";
    btn.disabled = true;
    progressContainer.classList.remove("hidden");
  } else {
    badge.textContent = "대기 중";
    badge.className = "status-indicator";
    btn.disabled = false;
  }
}

function startStatusPolling() {
  if (pollTimer) clearInterval(pollTimer);
  
  pollTimer = setInterval(async () => {
    try {
      const res = await fetch("/api/status");
      const status = await res.json();

      const stepText = document.getElementById("progress-step-text");
      const pctText = document.getElementById("progress-percent-text");
      const barFill = document.getElementById("progress-bar-fill");

      stepText.textContent = status.current_step || "작업 중...";
      pctText.textContent = `${status.percent}%`;
      barFill.style.width = `${status.percent}%`;

      if (!status.is_running) {
        clearInterval(pollTimer);
        setRunningState(false);
        if (status.error) {
          alert("제작 중 오류 발생: " + status.error);
        } else {
          stepText.textContent = "🎉 30일치(14편) 숏폼 대량 제작 및 100점 SEO 세팅 완료!";
          await loadBatches();
          if (status.current_batch_id) {
            document.getElementById("batch-selector").value = status.current_batch_id;
            loadBatchDetail(status.current_batch_id);
          }
        }
      }
    } catch (e) {
      console.error("폴링 오류:", e);
    }
  }, 1000);
}

async function loadBatches() {
  try {
    const res = await fetch("/api/batches");
    const data = await res.json();
    const selector = document.getElementById("batch-selector");
    selector.innerHTML = "";

    if (!data.batches || data.batches.length === 0) {
      selector.innerHTML = '<option value="">제작된 배치 없음</option>';
      return;
    }

    data.batches.forEach((b, idx) => {
      const opt = document.createElement("option");
      opt.value = b.batch_id;
      opt.textContent = `배치 ${b.date} (${b.episode_count}편)`;
      selector.appendChild(opt);
    });

    if (data.batches.length > 0) {
      currentBatchId = data.batches[0].batch_id;
      loadBatchDetail(currentBatchId);
    }
  } catch (err) {
    console.error("배치 목록 로드 실패:", err);
  }
}

async function loadBatchDetail(batchId) {
  currentBatchId = batchId;
  const btnCsv = document.getElementById("btn-download-csv");
  const btnUpload = document.getElementById("btn-youtube-upload");
  const statTotal = document.getElementById("stat-total-eps");

  try {
    const res = await fetch(`/api/batch/${batchId}`);
    const data = await res.json();
    currentBatchData = data;

    const episodes = data.episodes || [];
    statTotal.textContent = `${episodes.length} 편`;
    btnCsv.disabled = episodes.length === 0;
    btnUpload.disabled = episodes.length === 0;

    renderEpisodesSidebar(episodes);
    if (episodes.length > 0) {
      selectEpisode(0);
    }
  } catch (err) {
    console.error("배치 상세 로드 실패:", err);
  }
}

function renderEpisodesSidebar(episodes) {
  const sidebar = document.getElementById("episodes-list");
  sidebar.innerHTML = "";

  if (episodes.length === 0) {
    sidebar.innerHTML = '<div class="empty-state">에피소드가 없습니다.</div>';
    return;
  }

  episodes.forEach((ep, idx) => {
    const item = document.createElement("div");
    item.className = `episode-item ${idx === 0 ? "active" : ""}`;
    item.dataset.index = idx;

    const sched = ep.schedule || {};
    const dayKo = sched.weekday_ko ? `${sched.weekday_ko}요일` : "";
    const kst = sched.scheduled_kst ? sched.scheduled_kst.split(" ")[0] : "";

    item.innerHTML = `
      <div class="ep-badge">EP ${String(idx + 1).padStart(2, "0")}</div>
      <div class="ep-info">
        <div class="ep-date">📅 ${kst} (${dayKo}) 18:00 예약</div>
        <div class="ep-title">${ep.title}</div>
      </div>
    `;

    item.addEventListener("click", () => {
      document.querySelectorAll(".episode-item").forEach(el => el.classList.remove("active"));
      item.classList.add("active");
      selectEpisode(idx);
    });

    sidebar.appendChild(item);
  });
}

function selectEpisode(idx) {
  if (!currentBatchData || !currentBatchData.episodes) return;
  const ep = currentBatchData.episodes[idx];
  const studio = document.getElementById("episode-studio");
  if (!ep) return;

  const seo = ep.seo || {};
  const titles = seo.titles || [ep.title];
  const tagsString = seo.tags_string || (seo.tags ? seo.tags.join(", ") : "");
  const scenes = ep.scenes || [];

  studio.innerHTML = `
    <div class="studio-content-grid">
      <!-- 9:16 비디오 플레이어 -->
      <div class="video-preview-wrapper">
        <video class="video-player-916" controls poster="${ep.thumbnail_url || ''}">
          <source src="${ep.video_url || ''}" type="video/mp4">
          브라우저가 비디오 재생을 지원하지 않습니다.
        </video>
        <a href="${ep.video_url || '#'}" download="${ep.id}.mp4" class="btn btn-outline" style="width:100%;">
          ⬇️ 완성 비디오 MP4 다운로드
        </a>
      </div>

      <!-- SEO 100점 메타데이터 및 4단계 대본 -->
      <div class="seo-section">
        <!-- 후킹 타이틀 3종 -->
        <div class="seo-box">
          <div class="seo-box-header">
            <h4>🎯 알고리즘 후킹 제목 (A/B/C 3종)</h4>
            <button class="btn-copy" onclick="copyText('${escapeHtml(titles[0])}')">제목 복사</button>
          </div>
          <div class="copyable-text">${titles.map((t, i) => `<b>[Type ${String.fromCharCode(65 + i)}]</b> ${escapeHtml(t)}`).join("\n")}</div>
        </div>

        <!-- 500자 태그 -->
        <div class="seo-box">
          <div class="seo-box-header">
            <h4>🏷️ 500자 알고리즘 고득점 태그셋</h4>
            <button class="btn-copy" onclick="copyText('${escapeHtml(tagsString)}')">전체 태그 복사</button>
          </div>
          <div class="tag-pills">
            ${(seo.tags || []).map(t => `<span class="tag-pill">#${escapeHtml(t)}</span>`).join("")}
          </div>
        </div>

        <!-- 설명란 -->
        <div class="seo-box">
          <div class="seo-box-header">
            <h4>📝 타임라인 & 해시태그 포함 설명란</h4>
            <button class="btn-copy" onclick="copyText('${escapeHtml(seo.description || '')}')">설명 복사</button>
          </div>
          <div class="copyable-text">${escapeHtml(seo.description || '')}</div>
        </div>

        <!-- 고정 댓글 -->
        <div class="seo-box">
          <div class="seo-box-header">
            <h4>📌 시청자 참여 유도용 고정 댓글 (Pinned Comment)</h4>
            <button class="btn-copy" onclick="copyText('${escapeHtml(seo.pinned_comment || '')}')">댓글 복사</button>
          </div>
          <div class="copyable-text">${escapeHtml(seo.pinned_comment || '')}</div>
        </div>

        <!-- 4단계 서사 대본 뷰어 -->
        <div class="seo-box">
          <div class="seo-box-header">
            <h4>📜 신비한 건축사전 4단계 서사 대본 구조</h4>
          </div>
          <div class="copyable-text">${scenes.map((s, i) => `<b>[${s.type.toUpperCase()}]</b> ${s.narrator} (${s.infographic ? s.infographic.label + ' ' + s.infographic.dimension : ''})`).join("\n\n")}</div>
        </div>
      </div>
    </div>
  `;
}

function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/[&<>"']/g, m => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
  }[m]));
}

function copyText(text) {
  navigator.clipboard.writeText(text).then(() => {
    alert("클립보드에 복사되었습니다!");
  }).catch(err => {
    console.error("복사 실패:", err);
  });
}

async function triggerYoutubeUpload() {
  if (!currentBatchId) return;
  const ok = confirm("현재 배치의 에피소드들을 YouTube Data API를 통해 '비공개 예약 공개'로 업로드하시겠습니까?\n(client_secrets.json이 등록되어 있어야 실제 계정에 등록됩니다.)");
  if (!ok) return;

  try {
    const res = await fetch("/api/schedule_upload", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ batch_id: currentBatchId })
    });
    const result = await res.json();
    alert(`YouTube 예약 업로드 처리 완료!\n총 ${result.results.length}편이 처리되었습니다.`);
  } catch (err) {
    alert("업로드 요청 실패: " + err.message);
  }
}

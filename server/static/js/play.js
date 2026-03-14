// IMPORTANT: Must be loaded with <script type="module">

function getEnvSlug() {
  const shell = document.querySelector(".play-shell");
  const slug = shell ? shell.dataset.envSlug : "";
  return (slug || "").trim();
}

const ENV = getEnvSlug();

let difficulty = "medium";
const socket = io({
  transports: ["websocket"]
});
let waitingForState = false;

function escapeHtml(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => (
    { "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;" }[c]
  ));
}

/* =============================
   UI: difficulty + reset emit
============================= */

const diffButtons = document.querySelectorAll(".play-diff-btn");

function setDifficulty(diff) {
  difficulty = diff;

  diffButtons.forEach(btn => {
    btn.classList.toggle("is-active", btn.dataset.diff === diff);
  });

  reset();
}

diffButtons.forEach(btn => {
  btn.addEventListener("click", () => {
    setDifficulty(btn.dataset.diff);
  });
});

// default highlight
setDifficulty("medium");

const resetBtn = document.getElementById("btnReset");
if (resetBtn) {
  resetBtn.addEventListener("click", () => reset());
}

function reset() {
  waitingForState = true;

  const inputs = document.querySelectorAll(".play-input");
  const players = [];

  inputs.forEach(input => {
    players.push((input.value || "").trim());
  });

  socket.emit("reset_game", {
    env_slug: ENV,
    difficulty: difficulty,
    players: players
  });
}

/* =============================
   UI: tabs, elo filter pop
============================= */

(function initSidebarUI() {
  const tabs = document.querySelectorAll(".play-tab");
  const panes = {
    browse: document.getElementById("tab-browse"),
    mine: document.getElementById("tab-mine"),
  };

  function setTab(name) {
    tabs.forEach(t => {
      const active = t.dataset.tab === name;
      t.classList.toggle("is-active", active);
      t.setAttribute("aria-selected", active ? "true" : "false");
    });

    if (panes.browse) panes.browse.classList.toggle("is-active", name === "browse");
    if (panes.mine) panes.mine.classList.toggle("is-active", name === "mine");
  }

  const params = new URLSearchParams(window.location.search);
  const initialTab = params.get("tab");

  if (initialTab === "mine") {
    setTab("mine");
  } else {
    setTab("browse");
  }

  tabs.forEach(t => t.addEventListener("click", () => setTab(t.dataset.tab)));

  const btn = document.getElementById("eloFilterBtn");
  const pop = document.getElementById("eloPop");

  if (btn && pop) {
    btn.addEventListener("click", () => {
      const open = !pop.classList.contains("is-open");
      pop.classList.toggle("is-open", open);
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  const clear = document.getElementById("eloClear");
  if (clear) {
    clear.addEventListener("click", () => {
      const min = document.getElementById("eloMin");
      const max = document.getElementById("eloMax");
      if (min) min.value = "";
      if (max) max.value = "";
      if (btn) btn.textContent = "Elo: Any";
    });
  }
})();

/* =============================
   UI: player highlight + fill
============================= */

(function initPlayerSelection() {
  const playerInputs = Array.from(document.querySelectorAll(".play-input"));
  let activePlayerIdx = 0;

  function ensureHighlightStyles() {
    if (document.getElementById("playerHighlightStyle")) return;
    const style = document.createElement("style");
    style.id = "playerHighlightStyle";
    style.textContent = `
      .play-input.is-active-player{
        outline: 2px solid rgba(255, 255, 255, 0.35);
        box-shadow: 0 0 0 4px rgba(255, 255, 255, 0.10);
      }

      .play-sort-pill.is-neutral{
        opacity: 0.55;
      }
    `;
    document.head.appendChild(style);
  }

  function setActivePlayer(idx) {
    if (!playerInputs.length) return;

    activePlayerIdx = ((idx % playerInputs.length) + playerInputs.length) % playerInputs.length;

    playerInputs.forEach((inp, i) => {
      inp.classList.toggle("is-active-player", i === activePlayerIdx);
    });
  }

  function fillActivePlayer(name) {
    if (!playerInputs.length) return;
    const active = playerInputs[activePlayerIdx];
    if (!active) return;

    active.value = name;
    setActivePlayer(activePlayerIdx + 1);
  }

  ensureHighlightStyles();
  setActivePlayer(0);

  playerInputs.forEach((inp, idx) => {
    inp.addEventListener("focus", () => setActivePlayer(idx));
    inp.addEventListener("click", () => setActivePlayer(idx));
  });

  document.addEventListener("click", (e) => {
    const btnRow = e.target.closest(".bot-row-btn, .bot-select-btn");
    if (!btnRow) return;

    const botName = btnRow.dataset.bot || "";
    if (!botName) return;

    fillActivePlayer(botName);
  });
})();

/* =============================
   UI: search + sort bot list
============================= */

(function initBotSearchAndSort() {
  const searchInput = document.getElementById("botSearch");
  const browseList = document.getElementById("browseList");
  const eloSortBtn = document.getElementById("sortByElo");

  if (!browseList) return;

  let sortState = 0; // 0=alpha, 1=elo desc, 2=elo asc
  let allRows = [];

  function getRows() {
    return Array.from(browseList.querySelectorAll(".bot-row"));
  }

  function getBotNameFromRow(row) {
    const el = row.querySelector(".bot-name");
    return (el ? el.textContent : row.dataset.bot || "").trim().toLowerCase();
  }

  function getBotEloFromRow(row) {
    const d = row.getAttribute("data-elo");
    if (d != null && d !== "") {
      const n = Number(d);
      return Number.isFinite(n) ? n : 0;
    }

    const el = row.querySelector(".bot-elo");
    const txt = (el ? el.textContent : "").toLowerCase();
    const m = txt.match(/(-?\d+(\.\d+)?)/);
    if (!m) return 0;

    const n = Number(m[1]);
    return Number.isFinite(n) ? n : 0;
  }

  function sortRows(rows, mode) {
    return rows.slice().sort((a, b) => {
      if (mode === 0) {
        return getBotNameFromRow(a).localeCompare(getBotNameFromRow(b));
      }
      if (mode === 1) {
        return getBotEloFromRow(b) - getBotEloFromRow(a);
      }
      return getBotEloFromRow(a) - getBotEloFromRow(b);
    });
  }

  function updateEloBtnUI() {
    if (!eloSortBtn) return;

    if (sortState === 0) {
      eloSortBtn.textContent = "Elo";
      eloSortBtn.classList.add("is-neutral");
    } else if (sortState === 1) {
      eloSortBtn.textContent = "Elo ▲";
      eloSortBtn.classList.remove("is-neutral");
    } else {
      eloSortBtn.textContent = "Elo ▼";
      eloSortBtn.classList.remove("is-neutral");
    }
  }

  function renderRows(rows) {
    browseList.innerHTML = "";
    rows.forEach(row => browseList.appendChild(row));
  }

  function applyFiltersAndSort() {
    const query = searchInput ? searchInput.value.trim().toLowerCase() : "";

    let filteredRows = allRows.filter(row => {
      if (!query) return true;
      return getBotNameFromRow(row).includes(query);
    });

    filteredRows = sortRows(filteredRows, sortState);
    renderRows(filteredRows);
  }

  function snapshotRows() {
    allRows = getRows();
  }

  snapshotRows();
  updateEloBtnUI();
  applyFiltersAndSort();

  if (eloSortBtn) {
    eloSortBtn.addEventListener("click", () => {
      sortState = (sortState + 1) % 3;
      updateEloBtnUI();
      applyFiltersAndSort();
    });
  }

  if (searchInput) {
    searchInput.addEventListener("input", () => {
      applyFiltersAndSort();
    });
  }
})();

/* =============================
   UI: prevent arrow keys scroll
============================= */

window.addEventListener("keydown", function (e) {
  const keysToBlock = ["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", " "];
  if (keysToBlock.includes(e.key)) {
    e.preventDefault();
  }
});

/* =============================
   UI: delete bot
============================= */

document.addEventListener("click", async function (e) {
  if (!e.target.classList.contains("bot-delete-btn")) return;

  const row = e.target.closest(".bot-row");
  if (!row) return;

  const botId = row.dataset.id;
  if (!botId) return;

  if (!confirm("Delete this bot permanently?")) return;

  const res = await fetch(`/delete_bot/${botId}`, {
    method: "POST",
    headers: { "X-Requested-With": "XMLHttpRequest" }
  });

  const data = await res.json();

  if (data.success) {
    const url = new URL(window.location.href);
    url.searchParams.set("tab", "mine");
    window.location.href = url.toString();
  } else {
    alert(data.message || "Delete failed.");
  }
});

/* =============================
   UI: auto upload on file choose
============================= */

(function initAutoUpload() {
  const uploadInput = document.getElementById("botUploadInput");
  const uploadForm = document.getElementById("botUploadForm");

  if (!uploadInput || !uploadForm) return;

  uploadInput.addEventListener("change", () => {
    if (!uploadInput.files || !uploadInput.files.length) return;

    if (typeof uploadForm.requestSubmit === "function") {
      uploadForm.requestSubmit();
    } else {
      uploadForm.submit();
    }
  });
})();


/* =============================
   Bot error banner
============================= */

socket.on("bot_error", (data) => {
  showBotError(data.message);
});

function showBotError(message) {
  const banner = document.getElementById("botErrorBanner");
  if (!banner) return;

  banner.textContent = message;
  banner.style.display = "block";

  const p1 = document.getElementById("p1Input");
  const p2 = document.getElementById("p2Input");

  if (message.includes("P1") && p1) p1.style.borderColor = "red";
  if (message.includes("P2") && p2) p2.style.borderColor = "red";

  setTimeout(() => {
    banner.style.display = "none";
    if (p1) p1.style.borderColor = "";
    if (p2) p2.style.borderColor = "";
  }, 4000);
}

/* =============================
   Canvas + env draw module
============================= */

const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

const keys = {};
let draw = null;
let debugEnabled = false;

async function loadEnvironment() {
  try {
    const module = await import(`/static/draw/${ENV}_draw.js`);
    draw = module.default;

    if (typeof draw !== "function") {
      throw new Error("Draw module does not export default function");
    }
  } catch (err) {
    draw = (ctx2) => {
      ctx2.clearRect(0, 0, canvas.width, canvas.height);
      ctx2.fillStyle = "#111";
      ctx2.fillRect(0, 0, canvas.width, canvas.height);
      ctx2.fillStyle = "red";
      ctx2.font = "20px Arial";
      ctx2.fillText(`Failed to load environment: ${ENV}`, 50, 200);
    };
  }
}

/* =============================
   Input handling
============================= */

document.addEventListener("keydown", (e) => {
  keys[e.key] = true;
});

document.addEventListener("keyup", (e) => {
  keys[e.key] = false;
});

/* =============================
   Game loop (client tick)
============================= */

let lastTime = 0;
const fps = 60;
const frameDuration = 1000 / fps;

function gameLoop(currentTime) {
  if (currentTime - lastTime >= frameDuration) {

    if (!waitingForState) {
      console.log(currentTime - lastTime)
      socket.emit("input", {
        action: keys,
        env_slug: ENV,
      });

      waitingForState = true;
      //lastTime = currentTime;
    }

  }

  requestAnimationFrame(gameLoop);
}

socket.on("connect", () => {
  socket.emit("join_env", {
    env_slug: ENV,
    difficulty: difficulty
  });
});

/* =============================
   Receive state from server
============================= */

socket.on("state", (state) => {
  waitingForState = false;

  if (!draw) return;

  draw(ctx, state);

  if (debugEnabled) {
    const debugBox = document.getElementById("debugBox");
    if (debugBox) {
      debugBox.textContent = JSON.stringify(state, null, 2);
    }
  }
});

const chkDebug = document.getElementById("chkDebug");
if (chkDebug) {
  chkDebug.addEventListener("change", (e) => {
    debugEnabled = e.target.checked;
  });
}

const btnFullscreen = document.getElementById("btnFullscreen");
if (btnFullscreen) {
  btnFullscreen.addEventListener("click", () => {
    if (!document.fullscreenElement) {
      canvas.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
  });
}

/* =============================
   Initialize
============================= */

await loadEnvironment();
gameLoop(performance.now());
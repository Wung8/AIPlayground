// static/play.js
// IMPORTANT: Must be loaded with <script type="module">

const socket = io();

const resetBtn = document.getElementById("btnReset");

resetBtn.addEventListener("click", () => {
  const p1Name = document.getElementById("p1Input").value.trim();
  const p2Name = document.getElementById("p2Input").value.trim();

  socket.emit("reset_game", {
    env_slug: window.__ENV_SLUG__,
    p1_name: p1Name,
    p2_name: p2Name
  });
});

socket.on("bot_error", (data) => {
  showBotError(data.message);
});

function showBotError(message) {
  const banner = document.getElementById("botErrorBanner");
  banner.textContent = message;
  banner.style.display = "block";

  if (message.includes("P1")) {
    document.getElementById("p1Input").style.borderColor = "red";
  }

  if (message.includes("P2")) {
    document.getElementById("p2Input").style.borderColor = "red";
  }

  setTimeout(() => {
    banner.style.display = "none";
    document.getElementById("p1Input").style.borderColor = "";
    document.getElementById("p2Input").style.borderColor = "";
  }, 4000);
}

const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

const ENV = window.__ENV_SLUG__ || "slimevolleyball";

const keys = {};
let draw = null;
let debugEnabled = false;

/* =============================
   Load Environment Draw Module
============================= */

async function loadEnvironment() {
  try {
    const module = await import(`./draw/${ENV}_draw.js`);
    draw = module.default;

    if (typeof draw !== "function") {
      throw new Error("Draw module does not export default function");
    }

    console.log(`Loaded draw module for: ${ENV}`);
  } catch (err) {
    console.error(`Failed to load draw module for ${ENV}`, err);

    // Fallback draw (simple error screen)
    draw = (ctx) => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = "#111";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = "red";
      ctx.font = "20px Arial";
      ctx.fillText(`Failed to load environment: ${ENV}`, 50, 200);
    };
  }
}

/* =============================
   Input Handling
============================= */

document.addEventListener("keydown", (e) => {
  keys[e.key] = true;
});

document.addEventListener("keyup", (e) => {
  keys[e.key] = false;
});

/* =============================
   Game Loop (Client Tick)
============================= */

let lastTime = 0;
const maxAllowedTime = 1000;
const fps = 20;
const frameDuration = 1000 / fps;

function gameLoop(currentTime) {
  if (currentTime - lastTime >= frameDuration) {
    if (currentTime - lastTime > maxAllowedTime) {
      lastTime = currentTime;
    }

    socket.emit("input", {
      action: keys,
      env_slug: ENV,
    });

    lastTime += frameDuration;
  }

  requestAnimationFrame(gameLoop);
}

socket.on("connect", () => {
  socket.emit("join_env", {
    env_slug: ENV
  });
});

/* =============================
   Receive State From Server
============================= */

socket.on("state", (state) => {
  if (!draw) return;

  draw(ctx, state);

  if (debugEnabled) {
    const debugBox = document.getElementById("debugBox");
    if (debugBox) {
      debugBox.textContent = JSON.stringify(state, null, 2);
    }
  }
});

/* =============================
   UI Controls
============================= */

const btnReset = document.getElementById("btnReset");
if (btnReset) {
  btnReset.addEventListener("click", () => {
    socket.emit("reset", { env_slug: ENV });
  });
}

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

import "./style.css";

const app = document.querySelector<HTMLDivElement>("#app");
if (!app) throw new Error("missing #app");

app.innerHTML = `
  <div class="page">
    <header class="topbar">
      <div class="brand">
        <div class="brand-icon" aria-hidden="true">
          <div class="brand-dot dot-1"></div>
          <div class="brand-dot dot-2"></div>
          <div class="brand-v">v</div>
        </div>
        <div class="brand-text">AI Playground</div>
      </div>

      <nav class="nav">
        <a class="nav-link is-active" href="#">Home</a>
        <a class="nav-link" href="#">About</a>
        <a class="nav-link" href="#">Environments</a>
        <a class="nav-link" href="#">ACM</a>
        <a class="nav-link" href="#">Login</a>
      </nav>
    </header>

    <div class="content">
      <aside class="sidebar">
        <div class="card">
          <div class="card-title">Select Players:</div>

          <div class="field-row">
            <div class="field-label">P1:</div>
            <input class="field-input" value="player" />
          </div>

          <div class="field-row">
            <div class="field-label">P2:</div>
            <div class="field-input field-pill">
              <span>basicbot25</span>
              <span class="muted">elo: 1000</span>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-title">Search Bots:</div>
          <input class="field-input field-search" value="search" />

          <div class="sort-row">
            <div class="sort-left">
              <span class="muted">Sort By:</span>
              <span class="sort-pill">Elo</span>
            </div>
          </div>

          <div class="bot-list">
            <button class="bot-item">
              <div class="bot-name">epicbot</div>
              <div class="bot-meta">
                <div class="muted">elo: 1400</div>
                <div class="muted">by: someone</div>
              </div>
            </button>

            <button class="bot-item is-selected">
              <div class="bot-name">basicbot25</div>
              <div class="bot-meta">
                <div class="muted">elo: 1000</div>
                <div class="muted">by: yung8</div>
              </div>
            </button>

            <button class="bot-item">
              <div class="bot-name">another_bot2000</div>
              <div class="bot-meta">
                <div class="muted">elo: 600</div>
                <div class="muted">by: yung8</div>
              </div>
            </button>
          </div>
        </div>
      </aside>

      <main class="main">
        <div class="panel-header">
          <a class="back-link" href="#">Back</a>
          <h1 class="title">Slime Volleyball</h1>
        </div>

        <section class="stage">
          <div class="canvas-shell">
            <canvas id="game" width="800" height="400"></canvas>
          </div>

          <div class="stage-actions">
            <button class="stage-link">Reset</button>

            <label class="debug-toggle">
              <span class="stage-link">Debug</span>
              <input type="checkbox" />
            </label>

            <button class="stage-link">Fullscreen</button>
          </div>
        </section>

        <section class="debug-panel">
          <div class="debug-scroll">
            <div class="debug-text">
              DebugTextDebugTextDebugTextDebugTextDebugTextDebugTextDebugText<br />
              DebugTextDebugTextDebugTextDebugTextDebugTextDebugTextDebugText<br />
              DebugTextDebugTextDebugTextDebugTextDebugTextDebugTextDebugText<br />
              DebugTextDebugTextDebugTextDebugTextDebugTextDebugTextDebugText
            </div>
          </div>
        </section>
      </main>
    </div>
  </div>
`;

// keep the canvas pure white like the concept art
const canvas = document.getElementById("game") as HTMLCanvasElement | null;
if (canvas) {
  const ctx = canvas.getContext("2d");
  if (ctx) {
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  }
}

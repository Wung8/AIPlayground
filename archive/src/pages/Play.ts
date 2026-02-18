import { getEnv, environments } from "../data/environments";

type Bot = {
  name: string;
  elo: number;
  by: string;
};

const BOTS: Bot[] = [
  { name: "epicbot", elo: 1400, by: "someone" },
  { name: "basicbot25", elo: 1000, by: "wung8" },
  { name: "another_bot2000", elo: 600, by: "wung8" },
];

function fmtElo(n: number) {
  return `${n}`;
}

export function PlayPage(slug?: string) {
  const env = (slug && getEnv(slug)) || environments[0];
  const title = env ? env.title : "Play";

  const botRows = BOTS.map(
    (b) => `
      <div class="bot-row">
        <div class="bot-name">${b.name}</div>
        <div class="bot-meta">
          <div class="bot-elo">elo: ${fmtElo(b.elo)}</div>
          <div class="bot-by">by: ${b.by}</div>
        </div>
      </div>
    `
  ).join("");

  return `
    <div class="play-shell">
      <aside class="play-left">
        <div class="play-left-card">
          <div class="play-left-title">Select Players:</div>

          <div class="play-field">
            <div class="play-label">P1:</div>
            <div class="play-input">player</div>
          </div>

          <div class="play-field">
            <div class="play-label">P2:</div>
            <div class="play-input">basicbot25</div>
            <div class="play-inline-elo">elo: 1000</div>
          </div>

          <div class="play-search">
            <div class="play-search-row">
              <div class="play-search-label">Search Bots:</div>
              <div class="play-search-box">search</div>
            </div>
            <div class="play-sort-row">
              <div class="play-sort-label">Sort By:</div>
              <div class="play-sort-pill">Elo</div>
            </div>
          </div>

          <div class="play-botlist">
            ${botRows}
          </div>
        </div>
      </aside>

      <main class="play-main">
        <div class="play-main-head">
          <a class="play-back" href="#/doc/${env?.slug || ""}">Back</a>
          <div class="play-title">${title}</div>
        </div>

        <div class="play-stage">
          <div class="play-canvas"></div>

          <div class="play-stage-controls">
            <button class="play-stage-btn" type="button">Reset</button>
            <label class="play-stage-debug">
              Debug <input type="checkbox" />
            </label>
            <button class="play-stage-btn" type="button">Fullscreen</button>
          </div>
        </div>

        <div class="play-debug">
          <div class="play-debug-box">
            DebugTextDebugTextDebugTextDebugTextDebugTextDebugTextDebugTextDebugText<br/>
            DebugTextDebugTextDebugTextDebugTextDebugTextDebugTextDebugTextDebugText<br/>
            DebugTextDebugTextDebugTextDebugTextDebugTextDebugTextDebugTextDebugText<br/>
            DebugTextDebugTextDebugTextDebugTextDebugTextDebugTextDebugTextDebugText
          </div>
        </div>
      </main>
    </div>
  `;
}

import { getEnv, environments } from "../data/environments";

function stars(n: number) {
  const full = "★".repeat(Math.max(0, Math.min(5, n)));
  const empty = "☆".repeat(Math.max(0, 5 - Math.min(5, Math.max(0, n))));
  return full + empty;
}

export function EnvDocPage(slug: string) {
  const env = getEnv(slug) || environments[0];
  if (!env) return `<div class="content"><main class="main">missing env</main></div>`;

  const sidebarDoc = `
    <div class="side-section">
      <div class="side-title">User Documentation</div>
      <div class="side-item small">Installation</div>
      <div class="side-item small">Creating Agents</div>
      <div class="side-item small">Uploading Agents</div>
    </div>
  `;

  const sidebarEnv = `
    <div class="side-section">
      <div class="side-title">Environments</div>
      <div class="side-box">
        ${environments
          .map((e) => {
            const cls = e.slug === env.slug ? "side-item is-active" : "side-item";
            return `<a class="${cls}" href="#/doc/${e.slug}">${e.title}</a>`;
          })
          .join("")}
      </div>
    </div>
  `;

  const docBlocks = (env.docSections || [])
    .filter((s) => (s.title || "").trim().toLowerCase() !== "user documentation")
    .map((s) => {
      const items = (s.items || []).map((it) => `<li>${it}</li>`).join("");
      return `
        <div class="doc-block">
          <div class="doc-h">${s.title}</div>
          <ul class="doc-ul">${items}</ul>
        </div>
      `;
    })
    .join("");

  return `
    <div class="content">
      <aside class="sidebar wide">
        ${sidebarDoc}
        ${sidebarEnv}
      </aside>

      <main class="main">
        <div class="doc-header">
          <div class="doc-left">
            <a class="back-link" href="#/environments">Back</a>
            <div class="doc-title-row">
              <div class="doc-title">${env.title}</div>
              <div class="doc-title-muted">Documentation</div>
            </div>
            <div class="doc-diff">
              <span class="doc-diff-label">Difficulty:</span>
              <span class="doc-stars">${stars(env.difficulty)}</span>
            </div>
          </div>

          <a class="doc-gh" href="#/github">Github</a>
        </div>

        <div class="doc-canvas-wrap">
          <div class="doc-canvas"></div>
        </div>

        <div class="doc-play-wrap">
          <a class="doc-play-btn" href="#/play/${env.slug}">Play now</a>
        </div>

        <div class="doc-desc">
          <div class="doc-desc-h">Description</div>
          <div class="doc-desc-p">${env.description}</div>
        </div>

        ${docBlocks ? `<div class="doc-sections">${docBlocks}</div>` : ""}
      </main>
    </div>
  `;
}

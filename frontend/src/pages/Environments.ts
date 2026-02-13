import { environments } from "../data/environments";

function stars(n: number) {
  const full = "★".repeat(Math.max(0, Math.min(5, n)));
  const empty = "☆".repeat(Math.max(0, 5 - Math.min(5, Math.max(0, n))));
  return full + empty;
}

export function EnvironmentsPage(selectedSlug?: string) {
  const selected = selectedSlug || environments[0]?.slug || "";

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
            const cls = e.slug === selected ? "side-item is-active" : "side-item";
            return `<a class="${cls}" href="#/doc/${e.slug}">${e.title}</a>`;

            // return `<a class="${cls}" href="#/environments/${e.slug}">${e.title}</a>`;
          })
          .join("")}
      </div>
    </div>
  `;

  const cards = environments
    .map((e) => {
      return `
        <div class="env-card">
          <div class="env-card-left">
            <div class="env-h2">${e.title}</div>
            <div class="env-diff">
              <span class="env-diff-label">Difficulty:</span>
              <span class="env-stars">${stars(e.difficulty)}</span>
            </div>
            <div class="env-desc">${e.description}</div>
            <a class="env-doc-link" href="#/doc/${e.slug}">documentation</a>
          </div>
          <div class="env-card-right">
            <div class="env-img"></div>
          </div>
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

      <main class="main panel">
        <div class="panel-pad">
          <div class="panel-title">Environments</div>
          <div class="env-list">
            ${cards}
          </div>
        </div>
      </main>
    </div>
  `;
}

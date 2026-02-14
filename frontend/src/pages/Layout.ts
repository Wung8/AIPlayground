export function Layout(active: "home" | "environments" | "acm" | "about" | "login", inner: string) {
  const nav = (label: string, href: string, key: typeof active) =>
    `<a class="nav-link ${active === key ? "is-active" : ""}" href="${href}">${label}</a>`;

  return `
    <div class="page">
      <header class="topbar">
        <div class="brand">
          <div class="brand-icon" aria-hidden="true">
            <div class="brand-dot dot-1"></div>
            <div class="brand-dot dot-2"></div>
            <div class="brand-v">v</div>
          </div>
          <a class="brand-text brand-link" href="#/">AI Playground</a>
        </div>

        <nav class="nav">
          ${nav("Home", "#/", "home")}
          ${nav("Environments", "#/environments", "environments")}
          ${nav("ACM", "#/acm", "acm")}
          ${nav("Login", "#/login", "login")}
        </nav>
      </header>

      ${inner}
    </div>
  `;
}

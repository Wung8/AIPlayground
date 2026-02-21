// src/components/Layout.jsx
import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";

export default function Layout({
  title = "AI Playground",
  active = "",
  isAuthenticated = false,
  flashes = [],
  children,
}) {
  const [localFlashes, setLocalFlashes] = useState(() =>
    (flashes || []).map((f, i) => ({ id: i, ...f }))
  );

  useEffect(() => {
    document.title = title || "AI Playground";
  }, [title]);

  useEffect(() => {
    if (!localFlashes.length) return;

    const timers = localFlashes.map((f) =>
      setTimeout(() => {
        setLocalFlashes((prev) => prev.filter((x) => x.id !== f.id));
      }, 5000)
    );

    return () => timers.forEach(clearTimeout);
  }, [localFlashes.length]);

  const removeFlash = (id) => {
    setLocalFlashes((prev) => prev.filter((x) => x.id !== id));
  };

  const navClass = (key) => `nav-link${active === key ? " is-active" : ""}`;

  return (
    <div className="page">
      <header className="topbar">
        <div className="brand">
          <div className="brand-icon" aria-hidden="true" />
          <Link className="brand-text brand-link" to="/">
            AI Playground
          </Link>
        </div>

        <nav className="nav">
          <Link className={navClass("home")} to="/">
            Home
          </Link>
          <Link className={navClass("environments")} to="/environments">
            Environments
          </Link>
          <Link className={navClass("acm")} to="/acm">
            ACM
          </Link>

          {isAuthenticated ? (
            <>
              <Link className={navClass("profile")} to="/profile">
                Profile
              </Link>
              <Link className="nav-link" to="/logout">
                Logout
              </Link>
            </>
          ) : (
            <Link className={navClass("login")} to="/login">
              Login
            </Link>
          )}
        </nav>
      </header>

      {localFlashes.length > 0 && (
        <div className="flash-wrap">
          {localFlashes.map((f) => (
            <div
              key={f.id}
              className={`flash flash-${String(f.category || "info")}`}
              role="status"
              onClick={() => removeFlash(f.id)}
            >
              {f.message}
            </div>
          ))}
        </div>
      )}

      {children}
    </div>
  );
}

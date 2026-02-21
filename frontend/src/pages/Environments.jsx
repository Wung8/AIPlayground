// src/pages/Environments.jsx
import React from "react";
import { Link } from "react-router-dom";
import Layout from "../components/Layout";
import environments from "../data/environments.json";

function Stars({ n }) {
  const val = Math.max(0, Math.min(5, Number.isFinite(n) ? n : 0));
  return (
    <span aria-label={`difficulty ${val} out of 5`}>
      {"★".repeat(val)}
      {"☆".repeat(5 - val)}
    </span>
  );
}

function Sidebar({ selectedSlug = "" }) {
  return (
    <aside className="sidebar wide">
      <div className="side-section">
        <div className="side-title">User Documentation</div>
        <div className="side-item small">Installation</div>
        <div className="side-item small">Creating Agents</div>
        <div className="side-item small">Uploading Agents</div>
      </div>

      <div className="side-section">
        <div className="side-title">Environments</div>
        <div className="side-box">
          {environments.map((e) => (
            <Link
              key={e.slug}
              className={`side-item${e.slug === selectedSlug ? " is-active" : ""}`}
              to={`/environments/${e.slug}`}
            >
              {e.title}
            </Link>
          ))}
        </div>
      </div>
    </aside>
  );
}

export default function EnvironmentsPage({
  isAuthenticated = false,
  flashes = [],
}) {
  return (
    <Layout
      title="Environments"
      active="environments"
      isAuthenticated={isAuthenticated}
      flashes={flashes}
    >
      <div className="content">
        <Sidebar selectedSlug="" />

        <main className="main panel">
          <div className="panel-pad">
            <div className="panel-title">Environments</div>
            <div className="env-list">
              {environments.map((e) => (
                <div key={e.slug} className="env-card">
                  <div className="env-card-left">
                    <Link className="env-h2" to={`/environments/${e.slug}`}>
                      {e.title}
                    </Link>

                    <div className="env-diff">
                    <span className="env-diff-label">Difficulty:</span>
                    <span className="env-stars">
                      <Stars n={e.difficulty} />
                    </span>
                    </div>

                    <div className="env-desc">{e.description}</div>

                    <Link className="env-doc-link" to={`/environments/${e.slug}`}>
                      documentation
                    </Link>
                  </div>

                  <div className="env-card-right">
                    <Link to={`/play/${e.slug}`} className="env-img-link">
                      <div className="env-img" />
                    </Link>
                  </div>

                </div>
              ))}
            </div>
          </div>
        </main>
      </div>
    </Layout>
  );
}

// src/pages/EnvDoc.jsx
import React from "react";
import { Link, useParams, Navigate } from "react-router-dom";
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

function Sidebar({ activeSlug = "" }) {
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
              className={`side-item${e.slug === activeSlug ? " is-active" : ""}`}
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

export default function EnvDocPage({
  isAuthenticated = false,
  flashes = [],
}) {
  const { slug } = useParams();

  const s = String(slug || "").trim().toLowerCase();
  const env = environments.find((e) => e.slug === s) || null;

  if (!env) return <Navigate to="/environments" replace />;

  const title = `${env.title} Docs`;
  const docSections = Array.isArray(env.docSections) ? env.docSections : [];

  return (
    <div className="content">
    <Sidebar activeSlug={env.slug} />

    <main className="main">
        <div className="doc-header">
        <div className="doc-left">
            <Link className="back-link" to="/environments">
            Back
            </Link>

            <div className="doc-title-row">
            <div className="doc-title">{env.title}</div>
            <div className="doc-title-muted">Documentation</div>
            </div>

            <div className="doc-diff">
            <span className="doc-diff-label">Difficulty:</span>
            <span className="doc-stars">
                <Stars n={env.difficulty} />
            </span>
            </div>
        </div>

        <a className="doc-gh" href="/github">
            Github
        </a>
        </div>

        <div className="doc-canvas-wrap">
        <div className="doc-canvas" />
        </div>

        <div className="doc-play-wrap">
        <Link className="doc-play-btn" to={`/play/${env.slug}`}>
            Play now
        </Link>
        </div>

        <div className="doc-desc">
        <div className="doc-desc-h">Description</div>
        <div className="doc-desc-p">{env.description}</div>
        </div>

        {docSections.length > 0 && (
        <div className="doc-sections">
            {docSections
            .filter((sec) => String(sec?.title || "").trim().toLowerCase() !== "user documentation")
            .map((sec, idx) => (
                <div key={`${sec?.title || "section"}-${idx}`} className="doc-block">
                <div className="doc-h">{sec.title}</div>
                <ul className="doc-ul">
                    {(sec.items || []).map((it, j) => (
                    <li key={`${idx}-${j}`}>{it}</li>
                    ))}
                </ul>
                </div>
            ))}
        </div>
        )}
    </main>
    </div>
  );
}

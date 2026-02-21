// src/pages/Home.jsx
import React from "react";
import { Link } from "react-router-dom";
import Layout from "../components/Layout";

export default function Home({
  isAuthenticated = false,
  flashes = [],
}) {
  return (
    <Layout
      title="AI Playground"
      active="home"
      isAuthenticated={isAuthenticated}
      flashes={flashes}
    >
      <div className="home">
        <div className="home-hero">
          <div className="home-title">AI Playground</div>
          <div className="home-subtitle">
            A platform for learning and<br />
            experimenting with AI.
          </div>

          <div className="home-actions">
            <Link className="home-btn" to="/environments">
              Learn More
            </Link>
            <Link className="home-btn" to="/acm">
              About ACM
            </Link>
          </div>
        </div>

        <div className="home-footer">
          <a className="home-footer-link" href="/github">
            [ ] Github
          </a>
          <a className="home-footer-link" href="/discord">
            [ ] Discord
          </a>
          <a className="home-footer-link" href="/contact">
            [ ] Contact
          </a>
        </div>
      </div>
    </Layout>
  );
}

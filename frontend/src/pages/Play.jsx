// src/pages/Play.jsx
import React, { useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import "./play.css";

function TabButton({ active, onClick, children }) {
  return (
    <button
      type="button"
      className={`ap-tab ${active ? "is-active" : ""}`}
      onClick={onClick}
    >
      {children}
    </button>
  );
}

function BotRow({ bot, onRemove, removable }) {
  return (
    <div className="ap-bot-row">
      <div className="ap-bot-left">
        <div className="ap-bot-name">{bot.name}</div>
      </div>

      <div className="ap-bot-meta">
        <div className="ap-bot-meta-top">elo: {bot.elo}</div>
        <div className="ap-bot-meta-bottom">by: {bot.by}</div>
      </div>

      {removable ? (
        <button
          type="button"
          className="ap-bot-remove"
          aria-label={`remove ${bot.name}`}
          onClick={() => onRemove?.(bot.id)}
        >
          ×
        </button>
      ) : null}
    </div>
  );
}

export default function Play() {
  const { envSlug } = useParams();

  const envTitle = useMemo(() => {
    const slug = String(envSlug ?? "slime-volleyball")
      .replace(/[-_]+/g, " ")
      .trim();
    return slug
      .split(" ")
      .map((w) => (w ? w[0].toUpperCase() + w.slice(1) : w))
      .join(" ");
  }, [envSlug]);

  const [p1, setP1] = useState("player");
  const [p2, setP2] = useState("basicbot25");

  const [tab, setTab] = useState("browse"); // "browse" | "mybots"
  const [search, setSearch] = useState("");

  const [eloMin, setEloMin] = useState(0);
  const [eloMax, setEloMax] = useState(3000);

  const [selectedBots, setSelectedBots] = useState([
    { id: "epicbot", name: "epicbot", elo: 1400, by: "wung8" },
    { id: "basicbot25", name: "basicbot25", elo: 1000, by: "wung8" },
  ]);

  const maxBots = 3;

  const browseBots = useMemo(
    () => [
      { id: "epicbot", name: "epicbot", elo: 1400, by: "wung8" },
      { id: "basicbot25", name: "basicbot25", elo: 1000, by: "wung8" },
      { id: "another_bot2000", name: "another_bot2000", elo: 600, by: "wung8" },
      { id: "bot_zen", name: "bot_zen", elo: 1750, by: "kai" },
      { id: "fast_rnn", name: "fast_rnn", elo: 920, by: "sam" },
    ],
    []
  );

  const myBots = useMemo(
    () => [
      { id: "my_v1", name: "my_v1", elo: 880, by: "you" },
      { id: "my_v2", name: "my_v2", elo: 1210, by: "you" },
    ],
    []
  );

  const activeList = tab === "browse" ? browseBots : myBots;

  const filteredActive = useMemo(() => {
    const q = search.trim().toLowerCase();
    return activeList
      .filter((b) => (q ? b.name.toLowerCase().includes(q) : true))
      .filter((b) => b.elo >= eloMin && b.elo <= eloMax);
  }, [activeList, search, eloMin, eloMax]);

  function addBot(bot) {
    setSelectedBots((prev) => {
      if (prev.some((x) => x.id === bot.id)) return prev;
      if (prev.length >= maxBots) return prev;
      return [...prev, bot];
    });
  }

  function removeBot(id) {
    setSelectedBots((prev) => prev.filter((b) => b.id !== id));
  }

  const selectedCount = selectedBots.length;
  const atLimit = selectedCount >= maxBots;

  return (
    <div className="ap-play-page">
      <div className="ap-shell">
        <aside className="ap-side">
          <div className="ap-panel">
            <div className="ap-panel-title">Select Players:</div>

            <div className="ap-field-row">
              <div className="ap-field-label">P1:</div>
              <input
                className="ap-input"
                value={p1}
                onChange={(e) => setP1(e.target.value)}
              />
            </div>

            <div className="ap-field-row">
              <div className="ap-field-label">P2:</div>
              <input
                className="ap-input"
                value={p2}
                onChange={(e) => setP2(e.target.value)}
              />
              <div className="ap-elo-inline">elo: 1000</div>
            </div>

            <div className="ap-tabs">
              <TabButton active={tab === "browse"} onClick={() => setTab("browse")}>
                Browse
              </TabButton>
              <TabButton active={tab === "mybots"} onClick={() => setTab("mybots")}>
                My Bots
              </TabButton>
            </div>

            <div className="ap-search-row">
              <div className="ap-search-label">Search:</div>
              <input
                className="ap-input ap-search"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>

            <div className="ap-filter-row">
              <div className="ap-filter-label">Sort By:</div>
              <div className="ap-filter-pill">Elo</div>
              <div className="ap-filter-label">Elo Range:</div>
              <div className="ap-elo-range">
                <input
                  type="number"
                  className="ap-input ap-elo"
                  value={eloMin}
                  onChange={(e) => setEloMin(Number(e.target.value || 0))}
                />
                <span className="ap-elo-dash">-</span>
                <input
                  type="number"
                  className="ap-input ap-elo"
                  value={eloMax}
                  onChange={(e) => setEloMax(Number(e.target.value || 0))}
                />
              </div>
            </div>

            <div className="ap-bot-list">
              {filteredActive.map((b) => (
                <button
                  key={b.id}
                  type="button"
                  className={`ap-bot-pick ${atLimit ? "is-disabled" : ""}`}
                  onClick={() => addBot(b)}
                  disabled={atLimit}
                  title={atLimit ? "maximum bots selected" : "add bot"}
                >
                  <div className="ap-bot-pick-inner">
                    <div className="ap-bot-pick-name">{b.name}</div>
                    <div className="ap-bot-pick-meta">
                      <div>elo: {b.elo}</div>
                      <div>by: {b.by}</div>
                    </div>
                  </div>
                </button>
              ))}
            </div>

            <div className="ap-selected">
              {selectedBots.map((b) => (
                <BotRow
                  key={b.id}
                  bot={b}
                  removable
                  onRemove={removeBot}
                />
              ))}

              {atLimit ? (
                <div className="ap-limit-note">
                  Maximum of {maxBots} bots allowed
                  <br />
                  per environment
                </div>
              ) : (
                <button
                  type="button"
                  className="ap-add-btn"
                  onClick={() => {
                    const next = filteredActive.find(
                      (b) => !selectedBots.some((x) => x.id === b.id)
                    );
                    if (next) addBot(next);
                  }}
                  aria-label="add bot"
                >
                  +
                </button>
              )}
            </div>

            <div className="ap-signin-hint">Sign in to upload bots</div>
          </div>
        </aside>

        <main className="ap-main">
          <div className="ap-topline">
            <Link className="ap-back" to="/environments">
              Back
            </Link>
          </div>

          <h1 className="ap-title">{envTitle}</h1>

          <div className="ap-stage">
            <div className="ap-canvas-shell" aria-label="game canvas region">
              <div className="ap-canvas-placeholder" />
            </div>

            <div className="ap-controls">
              <button type="button" className="ap-ctrl-btn">
                Reset
              </button>

              <label className="ap-debug">
                <span>Debug</span>
                <input type="checkbox" />
              </label>

              <button type="button" className="ap-ctrl-btn">
                Fullscreen
              </button>
            </div>

            <div className="ap-bottom-panel" />
          </div>
        </main>
      </div>
    </div>
  );
}

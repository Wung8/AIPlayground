// src/pages/Play.jsx
import React, { useMemo, useRef, useState } from "react";
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

function BotTile({ bot, onPick, disabled = false }) {
  return (
    <button
      type="button"
      className={`ap-bot-pick ${disabled ? "is-disabled" : ""}`}
      onClick={() => {
        if (!disabled) onPick?.(bot);
      }}
      disabled={disabled}
      title={disabled ? "no bot" : "select bot"}
    >
      <div className="ap-bot-pick-inner">
        <div className="ap-bot-pick-name">{bot?.name ?? "—"}</div>
        <div className="ap-bot-pick-meta">
          <div>elo: {bot?.elo ?? "—"}</div>
          <div>by: {bot?.by ?? "—"}</div>
        </div>
      </div>
    </button>
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

  const [selectedPlayer, setSelectedPlayer] = useState(1); // 1 | 2 | null
  const [tab, setTab] = useState("browse"); // "browse" | "mybots"
  const [search, setSearch] = useState("");

  const [eloMin, setEloMin] = useState(0);
  const [eloMax, setEloMax] = useState(3000);

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
    if (tab !== "browse") return activeList;

    const q = search.trim().toLowerCase();
    return activeList
      .filter((b) => (q ? b.name.toLowerCase().includes(q) : true))
      .filter((b) => b.elo >= eloMin && b.elo <= eloMax);
  }, [tab, activeList, search, eloMin, eloMax]);

  function assignToSelectedPlayer(bot) {
    if (!bot) return;

    if (selectedPlayer === 1) {
      setP1(bot.name);
      setSelectedPlayer(2);
      return;
    }

    if (selectedPlayer === 2) {
      setP2(bot.name);
      setSelectedPlayer(null);
      return;
    }

    // if neither is selected, default to p1
    setP1(bot.name);
    setSelectedPlayer(2);
  }

  async function uploadAgentFile(file) {
    const formData = new FormData();
    formData.append("file", file);

    // default agent name is filename (backend also defaults if name is omitted)
    const baseName = file.name.replace(/\.py$/i, "");
    const url = `/agents/upload?name=${encodeURIComponent(baseName)}`;

    const res = await fetch(url, {
      method: "POST",
      body: formData,
      credentials: "include",
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      throw new Error(data?.error || "upload failed");
    }

    return data;
  }


  const fileInputRef = useRef(null);

  return (
    <div className="ap-play-page">
      <div className="ap-shell">
        <aside className="ap-side">
          <div className="ap-panel">
            <div className="ap-panel-title">Select Players:</div>

            <div className="ap-field-row">
              <div className="ap-field-label">P1:</div>
              <input
                className={`ap-input ${selectedPlayer === 1 ? "is-selected" : ""}`}
                value={p1}
                onChange={(e) => setP1(e.target.value)}
                onClick={() => setSelectedPlayer(1)}
              />
            </div>

            <div className="ap-field-row">
              <div className="ap-field-label">P2:</div>
              <input
                className={`ap-input ${selectedPlayer === 2 ? "is-selected" : ""}`}
                value={p2}
                onChange={(e) => setP2(e.target.value)}
                onClick={() => setSelectedPlayer(2)}
              />
              <div className="ap-elo-inline">elo: 1000</div>
            </div>

            <div className="ap-tabs">
              <TabButton
                active={tab === "browse"}
                onClick={() => {
                  setTab("browse");
                }}
              >
                Browse
              </TabButton>
              <TabButton
                active={tab === "mybots"}
                onClick={() => {
                  setTab("mybots");
                }}
              >
                My Bots
              </TabButton>
            </div>

            {tab === "browse" ? (
              <>
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
                  <BotTile
                    bot={filteredActive[0] ?? null}
                    disabled={!filteredActive[0]}
                    onPick={assignToSelectedPlayer}
                  />
                  <BotTile
                    bot={filteredActive[1] ?? null}
                    disabled={!filteredActive[1]}
                    onPick={assignToSelectedPlayer}
                  />
                  <BotTile
                    bot={filteredActive[2] ?? null}
                    disabled={!filteredActive[2]}
                    onPick={assignToSelectedPlayer}
                  />
                </div>
              </>
            ) : (
              <>
                <div className="ap-bot-list">
                  {myBots.map((b) => (
                    <BotTile key={b.id} bot={b} onPick={assignToSelectedPlayer} />
                  ))}

                  <input
                    ref={fileInputRef}
                    type="file"
                    style={{ display: "none" }}
                    onChange={async (e) => {
                      const file = e.target.files?.[0];
                      if (!file) return;

                      try {
                        const created = await uploadAgentFile(file);
                        console.log("uploaded:", created);
                      } catch (err) {
                        console.error(err);
                        alert(String(err.message || err));
                      } finally {
                        // allow re-selecting the same file later
                        e.target.value = "";
                      }
                    }}
                  />

                  <button
                    type="button"
                    className="ap-add-btn"
                    onClick={() => fileInputRef.current?.click()}
                    aria-label="upload bot"
                    title="upload bot"
                  >
                    +
                  </button>
                </div>
              </>
            )}
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

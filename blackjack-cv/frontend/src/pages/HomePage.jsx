import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getPlayerProfile, savePlayerProfile } from "../utils/storage";

export default function HomePage() {
  const navigate = useNavigate();
  const [playerName, setPlayerName] = useState("");
  const [note, setNote] = useState("");

  useEffect(() => {
    const profile = getPlayerProfile();
    setPlayerName(profile.playerName || "");
    setNote(profile.note || "");
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    const cleanName = playerName.trim();

    if (!cleanName) {
      alert("Please enter your player name.");
      return;
    }

    savePlayerProfile({
      playerName: cleanName,
      note: note.trim(),
    });

    navigate("/game");
  };

  return (
    <section className="page page--home">
      <div className="content-card">
        <h1>Blackjack CV Project</h1>
        <p>
          This React application combines blackjack gameplay, camera-based card
          recognition, match history, and local persistence.
        </p>

        <form className="player-form" onSubmit={handleSubmit}>
          <label className="form-group">
            <span>Player Name</span>
            <input
              type="text"
              value={playerName}
              onChange={(e) => setPlayerName(e.target.value)}
              placeholder="Enter your name"
            />
          </label>

          <label className="form-group">
            <span>Session Note</span>
            <textarea
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder="Optional note about this session"
              rows="4"
            />
          </label>

          <button type="submit" className="primary-btn">
            Start Game
          </button>
        </form>
      </div>
    </section>
  );
}
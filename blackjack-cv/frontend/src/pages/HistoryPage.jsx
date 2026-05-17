import React, { useEffect, useState } from "react";
import {
  getMatchHistory,
  updateMatchRecord,
  deleteMatchRecord,
  clearMatchHistory,
} from "../utils/storage";

function getResultType(result) {
  if (result === "player_wins" || result === "blackjack") return "win";
  if (result === "dealer_wins" || result === "bust") return "loss";
  return "push";
}

function formatResultLabel(result) {
  if (result === "player_wins") return "Win";
  if (result === "dealer_wins") return "Loss";
  if (result === "blackjack") return "Blackjack";
  if (result === "bust") return "Bust";
  if (result === "push") return "Push";
  return result;
}

function formatAmount(amount) {
  if (amount > 0) return `+$${amount}`;
  if (amount < 0) return `-$${Math.abs(amount)}`;
  return `$${amount}`;
}

export default function HistoryPage() {
  const [history, setHistory] = useState([]);
  const [editingId, setEditingId] = useState(null);
  const [editNote, setEditNote] = useState("");

  useEffect(() => {
    setHistory(getMatchHistory());
  }, []);

  const startEdit = (item) => {
    setEditingId(item.id);
    setEditNote(item.note || "");
  };

  const saveEdit = (id) => {
    const updated = updateMatchRecord(id, { note: editNote.trim() });
    setHistory(updated);
    setEditingId(null);
    setEditNote("");
  };

  const handleDelete = (id) => {
    const updated = deleteMatchRecord(id);
    setHistory(updated);
  };

  const handleClearAll = () => {
    const updated = clearMatchHistory();
    setHistory(updated);
  };

  return (
    <section className="page">
      <div className="content-card">
        <div className="page-header-row">
          <h1>Match History</h1>
          {history.length > 0 && (
            <button className="danger-btn" onClick={handleClearAll}>
              Clear All
            </button>
          )}
        </div>

        {history.length === 0 ? (
          <p>No matches saved yet.</p>
        ) : (
          <div className="history-list">
            {history.map((item) => {
              const resultType = getResultType(item.result);

              return (
                <div
                  key={item.id}
                  className={`history-card history-card--${resultType}`}
                >
                  <div className="history-card__top">
                    <h3>{item.playerName}</h3>
                    <span>{item.date}</span>
                  </div>

                  <div className="history-result-row">
                    <span
                      className={`history-result-badge history-result-badge--${resultType}`}
                    >
                      {formatResultLabel(item.result)}
                    </span>
                  </div>

                  <p>Bet: ${item.bet}</p>
                  <p
                    className={
                      item.amount > 0
                        ? "history-amount history-amount--positive"
                        : item.amount < 0
                        ? "history-amount history-amount--negative"
                        : "history-amount"
                    }
                  >
                    Balance Change: {formatAmount(item.amount)}
                  </p>

                  {editingId === item.id ? (
                    <div className="edit-block">
                      <textarea
                        value={editNote}
                        onChange={(e) => setEditNote(e.target.value)}
                        rows="3"
                      />
                      <div className="history-actions">
                        <button
                          className="primary-btn"
                          onClick={() => saveEdit(item.id)}
                        >
                          Save
                        </button>
                        <button
                          className="secondary-btn"
                          onClick={() => setEditingId(null)}
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <p>Note: {item.note || "No note"}</p>
                      <div className="history-actions">
                        <button
                          className="secondary-btn"
                          onClick={() => startEdit(item)}
                        >
                          Edit
                        </button>
                        <button
                          className="danger-btn"
                          onClick={() => handleDelete(item.id)}
                        >
                          Delete
                        </button>
                      </div>
                    </>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </section>
  );
}
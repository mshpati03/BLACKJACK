import React from "react";

const RESULT_CONFIG = {
  blackjack:    { label: "BLACKJACK!", emoji: "🃏", cls: "result--blackjack", sub: "Natural 21 pays 3:2" },
  player_wins:  { label: "YOU WIN",    emoji: "✓",  cls: "result--win",       sub: null },
  dealer_wins:  { label: "DEALER WINS",emoji: null, cls: "result--lose",      sub: null },
  push:         { label: "PUSH",       emoji: null, cls: "result--push",      sub: "Bet returned" },
  bust:         { label: "BUST",       emoji: null, cls: "result--bust",      sub: "Over 21" },
};

export default function ResultModal({ result, resultAmount, onNewRound }) {
  if (!result) return null;

  const config = RESULT_CONFIG[result] || { label: result.toUpperCase(), cls: "" };

  const amountLabel =
    result === "push"
      ? null
      : resultAmount > 0
      ? `+$${resultAmount.toLocaleString()}`
      : resultAmount < 0
      ? `-$${Math.abs(resultAmount).toLocaleString()}`
      : null;

  return (
    <div className="modal-backdrop">
      <div className={`result-modal ${config.cls}`}>
        <div className="result-modal__title">
          {config.label}
          {config.emoji && (
            <span style={{ marginLeft: "0.3em", fontSize: "0.85em" }}>{config.emoji}</span>
          )}
        </div>

        {amountLabel && (
          <div className="result-modal__amount">{amountLabel}</div>
        )}

        {config.sub && (
          <div className="result-modal__sub">{config.sub}</div>
        )}

        <button className="btn btn--new-round" onClick={onNewRound}>
          New Round
        </button>
      </div>
    </div>
  );
}

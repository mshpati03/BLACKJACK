import React, { useState } from "react";
import axios from "axios";
import BetInput, { MIN_BET, parseBetAmount } from "./BetInput";

const QUICK_CHIPS = [
  { amount: 5,   chipColor: "red"   },
  { amount: 25,  chipColor: "green" },
  { amount: 50,  chipColor: "blue"  },
  { amount: 100, chipColor: "dark"  },
];


/**
 * Betting UI grouped like the reference: curved teal header, one compact card body.
 */
export default function BettingPanel({ balance, onBetPlaced }) {
  const [betInput, setBetInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const parsedPreview = (() => {
    const trimmed = betInput.trim();
    if (!trimmed || !/^\d+$/.test(trimmed)) return null;
    const n = parseInt(trimmed, 10);
    if (n < MIN_BET || n > balance) return null;
    return n;
  })();

  const quickAdd = (delta) => {
    setError(null);
    setBetInput((prev) => {
      const base = /^\d+$/.test(prev) ? parseInt(prev, 10) : 0;
      const next = Math.min(balance, Math.max(0, base + delta));
      return next > 0 ? String(next) : "";
    });
  };

  const setMax = () => {
    setError(null);
    setBetInput(String(balance));
  };

  const clearBet = () => {
    setBetInput("");
    setError(null);
  };

  const handleDeal = async () => {
    const result = parseBetAmount(betInput, balance);
    if (result.error) {
      setError(result.error);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await axios.post("/api/bet", { amount: result.amount });
      setBetInput("");
      onBetPlaced(res.data);
    } catch (err) {
      const msg =
        err.response?.data?.error ||
        "Failed to place bet. Check backend connection.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const dealDisabled =
    loading || !parsedPreview || parsedPreview < MIN_BET || parsedPreview > balance;

  return (
    <section className="bet-panel-outer" aria-label="Betting">
      <div className="bet-panel">
        <header className="bet-panel__banner">
          <span className="bet-panel__you">You</span>
          <div className="bet-panel__balance-stack">
            <span className="bet-panel__balance-label">Balance</span>
            <span className="bet-panel__balance" aria-label="Balance">
              ${balance.toLocaleString()}
            </span>
          </div>
        </header>

        <div className="bet-panel__body">
          {parsedPreview != null && (
            <p className="bet-panel__wager-preview" aria-live="polite">
              Wager <strong>${parsedPreview.toLocaleString()}</strong>
            </p>
          )}

          <BetInput
            value={betInput}
            onChange={(v) => {
              setBetInput(v);
              setError(null);
            }}
            balance={balance}
            disabled={loading}
            error={error}
          />

          <div className="bet-quick-add" role="group" aria-label="Quick add to wager">
            <span className="bet-quick-add__label">Quick add</span>
            <div className="bet-quick-add__grid">
              {QUICK_CHIPS.map(({ amount, chipColor }) => (
                <button
                  key={amount}
                  type="button"
                  className={`btn--chip btn--chip--${chipColor}`}
                  onClick={() => quickAdd(amount)}
                  disabled={loading}
                >
                  +${amount}
                </button>
              ))}
            </div>
            <button
              type="button"
              className="btn--quick-max"
              onClick={setMax}
              disabled={loading || balance <= 0}
              aria-label={`Bet all — $${balance.toLocaleString()}`}
            >
              <span>ALL IN</span>
              <span style={{ opacity: 0.7, fontSize: "0.65rem" }}>${balance.toLocaleString()}</span>
            </button>
          </div>

          {error && <div className="betting-error betting-error--ref">{error}</div>}

          <div className="betting-actions betting-actions--ref">
            <button
              type="button"
              className="btn btn--clear btn--clear--ref"
              onClick={clearBet}
              disabled={loading}
            >
              Clear
            </button>
            <button
              type="button"
              className="btn btn--deal btn--deal--ref"
              onClick={handleDeal}
              disabled={dealDisabled}
            >
              {loading ? "Capturing…" : "Deal"}
            </button>
          </div>

          {loading && (
            <p className="betting-info betting-info--ref">
              Show each card to the camera when prompted.
            </p>
          )}
        </div>
      </div>
    </section>
  );
}

import React, { useCallback, useState } from "react";
import axios from "axios";
import StrategyAdvisor from "./StrategyAdvisor";


const DISABLED_PHASES = new Set([
  "dealer_turn",
  "round_over",
  "waiting_for_player_card",
  "waiting_for_dealer_card",
  "betting",
]);


export default function PlayerControls({ gameState, onStateChange, variant = "dock" }) {
  const [error, setError] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);
  const onTable = variant === "on-table";

  const sendAction = useCallback(
    async (action) => {
      setActionLoading(true);
      setError(null);
      try {
        const res = await axios.post("/api/action", { action });
        onStateChange(res.data);
      } catch (err) {
        const msg = err.response?.data?.error || "Action failed.";
        setError(msg);
      } finally {
        setActionLoading(false);
      }
    },
    [onStateChange]
  );

  if (!gameState) return null;

  const { game_phase, can_double, can_split, strategy_recommendation, active_hand, split_hand } = gameState;

  const buttonsDisabled = DISABLED_PHASES.has(game_phase) || actionLoading;
  const hasSplit = split_hand && split_hand.length > 0;
  const standLabel = hasSplit && active_hand === "player" ? "NEXT HAND" : "STAND";

  if (onTable) {
    return (
      <div className="table-action-bar table-action-bar--ref" aria-label="Game actions">
        <div className="table-action-bar__main">
          <button
            type="button"
            className="btn-table btn-table--hit"
            onClick={() => sendAction("hit")}
            disabled={buttonsDisabled}
          >
            {actionLoading ? "…" : "HIT"}
          </button>
          <button
            type="button"
            className="btn-table btn-table--stand"
            onClick={() => sendAction("stand")}
            disabled={buttonsDisabled}
          >
            {actionLoading ? "…" : standLabel}
          </button>
        </div>

        <div className="table-action-bar__secondary">
          {can_double && (
            <button
              type="button"
              className="btn-table btn-table--double"
              onClick={() => sendAction("double_down")}
              disabled={buttonsDisabled}
            >
              DOUBLE DOWN
            </button>
          )}

          {can_split && (
            <button
              type="button"
              className="btn-table btn-table--split"
              onClick={() => sendAction("split")}
              disabled={buttonsDisabled}
            >
              SPLIT
            </button>
          )}
        </div>

        {game_phase === "player_turn" && (
          <StrategyAdvisor recommendation={strategy_recommendation} />
        )}

        {error && <div className="action-error action-error--inline">{error}</div>}
      </div>
    );
  }

  return (
    <section className="controls-dock controls-dock--play" aria-label="Game actions">
      <div className="action-row action-row--dock">
        <button
          type="button"
          className="btn btn--hit"
          onClick={() => sendAction("hit")}
          disabled={buttonsDisabled}
        >
          HIT
        </button>
        <button
          type="button"
          className="btn btn--stand"
          onClick={() => sendAction("stand")}
          disabled={buttonsDisabled}
        >
          {standLabel}
        </button>
        <button
          type="button"
          className="btn btn--double"
          onClick={() => sendAction("double_down")}
          disabled={buttonsDisabled || !can_double}
        >
          DOUBLE DOWN
        </button>
        {can_split && (
          <button
            type="button"
            className="btn btn--split"
            onClick={() => sendAction("split")}
            disabled={buttonsDisabled}
          >
            SPLIT
          </button>
        )}
      </div>

      {game_phase === "player_turn" && (
        <StrategyAdvisor recommendation={strategy_recommendation} />
      )}

      {error && <div className="action-error">{error}</div>}
    </section>
  );
}
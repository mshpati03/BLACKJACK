import React, { useCallback, useState } from "react";
import axios from "axios";
import CardDisplay from "./CardDisplay";
import ResultModal from "./ResultModal";
import { formatScore } from "../utils/cardUtils";


const WAITING_PHASES = new Set(["waiting_for_player_card", "waiting_for_dealer_card"]);


function tableStatusMessage(gamePhase, isBetting, activeHand) {
  if (isBetting) return "Place your wager below, then deal.";
  if (gamePhase === "player_turn") return activeHand === "split" ? "Playing second hand…" : null;
  if (gamePhase === "dealer_turn") return "Dealer is playing…";
  if (WAITING_PHASES.has(gamePhase)) return "Follow the on-screen prompt.";
  if (gamePhase === "round_over") return null;
  return null;
}


function ChipRack() {
  const stacks = [
    { top: "#3ddc84", bottom: "#1e8f52" },
    { top: "#4da3ff", bottom: "#2563c8" },
    { top: "#3a4556", bottom: "#1c2433" },
    { top: "#ff5c5c", bottom: "#c42e2e" },
    { top: "#6ab7ff", bottom: "#2563c8" },
  ];
  return (
    <div className="chip-rack chip-rack--ref" aria-hidden="true">
      {stacks.map((c, i) => (
        <div key={i} className="chip-rack__stack">
          <span className="chip-rack__disc chip-rack__disc--3" style={{ background: c.bottom }} />
          <span className="chip-rack__disc chip-rack__disc--2" style={{ background: c.top }} />
          <span className="chip-rack__disc chip-rack__disc--1" style={{ background: c.bottom }} />
        </div>
      ))}
    </div>
  );
}


function FeltGuidelines() {
  return (
    <div className="game-table__felt-lines" aria-hidden="true">
      <div className="felt-guideline felt-guideline--outer" />
      <div className="felt-guideline felt-guideline--inner" />
    </div>
  );
}


function FeltCoinsDecor() {
  return (
    <div className="felt-coins" aria-hidden="true">
      <span className="felt-coin felt-coin--c1" />
      <span className="felt-coin felt-coin--c2" />
      <span className="felt-coin felt-coin--c3" />
      <span className="felt-coin felt-coin--c4" />
      <span className="felt-coin felt-coin--c5" />
      <span className="felt-coin felt-coin--c6" />
    </div>
  );
}


export default function GameTable({ gameState, onStateChange, isBetting, children }) {
  const [error, setError] = useState(null);

  const handleNewRound = useCallback(async () => {
    setError(null);
    try {
      const res = await axios.post("/api/new_round");
      onStateChange(res.data);
    } catch (err) {
      setError("Failed to start new round.");
    }
  }, [onStateChange]);

  if (!gameState) {
    return (
      <div className="game-table-shell game-table-shell--ref">
        <div className="game-table game-table--ref game-table--loading">
          <div className="loading">Loading game…</div>
        </div>
      </div>
    );
  }

  const {
    player_hand = [],
    dealer_hand = [],
    split_hand = [],
    player_score,
    split_score,
    dealer_score_visible,
    dealer_score_final,
    game_phase,
    result,
    result_amount,
    split_result,
    split_result_amount,
    balance,
    current_bet,
    split_bet,
    active_hand,
  } = gameState;

  const showResult = game_phase === "round_over";
  const dealerScore = dealer_score_final != null ? dealer_score_final : dealer_score_visible;
  const statusMsg = tableStatusMessage(game_phase, isBetting, active_hand);
  const hasSplit = split_hand && split_hand.length > 0;

  return (
    <div className="game-table-shell game-table-shell--ref">
      <div className="table-shell-header" aria-label="Blackjack 21">
        <span className="table-shell-header__title">Blackjack</span>
        <span className="table-shell-header__badge">21</span>
      </div>

      <div className="game-table game-table--ref">
        <div className="game-table__rim" aria-hidden="true" />
        <FeltGuidelines />
        <FeltCoinsDecor />

        <div className="game-table__inner">
          <ChipRack />

          <div className="table-hud-mini table-hud-mini--ref">
            <span className="table-hud-mini__item">
              BALANCE <strong>${balance.toLocaleString()}</strong>
            </span>
            <span className="table-hud-mini__dot" aria-hidden />
            <span className="table-hud-mini__item">
              BET <strong>${current_bet.toLocaleString()}</strong>
            </span>
            {hasSplit && (
              <>
                <span className="table-hud-mini__dot" aria-hidden />
                <span className="table-hud-mini__item">
                  SPLIT BET <strong>${split_bet?.toLocaleString()}</strong>
                </span>
              </>
            )}
          </div>

          {statusMsg && (
            <p className="table-status-line table-status-line--compact" role="status">
              {statusMsg}
            </p>
          )}

          {/* Dealer hand */}
          <div className="table-hand-block table-hand-block--dealer">
            <div className="hand-block-header">
              <span className="section-label section-label--ref">Dealer</span>
              {dealerScore != null && dealerScore > 0 && (
                <span className="score-badge" aria-label="Dealer score">
                  {formatScore(dealerScore)}
                </span>
              )}
            </div>
            <div className="hand-row hand-row--table">
              {dealer_hand.length > 0 ? (
                dealer_hand.map((card, i) => (
                  <CardDisplay
                    key={`dealer-${i}-${card.label}`}
                    rank={card.rank}
                    suit={card.suit}
                    faceDown={card.hidden}
                  />
                ))
              ) : (
                <>
                  <div className="card-slot" aria-hidden="true" />
                  <div className="card-slot" aria-hidden="true" />
                </>
              )}
            </div>
          </div>

          <div className="table-center-divider" aria-hidden="true" />

          {/* Player hands — side by side if split */}
          <div className={`table-hands-row${hasSplit ? " table-hands-row--split" : ""}`}>

            {/* Main hand */}
            <div className={`table-hand-block table-hand-block--player${hasSplit && active_hand === "player" && game_phase !== "round_over" ? " table-hand-block--active" : ""}${hasSplit && active_hand === "split" && game_phase !== "round_over" ? " table-hand-block--inactive" : ""}`}>
              <div className="hand-block-header">
                <span className="section-label section-label--ref">
                  {hasSplit ? "Hand 1" : "You"}
                </span>
                {player_score != null && player_score > 0 && (
                  <span className="score-badge" aria-label="Your score">
                    {formatScore(player_score)}
                  </span>
                )}
                {hasSplit && showResult && result && (
                  <span className={`result-chip result-chip--${result}`}>
                    {result === "player_wins" ? "WIN" : result === "push" ? "PUSH" : "LOSE"}
                  </span>
                )}
              </div>
              <div className="hand-row hand-row--table">
                {player_hand.length > 0 ? (
                  player_hand.map((card, i) => (
                    <CardDisplay
                      key={`player-${i}-${card.label}`}
                      rank={card.rank}
                      suit={card.suit}
                      faceDown={card.hidden}
                    />
                  ))
                ) : (
                  <>
                    <div className="card-slot" aria-hidden="true" />
                    <div className="card-slot" aria-hidden="true" />
                  </>
                )}
              </div>
            </div>

            {/* Split hand */}
            {hasSplit && (
              <div className={`table-hand-block table-hand-block--player${active_hand === "split" && game_phase !== "round_over" ? " table-hand-block--active" : ""}${active_hand === "player" && game_phase !== "round_over" ? " table-hand-block--inactive" : ""}`}>
                <div className="hand-block-header">
                  <span className="section-label section-label--ref">Hand 2</span>
                  {split_score != null && split_score > 0 && (
                    <span className="score-badge" aria-label="Split score">
                      {formatScore(split_score)}
                    </span>
                  )}
                  {showResult && split_result && (
                    <span className={`result-chip result-chip--${split_result}`}>
                      {split_result === "player_wins" ? "WIN" : split_result === "push" ? "PUSH" : "LOSE"}
                    </span>
                  )}
                </div>
                <div className="hand-row hand-row--table">
                  {split_hand.map((card, i) => (
                    <CardDisplay
                      key={`split-${i}-${card.label}`}
                      rank={card.rank}
                      suit={card.suit}
                      faceDown={card.hidden}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>

          {children}

          {error && <div className="action-error action-error--table">{error}</div>}

          {showResult && (
            <ResultModal
              result={result}
              resultAmount={result_amount}
              splitResult={split_result}
              splitResultAmount={split_result_amount}
              onNewRound={handleNewRound}
            />
          )}
        </div>
      </div>
    </div>
  );
}
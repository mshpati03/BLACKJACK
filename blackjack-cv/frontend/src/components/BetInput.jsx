import React from "react";

export const MIN_BET = 5;

/**
 * Parse a bet string for whole-dollar amounts (matches backend int bets).
 * Returns { amount: number } or { error: string }.
 */
export function parseBetAmount(raw, balance) {
  const trimmed = String(raw ?? "").trim();
  if (trimmed === "") {
    return { error: "Enter a bet amount." };
  }
  if (!/^\d+$/.test(trimmed)) {
    return { error: "Use a whole dollar amount (no decimals)." };
  }
  const amount = parseInt(trimmed, 10);
  if (amount < MIN_BET) {
    return { error: `Minimum bet is $${MIN_BET}.` };
  }
  if (amount > balance) {
    return { error: "Bet cannot exceed your balance." };
  }
  return { amount };
}

/**
 * Controlled numeric bet field with validation messaging on demand.
 * Props:
 *   value, onChange
 *   balance — max allowed
 *   disabled
 *   error — external error string (e.g. API)
 *   id — optional for label association
 */
export default function BetInput({
  id = "bet-amount-input",
  value,
  onChange,
  balance,
  disabled,
  error: externalError,
}) {
  return (
    <div className="bet-input">
      <label className="bet-input__label" htmlFor={id}>
        Wager ($)
      </label>
      <input
        id={id}
        type="text"
        inputMode="numeric"
        pattern="[0-9]*"
        autoComplete="off"
        className="bet-input__field"
        placeholder={`Min $${MIN_BET}`}
        value={value}
        onChange={(e) => onChange(e.target.value.replace(/\D/g, ""))}
        disabled={disabled}
        aria-invalid={Boolean(externalError)}
      />
      <div className="bet-input__hint">
        Whole dollars only · min ${MIN_BET} · max ${balance.toLocaleString()}
      </div>
    </div>
  );
}

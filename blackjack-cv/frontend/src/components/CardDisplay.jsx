import React, { useEffect, useState } from "react";
import { getSuitSymbol, getCardColor, rankAbbr } from "../utils/cardUtils";

export default function CardDisplay({ rank, suit, faceDown = false, small = false }) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setVisible(true), 30);
    return () => clearTimeout(t);
  }, []);

  const sizeClass = small ? "card card--small" : "card";
  const animClass = visible ? "card--visible" : "";

  if (faceDown) {
    return (
      <div className={`${sizeClass} card--facedown ${animClass}`} aria-label="Face-down card">
        <div className="card__back-pattern" />
      </div>
    );
  }

  if (!rank || !suit) return null;

  const color = getCardColor(suit);
  const symbol = getSuitSymbol(suit);
  const abbr = rankAbbr(rank);
  const label = `${abbr} of ${suit}`;

  return (
    <div className={`${sizeClass} ${animClass}`} style={{ color }} aria-label={label}>
      <div className="card__corner card__corner--tl">
        <span className="card__rank">{abbr}</span>
        <span className="card__suit-sm">{symbol}</span>
      </div>
      <div className="card__center">
        <span className="card__suit-lg">{symbol}</span>
      </div>
      <div className="card__corner card__corner--br">
        <span className="card__rank">{abbr}</span>
        <span className="card__suit-sm">{symbol}</span>
      </div>
    </div>
  );
}

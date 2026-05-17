import React from "react";

const COLOR_MAP = {
  HIT: "#00e5ff",
  STAND: "#00c853",
  "DOUBLE DOWN": "#ffd600",
};

/**
 * StrategyAdvisor shows the basic strategy recommendation during player turn.
 * Props:
 *   recommendation - "HIT" | "STAND" | "DOUBLE DOWN" | null
 */
export default function StrategyAdvisor({ recommendation }) {
  if (!recommendation) return null;

  const color = COLOR_MAP[recommendation] || "#ffffff";

  return (
    <div className="strategy-advisor">
      <span className="strategy-label">Recommended:</span>
      <span className="strategy-action" style={{ color }}>
        {recommendation}
      </span>
    </div>
  );
}

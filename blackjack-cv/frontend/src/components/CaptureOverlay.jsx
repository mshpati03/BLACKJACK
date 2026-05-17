import React from "react";

export default function CaptureOverlay({ promptMessage }) {
  return (
    <div className="capture-overlay">
      <div className="capture-overlay__box">
        <div className="capture-overlay__prompt">
          {promptMessage || "Show card to camera…"}
        </div>
        <div className="capture-overlay__ring">
          <svg width="40" height="40" viewBox="0 0 100 100">
            <circle
              className="capture-ring-bg"
              cx="50" cy="50" r="40"
              fill="none" strokeWidth="6"
            />
            <circle
              className="capture-ring-pulse"
              cx="50" cy="50" r="40"
              fill="none" strokeWidth="6"
              strokeDasharray="60 190"
              strokeLinecap="round"
              transform="rotate(-90 50 50)"
            >
              <animateTransform
                attributeName="transform"
                type="rotate"
                from="-90 50 50"
                to="270 50 50"
                dur="1.2s"
                repeatCount="indefinite"
              />
            </circle>
          </svg>
          <div className="capture-overlay__countdown">👁</div>
        </div>
        <div className="capture-overlay__sub">Hold card steady</div>
      </div>
    </div>
  );
}
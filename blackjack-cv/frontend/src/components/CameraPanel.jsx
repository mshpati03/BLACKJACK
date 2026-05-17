import React, { useEffect, useRef, useState, useCallback } from "react";
import { io } from "socket.io-client";
import CardDisplay from "./CardDisplay";
import { parseCardLabel } from "../utils/cardUtils";

const SOCKET_URL =
  process.env.REACT_APP_BACKEND_URL || "http://localhost:5001";

/**
 * Sidebar: live camera + detected card (reference: two-tone DETECTED header).
 */
export default function CameraPanel({ onDetection }) {
  const [frame, setFrame] = useState(null);
  const [detectedCard, setDetectedCard] = useState(null);
  const [confidence, setConfidence] = useState(0);
  const [pipeline, setPipeline] = useState(null);
  const socketRef = useRef(null);
  const holdRef = useRef({ label: null, conf: 0, miss: 0 });
  const CLIENT_HOLD_CLEAR = 4;

  const applyClientHold = useCallback((label, conf) => {
    const h = holdRef.current;
    if (label) {
      h.miss = 0;
      h.label = label;
      h.conf = conf;
      return { label, conf };
    }
    h.miss += 1;
    if (h.miss >= CLIENT_HOLD_CLEAR) {
      h.label = null;
      h.conf = 0;
      return { label: null, conf: 0 };
    }
    return { label: h.label, conf: h.conf };
  }, []);

  useEffect(() => {
    const socket = io(SOCKET_URL, { transports: ["websocket"] });
    socketRef.current = socket;

    socket.on("camera_stream", (data) => {
      if (data.frame) setFrame(data.frame);
      if (data.pipeline) setPipeline(data.pipeline);
      const rawLabel = data.detected_card || null;
      const rawConf = data.confidence || 0;
      const { label, conf } = applyClientHold(rawLabel, rawConf);
      setDetectedCard(label);
      setConfidence(conf);
      if (onDetection) onDetection({ ...data, detected_card: label, confidence: conf });
    });

    socket.on("connect_error", (err) => {
      console.warn("[CameraPanel] Socket connect error:", err.message);
    });

    return () => socket.disconnect();
  }, [onDetection, applyClientHold]);

  const parsed = detectedCard ? parseCardLabel(detectedCard) : null;
  const confidencePct = Math.round(confidence * 100);

  const pipelineTitle =
    pipeline != null
      ? `Inference: ${pipeline.unmirror_for_inference ? "flip before model" : "no flip"} · Preview: ${pipeline.mirror_preview ? "mirrored" : "as captured"}`
      : undefined;

  return (
    <div className="camera-panel">
      <div className="ref-panel ref-panel--camera">
        <div className="ref-panel__title ref-panel__title--cyan">Live camera</div>
        <div className="camera-feed">
          {frame ? (
            <img
              src={`data:image/jpeg;base64,${frame}`}
              alt="Live camera feed"
              className="camera-img"
            />
          ) : (
            <div className="camera-placeholder">
              <span>Waiting for camera…</span>
            </div>
          )}
        </div>
      </div>

      <div className="ref-panel ref-panel--detected">
        <div
          className="ref-panel__title ref-panel__title--split"
          title={pipelineTitle}
        >
          <span className="ref-panel__title-detected">Detected</span>
          <span className="ref-panel__title-sep">:</span>
          <span className="ref-panel__title-cardname">
            {detectedCard || "—"}
          </span>
        </div>
        <div className="detected-card-area detected-card-area--ref">
          {parsed ? (
            <>
              <CardDisplay rank={parsed.rank} suit={parsed.suit} />
              {confidence > 0 && (
                <div className="confidence-badge">{confidencePct}%</div>
              )}
            </>
          ) : (
            <div className="empty-detection">No card detected</div>
          )}
        </div>
      </div>
    </div>
  );
}

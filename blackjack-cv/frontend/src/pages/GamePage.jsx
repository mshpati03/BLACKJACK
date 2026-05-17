import React, { useEffect, useState, useCallback, useRef } from "react";
import axios from "axios";
import { io } from "socket.io-client";
import CameraPanel from "../components/CameraPanel";
import CaptureOverlay from "../components/CaptureOverlay";
import BettingPanel from "../components/BettingPanel";
import GameTable from "../components/GameTable";
import PlayerControls from "../components/PlayerControls";
import { addMatchRecord, getPlayerProfile } from "../utils/storage";

export default function GamePage() {
  const [gameState, setGameState] = useState(null);
  const [loadError, setLoadError] = useState(null);
  const socketRef = useRef(null);
  const lastSavedRoundRef = useRef(null);

  const fetchState = useCallback(async () => {
    try {
      const res = await axios.get("/api/state");
      setGameState(res.data);
      setLoadError(null);
    } catch (err) {
      setLoadError(
        "Cannot reach backend. Start Flask from backend/ (default port 5001). " +
          "Set PORT if you use another port and update frontend/package.json proxy."
      );
    }
  }, []);

  useEffect(() => {
    fetchState();
  }, [fetchState]);

  useEffect(() => {
    socketRef.current = io("http://localhost:5001");

    socketRef.current.on("game_state_update", (state) => {
      setGameState(state);
    });

    socketRef.current.on("card_captured", (data) => {
      if (data.hidden) return;

      const newCard = {
        rank: data.rank,
        suit: data.suit,
        label: data.card,
        hidden: false,
      };

      setGameState((prev) => {
        if (!prev) return prev;

        if (data.phase === "waiting_for_player_card") {
          if (data.active_hand === "split") {
            return { ...prev, split_hand: [...(prev.split_hand || []), newCard] };
          }
          return { ...prev, player_hand: [...(prev.player_hand || []), newCard] };
        }

        if (data.phase === "waiting_for_dealer_card") {
          return { ...prev, dealer_hand: [...(prev.dealer_hand || []), newCard] };
        }

        return prev;
      });
    });

    return () => {
      socketRef.current?.disconnect();
    };
  }, []);

  useEffect(() => {
    if (!gameState || gameState.game_phase !== "round_over") return;

    const signature = JSON.stringify({
      result: gameState.result,
      result_amount: gameState.result_amount,
      current_bet: gameState.current_bet,
      balance: gameState.balance,
    });

    if (lastSavedRoundRef.current === signature) return;
    lastSavedRoundRef.current = signature;

    const profile = getPlayerProfile();

    addMatchRecord({
      id: Date.now().toString(),
      playerName: profile.playerName || "Player",
      note: profile.note || "",
      result: gameState.result || "unknown",
      amount: gameState.result_amount || 0,
      bet: gameState.current_bet || 0,
      balance: gameState.balance || 0,
      date: new Date().toLocaleString(),
    });
  }, [gameState]);

  const handleStateChange = useCallback((newState) => {
    setGameState(newState);
  }, []);

  const isBetting = !gameState || gameState.game_phase === "betting";
  const isWaiting = gameState && !!gameState.prompt_message;

  return (
    <div className="app">
      <aside className="left-panel">
        <CameraPanel />
        {isWaiting && (
          <CaptureOverlay promptMessage={gameState.prompt_message} duration={3} />
        )}
      </aside>

      <main className="right-panel">
        {loadError ? (
          <div className="load-error">{loadError}</div>
        ) : (
          <div className={`game-column${isBetting ? " game-column--with-bet" : ""}`}>
            <div className="game-column__play">
              <GameTable
                gameState={gameState}
                onStateChange={handleStateChange}
                isBetting={isBetting}
              >
                {!isBetting && gameState && (
                  <PlayerControls
                    gameState={gameState}
                    onStateChange={handleStateChange}
                    variant="on-table"
                  />
                )}
              </GameTable>
            </div>

            {isBetting && (
              <div className="game-column__bet">
                <BettingPanel
                  balance={gameState?.balance ?? 1000}
                  onBetPlaced={handleStateChange}
                />
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
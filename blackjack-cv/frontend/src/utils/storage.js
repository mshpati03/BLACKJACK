const PLAYER_KEY = "blackjack_player_profile";
const HISTORY_KEY = "blackjack_match_history";

export function savePlayerProfile(profile) {
  localStorage.setItem(PLAYER_KEY, JSON.stringify(profile));
}

export function getPlayerProfile() {
  const raw = localStorage.getItem(PLAYER_KEY);
  return raw ? JSON.parse(raw) : { playerName: "", note: "" };
}

export function getMatchHistory() {
  const raw = localStorage.getItem(HISTORY_KEY);
  return raw ? JSON.parse(raw) : [];
}

export function addMatchRecord(record) {
  const current = getMatchHistory();
  const updated = [record, ...current];
  localStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
  return updated;
}

export function updateMatchRecord(id, updates) {
  const current = getMatchHistory();
  const updated = current.map((item) =>
    item.id === id ? { ...item, ...updates } : item
  );
  localStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
  return updated;
}

export function deleteMatchRecord(id) {
  const current = getMatchHistory();
  const updated = current.filter((item) => item.id !== id);
  localStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
  return updated;
}

export function clearMatchHistory() {
  localStorage.setItem(HISTORY_KEY, JSON.stringify([]));
  return [];
}
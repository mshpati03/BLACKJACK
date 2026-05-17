/**
 * Utility helpers for playing card data.
 */

const SUIT_SYMBOLS = {
  Spades: "♠",
  Hearts: "♥",
  Diamonds: "♦",
  Clubs: "♣",
};

const RED_SUITS = new Set(["Hearts", "Diamonds"]);

const RANKS = [
  "Ace",
  "2",
  "3",
  "4",
  "5",
  "6",
  "7",
  "8",
  "9",
  "10",
  "Jack",
  "Queen",
  "King",
];
const SUITS = ["Spades", "Hearts", "Diamonds", "Clubs"];

const RANK_ALIAS = {
  a: "Ace",
  ace: "Ace",
  j: "Jack",
  jack: "Jack",
  q: "Queen",
  queen: "Queen",
  k: "King",
  king: "King",
  ...Object.fromEntries([2, 3, 4, 5, 6, 7, 8, 9].map((n) => [String(n), String(n)])),
  10: "10",
};

const SUIT_ALIAS = {
  s: "Spades",
  spade: "Spades",
  spades: "Spades",
  h: "Hearts",
  heart: "Hearts",
  hearts: "Hearts",
  d: "Diamonds",
  diamond: "Diamonds",
  diamonds: "Diamonds",
  c: "Clubs",
  club: "Clubs",
  clubs: "Clubs",
};

const SUIT_LOWER = Object.fromEntries(SUITS.map((s) => [s.toLowerCase(), s]));

function canonicalRank(token) {
  if (!token) return null;
  const t = token.trim();
  if (RANKS.includes(t)) return t;
  return RANK_ALIAS[t.toLowerCase()] ?? null;
}

function canonicalSuit(token) {
  if (!token) return null;
  const t = token.trim();
  if (SUITS.includes(t)) return t;
  return SUIT_ALIAS[t.toLowerCase()] ?? SUIT_LOWER[t.toLowerCase()] ?? null;
}

/**
 * Map model-style labels ("10H", "7S") to "Rank of Suit" for the game UI.
 */
export function normalizeCardLabel(label) {
  if (!label || typeof label !== "string") return null;
  const s = label.trim();
  if (!s) return null;
  const lower = s.toLowerCase();
  if (lower.includes(" of ")) {
    const sep = " of ";
    const idx = lower.indexOf(sep);
    const left = s.slice(0, idx).trim();
    const right = s.slice(idx + sep.length).trim();
    const rank = canonicalRank(left);
    const suit = canonicalSuit(right);
    if (rank && suit) return `${rank} of ${suit}`;
    return null;
  }
  const compact = s.replace(/[\s_]+/g, "");
  const m = compact.match(/^([2-9]|10|[ajqk])([shdc])$/i);
  if (!m) return null;
  const r = m[1].toUpperCase();
  const sl = m[2].toUpperCase();
  const rankMap = {
    A: "Ace",
    J: "Jack",
    Q: "Queen",
    K: "King",
    2: "2",
    3: "3",
    4: "4",
    5: "5",
    6: "6",
    7: "7",
    8: "8",
    9: "9",
    10: "10",
  };
  const suitMap = { S: "Spades", H: "Hearts", D: "Diamonds", C: "Clubs" };
  const rank = rankMap[r];
  const suit = suitMap[sl];
  if (!rank || !suit) return null;
  return `${rank} of ${suit}`;
}

/**
 * Parse a label like "Ace of Spades" or compact "AS" into { rank, suit, label }.
 * Returns null if parsing fails.
 */
export function parseCardLabel(label) {
  if (!label || typeof label !== "string") return null;
  const canonical = normalizeCardLabel(label);
  if (!canonical) return null;
  const parts = canonical.split(" of ");
  if (parts.length !== 2) return null;
  const [rank, suit] = parts.map((x) => x.trim());
  return { rank, suit, label: canonical };
}

/** Return the unicode suit symbol for a suit name. */
export function getSuitSymbol(suit) {
  return SUIT_SYMBOLS[suit] || suit;
}

/** Return true if the suit is red (Hearts or Diamonds). */
export function isRedSuit(suit) {
  return RED_SUITS.has(suit);
}

/** Return CSS color string for a card's suit. */
export function getCardColor(suit) {
  return isRedSuit(suit) ? "#cc2222" : "#111111";
}

/**
 * Format a score for display.
 * Returns a string like "18" or "A/11" for soft aces if needed.
 */
export function formatScore(score) {
  if (score == null || score === 0) return "-";
  return String(score);
}

/** Return the display rank abbreviation (e.g. "A" for Ace, "J" for Jack). */
export function rankAbbr(rank) {
  const map = {
    Ace: "A",
    Jack: "J",
    Queen: "Q",
    King: "K",
  };
  return map[rank] || String(rank);
}

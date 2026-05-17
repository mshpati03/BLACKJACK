"""
Map YOLO / dataset class names to the canonical labels the game and UI expect:
  "Rank of Suit" (e.g. "10 of Hearts", "7 of Spades").

Roboflow-style compact names like "10H", "7S", "AS" are normalized here.
"""

from __future__ import annotations

import re
from typing import Optional

RANKS = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]
SUITS = ["Spades", "Hearts", "Diamonds", "Clubs"]

_SUIT_LOWER = {s.lower(): s for s in SUITS}

_RANK_ALIASES = {
    "a": "Ace",
    "ace": "Ace",
    "j": "Jack",
    "jack": "Jack",
    "q": "Queen",
    "queen": "Queen",
    "k": "King",
    "king": "King",
}
for _n in range(2, 10):
    _s = str(_n)
    _RANK_ALIASES[_s] = _s
_RANK_ALIASES["10"] = "10"

_SUIT_ALIASES = {
    "s": "Spades",
    "spade": "Spades",
    "spades": "Spades",
    "h": "Hearts",
    "heart": "Hearts",
    "hearts": "Hearts",
    "d": "Diamonds",
    "diamond": "Diamonds",
    "diamonds": "Diamonds",
    "c": "Clubs",
    "club": "Clubs",
    "clubs": "Clubs",
}

# Rank then suit (e.g. 10H, AS) or suit then rank (e.g. H10, SA)
_COMPACT_RANK_FIRST = re.compile(r"^([2-9]|10|[AJQK])([SHDC])$", re.IGNORECASE)
_COMPACT_SUIT_FIRST = re.compile(r"^([SHDC])([2-9]|10|[AJQK])$", re.IGNORECASE)

_INVISIBLE = re.compile(r"[\u200b-\u200d\ufeff\u2060]")

_RANK_FROM_GROUP = {
    "A": "Ace",
    "J": "Jack",
    "Q": "Queen",
    "K": "King",
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "7": "7",
    "8": "8",
    "9": "9",
    "10": "10",
}
_SUIT_FROM_LETTER = {"S": "Spades", "H": "Hearts", "D": "Diamonds", "C": "Clubs"}


def _normalize_rank_token(token: str) -> Optional[str]:
    if not token:
        return None
    t = token.strip()
    if t in RANKS:
        return t
    return _RANK_ALIASES.get(t.lower())


def _normalize_suit_token(token: str) -> Optional[str]:
    if not token:
        return None
    t = token.strip()
    if t in SUITS:
        return t
    return _SUIT_ALIASES.get(t.lower()) or _SUIT_LOWER.get(t.lower())


def normalize_card_label(raw: Optional[str]) -> Optional[str]:
    """
    Return canonical "Rank of Suit", or None if the string cannot be interpreted.
    """
    if raw is None:
        return None
    s = _INVISIBLE.sub("", str(raw).strip())
    if not s:
        return None

    lower = s.lower()
    if " of " in lower:
        sep = " of "
        idx = lower.index(sep)
        left = s[:idx].strip()
        right = s[idx + len(sep) :].strip()
        rank = _normalize_rank_token(left)
        suit = _normalize_suit_token(right)
        if rank and suit:
            return f"{rank} of {suit}"
        return None

    compact = re.sub(r"[\s_\-]+", "", s)
    m = _COMPACT_RANK_FIRST.match(compact)
    if m:
        r, suit_letter = m.group(1).upper(), m.group(2).upper()
    else:
        m = _COMPACT_SUIT_FIRST.match(compact)
        if not m:
            return None
        suit_letter, r = m.group(1).upper(), m.group(2).upper()

    rank = _RANK_FROM_GROUP.get(r)
    suit = _SUIT_FROM_LETTER.get(suit_letter)
    if not rank or not suit:
        return None
    return f"{rank} of {suit}"

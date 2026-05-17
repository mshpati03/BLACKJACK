"""
Basic blackjack strategy advisor.
Covers hard totals and soft totals.
Pair splitting is out of scope.
"""

# Hard total strategy table.
# Keys are player hard totals (int).
# Values are dicts: dealer upcard (2-11 where 11 = Ace) -> action
_HARD_STRATEGY = {
    # player total: {dealer_upcard: action}
    4:  {2:"HIT",3:"HIT",4:"HIT",5:"HIT",6:"HIT",7:"HIT",8:"HIT",9:"HIT",10:"HIT",11:"HIT"},
    5:  {2:"HIT",3:"HIT",4:"HIT",5:"HIT",6:"HIT",7:"HIT",8:"HIT",9:"HIT",10:"HIT",11:"HIT"},
    6:  {2:"HIT",3:"HIT",4:"HIT",5:"HIT",6:"HIT",7:"HIT",8:"HIT",9:"HIT",10:"HIT",11:"HIT"},
    7:  {2:"HIT",3:"HIT",4:"HIT",5:"HIT",6:"HIT",7:"HIT",8:"HIT",9:"HIT",10:"HIT",11:"HIT"},
    8:  {2:"HIT",3:"HIT",4:"HIT",5:"HIT",6:"HIT",7:"HIT",8:"HIT",9:"HIT",10:"HIT",11:"HIT"},
    9:  {2:"HIT",3:"DOUBLE DOWN",4:"DOUBLE DOWN",5:"DOUBLE DOWN",6:"DOUBLE DOWN",7:"HIT",8:"HIT",9:"HIT",10:"HIT",11:"HIT"},
    10: {2:"DOUBLE DOWN",3:"DOUBLE DOWN",4:"DOUBLE DOWN",5:"DOUBLE DOWN",6:"DOUBLE DOWN",7:"DOUBLE DOWN",8:"DOUBLE DOWN",9:"DOUBLE DOWN",10:"HIT",11:"HIT"},
    11: {2:"DOUBLE DOWN",3:"DOUBLE DOWN",4:"DOUBLE DOWN",5:"DOUBLE DOWN",6:"DOUBLE DOWN",7:"DOUBLE DOWN",8:"DOUBLE DOWN",9:"DOUBLE DOWN",10:"DOUBLE DOWN",11:"DOUBLE DOWN"},
    12: {2:"HIT",3:"HIT",4:"STAND",5:"STAND",6:"STAND",7:"HIT",8:"HIT",9:"HIT",10:"HIT",11:"HIT"},
    13: {2:"STAND",3:"STAND",4:"STAND",5:"STAND",6:"STAND",7:"HIT",8:"HIT",9:"HIT",10:"HIT",11:"HIT"},
    14: {2:"STAND",3:"STAND",4:"STAND",5:"STAND",6:"STAND",7:"HIT",8:"HIT",9:"HIT",10:"HIT",11:"HIT"},
    15: {2:"STAND",3:"STAND",4:"STAND",5:"STAND",6:"STAND",7:"HIT",8:"HIT",9:"HIT",10:"HIT",11:"HIT"},
    16: {2:"STAND",3:"STAND",4:"STAND",5:"STAND",6:"STAND",7:"HIT",8:"HIT",9:"HIT",10:"HIT",11:"HIT"},
    17: {2:"STAND",3:"STAND",4:"STAND",5:"STAND",6:"STAND",7:"STAND",8:"STAND",9:"STAND",10:"STAND",11:"STAND"},
    18: {2:"STAND",3:"STAND",4:"STAND",5:"STAND",6:"STAND",7:"STAND",8:"STAND",9:"STAND",10:"STAND",11:"STAND"},
    19: {2:"STAND",3:"STAND",4:"STAND",5:"STAND",6:"STAND",7:"STAND",8:"STAND",9:"STAND",10:"STAND",11:"STAND"},
    20: {2:"STAND",3:"STAND",4:"STAND",5:"STAND",6:"STAND",7:"STAND",8:"STAND",9:"STAND",10:"STAND",11:"STAND"},
    21: {2:"STAND",3:"STAND",4:"STAND",5:"STAND",6:"STAND",7:"STAND",8:"STAND",9:"STAND",10:"STAND",11:"STAND"},
}

# Soft total strategy table.
# Soft totals: the "other card" value alongside an Ace (e.g. soft 18 = Ace + 7).
# Keys are the non-Ace card value (2-9). Ace+Ace falls back to hard strategy.
_SOFT_STRATEGY = {
    # other_card_value: {dealer_upcard: action}
    2: {2:"HIT",3:"HIT",4:"HIT",5:"DOUBLE DOWN",6:"DOUBLE DOWN",7:"HIT",8:"HIT",9:"HIT",10:"HIT",11:"HIT"},
    3: {2:"HIT",3:"HIT",4:"HIT",5:"DOUBLE DOWN",6:"DOUBLE DOWN",7:"HIT",8:"HIT",9:"HIT",10:"HIT",11:"HIT"},
    4: {2:"HIT",3:"HIT",4:"DOUBLE DOWN",5:"DOUBLE DOWN",6:"DOUBLE DOWN",7:"HIT",8:"HIT",9:"HIT",10:"HIT",11:"HIT"},
    5: {2:"HIT",3:"HIT",4:"DOUBLE DOWN",5:"DOUBLE DOWN",6:"DOUBLE DOWN",7:"HIT",8:"HIT",9:"HIT",10:"HIT",11:"HIT"},
    6: {2:"HIT",3:"DOUBLE DOWN",4:"DOUBLE DOWN",5:"DOUBLE DOWN",6:"DOUBLE DOWN",7:"HIT",8:"HIT",9:"HIT",10:"HIT",11:"HIT"},
    7: {2:"STAND",3:"DOUBLE DOWN",4:"DOUBLE DOWN",5:"DOUBLE DOWN",6:"DOUBLE DOWN",7:"STAND",8:"STAND",9:"HIT",10:"HIT",11:"HIT"},
    8: {2:"STAND",3:"STAND",4:"STAND",5:"STAND",6:"STAND",7:"STAND",8:"STAND",9:"STAND",10:"STAND",11:"STAND"},
    9: {2:"STAND",3:"STAND",4:"STAND",5:"STAND",6:"STAND",7:"STAND",8:"STAND",9:"STAND",10:"STAND",11:"STAND"},
}


def _rank_to_value(rank):
    """Convert a rank string to its blackjack point value for strategy lookup."""
    rank = str(rank).strip()
    face_cards = {"Jack", "Queen", "King"}
    if rank in face_cards:
        return 10
    if rank == "Ace":
        return 11
    try:
        return int(rank)
    except ValueError:
        return None


def _upcard_key(dealer_upcard):
    """Return the dealer upcard key (int 2-11) used in the strategy tables."""
    if not dealer_upcard:
        return None
    rank = dealer_upcard.get("rank") if isinstance(dealer_upcard, dict) else str(dealer_upcard)
    return _rank_to_value(rank)


def get_recommendation(player_hand, dealer_upcard, can_double):
    """
    Returns "HIT", "STAND", or "DOUBLE DOWN" based on basic strategy.
    Returns None if inputs are missing or invalid.
    """
    if not player_hand or not dealer_upcard:
        return None

    upcard_val = _upcard_key(dealer_upcard)
    if upcard_val is None:
        return None

    # Determine if soft hand (contains at least one Ace counted as 11)
    aces = [c for c in player_hand if str(c.get("rank", "")).strip() == "Ace"]
    non_ace_values = [_rank_to_value(c.get("rank", "")) for c in player_hand
                      if str(c.get("rank", "")).strip() != "Ace"]

    is_soft = len(aces) >= 1

    # Calculate hard total (Aces as 1)
    hard_total = sum(
        (_rank_to_value(c.get("rank", "")) or 0) if str(c.get("rank", "")).strip() != "Ace" else 1
        for c in player_hand
    )
    # Add aces optimally
    for _ in aces:
        if hard_total + 10 <= 21:
            hard_total += 10
        else:
            hard_total += 0  # already counted as 1 above

    # Soft strategy lookup when exactly one Ace is counted as 11
    if is_soft and len(aces) == 1 and len(non_ace_values) == 1:
        other_val = non_ace_values[0]
        if other_val and other_val in _SOFT_STRATEGY:
            action = _SOFT_STRATEGY[other_val].get(upcard_val, "HIT")
            return _resolve_double(action, can_double, player_hand)

    # Hard strategy lookup
    clamped = min(max(hard_total, 4), 21)
    row = _HARD_STRATEGY.get(clamped)
    if row is None:
        return "STAND"

    action = row.get(upcard_val, "HIT")
    return _resolve_double(action, can_double, player_hand)


def _resolve_double(action, can_double, player_hand):
    """If DOUBLE DOWN is recommended but not allowed, fall back to HIT (common fallback)."""
    if action == "DOUBLE DOWN" and not can_double:
        return "HIT"
    return action

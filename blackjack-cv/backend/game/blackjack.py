"""
Single-player Blackjack engine with split support.
"""

import random
import re
from game.card_labels import RANKS, SUITS, normalize_card_label
from game.strategy import get_recommendation


STARTING_BALANCE = 1000
MINIMUM_BET = 5
RESHUFFLE_THRESHOLD = 15


def _build_deck():
    return [{"rank": r, "suit": s, "label": f"{r} of {s}"} for r in RANKS for s in SUITS]


def _card_value(rank):
    if rank in ("Jack", "Queen", "King"):
        return 10
    if rank == "Ace":
        return 11
    return int(rank)


def _parse_label(label):
    if label is None:
        raise ValueError("Invalid card label: (missing)")
    raw_display = label
    cleaned = str(label).strip()
    cleaned = re.sub(r"[\u200b-\u200d\ufeff\u2060]", "", cleaned)
    canonical = normalize_card_label(cleaned)
    if not canonical:
        raise ValueError(f"Invalid card label: {raw_display}")
    parts = canonical.split(" of ", 1)
    if len(parts) != 2:
        raise ValueError(f"Invalid card label: {raw_display}")
    rank, suit = parts[0].strip(), parts[1].strip()
    return {"rank": rank, "suit": suit, "label": canonical, "hidden": False}


class BlackjackGame:
    def __init__(self):
        self._deck = _build_deck()
        self._shuffle()

        self.player_hand = []
        self.dealer_hand = []
        self.used_cards = []

        self.split_hand = []
        self.split_bet = 0
        self.active_hand = "player"
        self.split_result = None
        self.split_result_amount = 0

        self.balance = STARTING_BALANCE
        self.current_bet = 0

        self.game_phase = "betting"
        self.result = None
        self.result_amount = 0
        self.last_detected_card = None
        self.last_detection_confidence = 0.0
        self.prompt_message = None
        self.strategy_recommendation = None

        self._predraw_hidden_card()

    # ------------------------------------------------------------------
    # Deck helpers
    # ------------------------------------------------------------------

    def _shuffle(self):
        random.shuffle(self._deck)

    def _reshuffle_if_needed(self):
        if len(self._deck) < RESHUFFLE_THRESHOLD:
            print("[Blackjack] Reshuffling deck...")
            self._deck = _build_deck()
            self._shuffle()

    def _remove_from_deck(self, label):
        for i, card in enumerate(self._deck):
            if card["label"] == label:
                self._deck.pop(i)
                return

    def _draw_random_card(self):
        self._reshuffle_if_needed()
        for i, card in enumerate(self._deck):
            if card["label"] not in self.used_cards:
                self._deck.pop(i)
                return {
                    "rank": card["rank"],
                    "suit": card["suit"],
                    "label": card["label"],
                    "hidden": False,
                }
        self._deck = _build_deck()
        self._shuffle()
        card = self._deck.pop(0)
        return {"rank": card["rank"], "suit": card["suit"], "label": card["label"], "hidden": False}

    def _predraw_hidden_card(self):
        card = self._draw_random_card()
        self.dealer_hand = [{**card, "hidden": True}]
        self.used_cards = [card["label"]]

    # ------------------------------------------------------------------
    # State reset
    # ------------------------------------------------------------------

    def reset_round_state(self):
        self.player_hand = []
        self.dealer_hand = []
        self.used_cards = []
        self.split_hand = []
        self.split_bet = 0
        self.active_hand = "player"
        self.split_result = None
        self.split_result_amount = 0
        self.current_bet = 0
        self.game_phase = "betting"
        self.result = None
        self.result_amount = 0
        self.last_detected_card = None
        self.last_detection_confidence = 0.0
        self.prompt_message = None
        self.strategy_recommendation = None
        self._reshuffle_if_needed()
        self._predraw_hidden_card()

    # ------------------------------------------------------------------
    # Bet
    # ------------------------------------------------------------------

    def place_bet(self, amount):
        if self.game_phase != "betting":
            raise ValueError("Can only place a bet during betting phase.")
        if amount < MINIMUM_BET:
            raise ValueError(f"Minimum bet is ${MINIMUM_BET}.")
        if amount > self.balance:
            raise ValueError("Insufficient balance.")
        self.current_bet = amount
        self.balance -= amount

    # ------------------------------------------------------------------
    # Card management
    # ------------------------------------------------------------------

    def _validate_and_register(self, label):
        if label in self.used_cards:
            raise ValueError(f"Duplicate card detected: '{label}' is already in play.")
        self.used_cards.append(label)
        self._remove_from_deck(label)

    def add_card_to_player(self, card_dict):
        self._validate_and_register(card_dict["label"])
        self.player_hand.append(card_dict)
        self.last_detected_card = card_dict["label"]

    def add_card_to_split(self, card_dict):
        self._validate_and_register(card_dict["label"])
        self.split_hand.append(card_dict)
        self.last_detected_card = card_dict["label"]

    def add_card_to_dealer(self, card_dict, hidden=False):
        self._validate_and_register(card_dict["label"])
        card_dict = {**card_dict, "hidden": hidden}
        self.dealer_hand.append(card_dict)
        self.last_detected_card = card_dict["label"]

    def _add_random_dealer_card_hidden(self, card_dict):
        self.used_cards.append(card_dict["label"])
        self.dealer_hand.append({**card_dict, "hidden": True})
        self.last_detected_card = card_dict["label"]

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    def calculate_score(self, hand):
        total = 0
        aces = 0
        for card in hand:
            if card.get("hidden"):
                continue
            rank = card["rank"]
            if rank == "Ace":
                aces += 1
                total += 11
            else:
                total += _card_value(rank)
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    def is_soft_hand(self, hand):
        total = 0
        aces = 0
        for card in hand:
            if card.get("hidden"):
                continue
            if card["rank"] == "Ace":
                aces += 1
                total += 11
            else:
                total += _card_value(card["rank"])
        reductions = 0
        while total > 21 and aces > reductions:
            total -= 10
            reductions += 1
        return aces > reductions

    def can_double_down(self):
        if self.game_phase != "player_turn":
            return False
        if self.active_hand == "split":
            return len(self.split_hand) == 2 and self.balance >= self.split_bet
        return len(self.player_hand) == 2 and self.balance >= self.current_bet

    def can_split(self):
        return (
            len(self.player_hand) == 2
            and not self.split_hand
            and self.game_phase == "player_turn"
            and self.active_hand == "player"
            and self.balance >= self.current_bet
            and _card_value(self.player_hand[0]["rank"]) == _card_value(self.player_hand[1]["rank"])
        )

    # ------------------------------------------------------------------
    # Capture helper
    # ------------------------------------------------------------------

    def _capture_card(self, capture_card_callback, prompt):
        self.prompt_message = prompt
        result = capture_card_callback()
        if result is None:
            raise RuntimeError("No stable card detected. Please try again.")
        label = result["card"]
        confidence = result["confidence"]
        card = _parse_label(label)
        self.last_detected_card = card["label"]
        self.last_detection_confidence = confidence
        return card

    # ------------------------------------------------------------------
    # New round
    # ------------------------------------------------------------------

    def new_round(self, capture_card_callback):
        self.player_hand = []
        existing_hidden = self.dealer_hand[0] if self.dealer_hand else None
        self.dealer_hand = []
        self.used_cards = []
        self.split_hand = []
        self.split_bet = 0
        self.active_hand = "player"
        self.split_result = None
        self.split_result_amount = 0

        # Hidden dealer card first
        if existing_hidden:
            hidden_card = existing_hidden
        else:
            hidden_card = self._draw_random_card()
        self._add_random_dealer_card_hidden(hidden_card)
        print(f"[Blackjack] Dealer hidden card: {hidden_card['label']} (face-down)")

        # Player first card — camera
        self.game_phase = "waiting_for_player_card"
        c1 = self._capture_card(capture_card_callback, "Show your first card to camera")
        self.add_card_to_player(c1)

        # Player second card — camera
        self.game_phase = "waiting_for_player_card"
        c3 = self._capture_card(capture_card_callback, "Show your second card to camera")
        self.add_card_to_player(c3)

        # Dealer upcard — camera
        self.game_phase = "waiting_for_dealer_card"
        c4 = self._capture_card(capture_card_callback, "Show dealer upcard to camera")
        self.add_card_to_dealer(c4, hidden=False)

        self.prompt_message = None
        self.game_phase = "player_turn"
        self._update_strategy()

        if self.calculate_score(self.player_hand) == 21:
            dealer_score = self.calculate_score(self.dealer_hand)
            if dealer_score == 21:
                self._end_round("push", 0)
            else:
                payout = int(self.current_bet * 1.5)
                self._end_round("blackjack", payout)

    # ------------------------------------------------------------------
    # Player actions
    # ------------------------------------------------------------------

    def hit(self, capture_card_callback):
        if self.game_phase != "player_turn":
            raise ValueError("Cannot hit right now.")
        self.game_phase = "waiting_for_player_card"
        card = self._capture_card(capture_card_callback, "Show card to camera")

        if self.active_hand == "split":
            self.add_card_to_split(card)
            self.prompt_message = None
            if self.calculate_score(self.split_hand) > 21:
                self.split_result = "bust"
                self.split_result_amount = -self.split_bet
                self.dealer_play(capture_card_callback)
            else:
                self.game_phase = "player_turn"
                self._update_strategy()
        else:
            self.add_card_to_player(card)
            self.prompt_message = None
            if self.calculate_score(self.player_hand) > 21:
                if self.split_hand and self.split_result is None:
                    self.active_hand = "split"
                    self.game_phase = "player_turn"
                    self._update_strategy()
                else:
                    self._end_round("bust", -self.current_bet)
            else:
                self.game_phase = "player_turn"
                self._update_strategy()

    def stand(self, capture_card_callback):
        if self.game_phase != "player_turn":
            raise ValueError("Cannot stand right now.")
        self.strategy_recommendation = None

        if self.active_hand == "player" and self.split_hand and self.split_result is None:
            self.active_hand = "split"
            self.game_phase = "player_turn"
            self._update_strategy()
        else:
            self.dealer_play(capture_card_callback)

    def double_down(self, capture_card_callback):
        if not self.can_double_down():
            raise ValueError("Cannot double down.")

        if self.active_hand == "split":
            self.balance -= self.split_bet
            self.split_bet *= 2
        else:
            self.balance -= self.current_bet
            self.current_bet *= 2

        self.game_phase = "waiting_for_player_card"
        card = self._capture_card(capture_card_callback, "Show card to camera (double down)")

        if self.active_hand == "split":
            self.add_card_to_split(card)
            self.prompt_message = None
            if self.calculate_score(self.split_hand) > 21:
                self.split_result = "bust"
                self.split_result_amount = -self.split_bet
            self.dealer_play(capture_card_callback)
        else:
            self.add_card_to_player(card)
            self.prompt_message = None
            if self.calculate_score(self.player_hand) > 21:
                if self.split_hand and self.split_result is None:
                    self.active_hand = "split"
                    self.game_phase = "player_turn"
                    self._update_strategy()
                else:
                    self._end_round("bust", -self.current_bet)
            else:
                if self.split_hand and self.split_result is None:
                    self.active_hand = "split"
                    self.game_phase = "player_turn"
                    self._update_strategy()
                else:
                    self.dealer_play(capture_card_callback)

    def split(self, capture_card_callback):
        if not self.can_split():
            raise ValueError("Cannot split.")

        self.balance -= self.current_bet
        self.split_bet = self.current_bet

        second_card = self.player_hand.pop(1)
        self.split_hand = [second_card]

        # Draw card for main hand
        self.game_phase = "waiting_for_player_card"
        self.active_hand = "player"
        c1 = self._capture_card(capture_card_callback, "Show card for first split hand")
        self.add_card_to_player(c1)

        # Draw card for split hand
        self.game_phase = "waiting_for_player_card"
        self.active_hand = "split"
        c2 = self._capture_card(capture_card_callback, "Show card for second split hand")
        self.add_card_to_split(c2)

        self.active_hand = "player"
        self.game_phase = "player_turn"
        self._update_strategy()

    # ------------------------------------------------------------------
    # Dealer play
    # ------------------------------------------------------------------

    def dealer_play(self, capture_card_callback):
        self.game_phase = "dealer_turn"
        for card in self.dealer_hand:
            card["hidden"] = False
        while self.calculate_score(self.dealer_hand) < 17:
            card = self._capture_card(
                capture_card_callback,
                f"Show dealer card to camera (dealer score: {self.calculate_score(self.dealer_hand)})"
            )
            self.add_card_to_dealer(card, hidden=False)
        self.prompt_message = None
        self.resolve_round()

    # ------------------------------------------------------------------
    # Round resolution
    # ------------------------------------------------------------------

    def resolve_round(self):
        dealer_score = self.calculate_score(self.dealer_hand)

        def resolve_hand(score, bet):
            if score > 21:
                return "bust", 0
            elif dealer_score > 21 or score > dealer_score:
                return "player_wins", bet * 2
            elif score == dealer_score:
                return "push", bet
            else:
                return "dealer_wins", 0

        player_score = self.calculate_score(self.player_hand)
        main_result, main_payout = resolve_hand(player_score, self.current_bet)
        self.balance += main_payout
        main_net = main_payout - self.current_bet

        if self.split_hand:
            split_score = self.calculate_score(self.split_hand)
            if self.split_result == "bust":
                split_payout = 0
            else:
                self.split_result, split_payout = resolve_hand(split_score, self.split_bet)
            self.balance += split_payout
            self.split_result_amount = split_payout - self.split_bet
            self.result_amount = main_net + self.split_result_amount
        else:
            self.result_amount = main_net

        self.result = main_result
        self.game_phase = "round_over"
        self.strategy_recommendation = None
        for card in self.dealer_hand:
            card["hidden"] = False

    def _end_round(self, result, result_amount):
        self.result = result
        self.result_amount = result_amount
        if result == "push":
            self.balance += self.current_bet
        elif result_amount > 0:
            self.balance += self.current_bet + result_amount
        self.game_phase = "round_over"
        self.strategy_recommendation = None
        for card in self.dealer_hand:
            card["hidden"] = False

    # ------------------------------------------------------------------
    # Strategy
    # ------------------------------------------------------------------

    def _update_strategy(self):
        if self.game_phase != "player_turn":
            self.strategy_recommendation = None
            return
        upcard = next((c for c in self.dealer_hand if not c.get("hidden")), None)
        active = self.split_hand if self.active_hand == "split" else self.player_hand
        self.strategy_recommendation = get_recommendation(
            active, upcard, self.can_double_down()
        )

    # ------------------------------------------------------------------
    # State serialization
    # ------------------------------------------------------------------

    def get_state(self):
        player_score = self.calculate_score(self.player_hand)
        split_score = self.calculate_score(self.split_hand) if self.split_hand else None
        visible_dealer_cards = [c for c in self.dealer_hand if not c.get("hidden")]
        dealer_score_visible = self.calculate_score(visible_dealer_cards) if visible_dealer_cards else 0
        dealer_score_final = None
        if self.game_phase in ("dealer_turn", "round_over"):
            dealer_score_final = self.calculate_score(self.dealer_hand)

        return {
            "player_hand": self.player_hand,
            "dealer_hand": self.dealer_hand,
            "split_hand": self.split_hand,
            "player_score": player_score,
            "split_score": split_score,
            "dealer_score_visible": dealer_score_visible,
            "dealer_score_final": dealer_score_final,
            "balance": self.balance,
            "current_bet": self.current_bet,
            "split_bet": self.split_bet,
            "active_hand": self.active_hand,
            "game_phase": self.game_phase,
            "result": self.result,
            "result_amount": self.result_amount,
            "split_result": self.split_result,
            "split_result_amount": self.split_result_amount,
            "used_cards": self.used_cards,
            "last_detected_card": self.last_detected_card,
            "last_detection_confidence": self.last_detection_confidence,
            "prompt_message": self.prompt_message,
            "can_double": self.can_double_down(),
            "can_split": self.can_split(),
            "strategy_recommendation": self.strategy_recommendation,
        }

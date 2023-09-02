from Enums import State, Action


state_action_strategy = {
    State.CO: [
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 2, 7],  # not suit
        [1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 2, 7],  # suit
    ],

    State.DE: [
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2, 8],  # not suit
        [1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 4, 4],  # suit
    ],
    State.DE_CO: [
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 4],  # not suit
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 2, 5],  # suit
    ],

    State.SB: [
        [1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 3, 5, 1],  # not suit
        [1, 0, 0, 2, 0, 1, 0, 1, 2, 2, 2, 1, 1],  # suit
    ],
    State.SB_CO: [
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 5],  # not suit
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 2, 6],  # suit
    ],
    State.SB_DE: [
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 5],  # not suit
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 9],  # suit
    ],
    State.SB_CO_DE: [
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 3],  # not suit
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 2, 2],  # suit
    ],

    State.BB_CO: [
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 6],  # not suit
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2, 8],  # suit
    ],
    State.BB_DE: [
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 9],  # not suit
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 7],  # suit
    ],
    State.BB_SB: [
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 4, 4],  # not suit
        [1, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 5, 1],  # suit
    ],
    State.BB_CO_DE: [
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 2],  # not suit
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1],  # suit
    ],
    State.BB_CO_SB: [
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 3],  # not suit
        [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 2],  # suit
    ],
    State.BB_DE_SB: [
        [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2],  # not suit
        [0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 3],  # suit
    ],
    State.BB_CO_DE_SB: [
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 2],  # not suit
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0],  # suit
    ],

}


def decide_action(c1, c2, state):
    vector = state_action_strategy[state][int(c1.suit == c2.suit)]

    max_rank = max(c1.number.value, c2.number.value)
    min_rank = min(c1.number.value, c2.number.value)
    d = max_rank - min_rank
    s = sum(vector[0:max_rank-1])

    if s > d:
        return Action.AllIn

    return Action.Fold







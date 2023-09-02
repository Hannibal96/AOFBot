from enum import Enum


class Location(Enum):
    Bottom = 0
    Left = 1
    Top = 2
    Right = 3


class Position(Enum):
    CutOff = 0
    Dealer = 1
    SmallBlind = 2
    BigBlind = 3
    SittingOut = -1

    def __str__(self):
        if self.value == 0:
            return "CO"
        if self.value == 1:
            return "DE"
        if self.value == 2:
            return "SB"
        if self.value == 3:
            return "BB"
        if self.value == -1:
            return "XX"


class Action(Enum):
    UnDecided = 0
    Fold = 1
    AllIn = 2


class PreviousAction(Enum):
    Empty = 0
    OneRaiseCutoff = 1
    OneRaiseDealer = 2
    OneRaiseSmallBlind = 3
    TwoRaiseCutoffDealer = 4
    TwoRaiseCutoffSmallBlind = 5
    TwoRaiseDealerSmallBlind = 6
    ThreeRaise = 6


class State(Enum):
    CO = 0
    DE = 1
    DE_CO = 2
    SB = 3
    SB_CO = 4
    SB_DE = 5
    SB_CO_DE = 6
    BB_CO = 7
    BB_DE = 8
    BB_SB = 9
    BB_CO_DE = 10
    BB_CO_SB = 11
    BB_DE_SB = 12
    BB_CO_DE_SB = 13


class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class Suits(Enum):
    Heart = 0
    Diamond = 1
    Spade = 2
    Club = 3


class Number(Enum):
    Ace = 14
    Duce = 2
    Three = 3
    Four = 4
    Five = 5
    Six = 6
    Seven = 7
    Eight = 8
    Nine = 9
    Ten = 10
    Jack = 11
    Queen = 12
    King = 13
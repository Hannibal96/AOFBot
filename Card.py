from Enums import Color, Suits, Number


class Card:
    def __init__(self, number, suit):
        if number not in Number:
            assert False
        if suit not in Suits:
            assert False
        self.number = number
        self.suit = suit

    def __eq__(self, other):
        return self.number.value == other.number.value and self.suit.value == other.suit.value

    def __lt__(self, other):
        if self.number.value == other.number.value:
            return self.suit.value < other.suit.value
        return self.number.value < other.number.value

    def __str__(self):
        suits_symbols = [Color.RED+'♥'+Color.END, Color.YELLOW+'♦'+Color.END, Color.PURPLE+'♠'+Color.END, Color.GREEN+'♣'+Color.END]
        numbers_symbols = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        return '|'+numbers_symbols[self.number.value-2]+suits_symbols[self.suit.value]+'|'



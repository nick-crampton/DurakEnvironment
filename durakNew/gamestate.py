from durakNew.utils.printCardLists import printCardLists
class GameState:
    def __init__(self):
        self.trumpSuit = None
        ##self.attackingCards = []
        ##self.defendingCards = []

        self.attackDefensePairs = []
        self.playerHands = {}
        self.talon = []
        self.discardPile = []
        self.activeRole = None
    
    def undefendedCards(self):
        return [pair[0] for pair in self.attackDefensePairs if pair[1] is None]

    def __str__(self):
        output = []

        ##Trump Suit
        output.append(f"Trump Suit: {self.trumpSuit}")

        ##Attacking Cards
        output.append("Attacking Cards:")
        output.extend(printCardLists(self.attackingCards))

        ##Defending Cards
        output.append("Defending Cards:")
        output.extend(printCardLists(self.defendingCards))

        ##Player Hands
        output.append("Player Hands:")
        for player, hand in self.playerHands.items():
            output.append(f"  Player {player}:")
            output.extend(printCardLists(hand))

        ##Talon
        output.append("Talon:")
        output.extend(printCardLists(self.talon))

        ##Discard Pile
        output.append("Discard Pile:")
        output.extend(printCardLists(self.discardPile))

        ##Role
        output.append(f"Active Role: {self.activeRole}")

        return "\n".join(output)
from durakNew.utils.printCardLists import printCardLists
class GameState:
    def __init__(self):
        self.trumpSuit = None
        self.attackDefensePairs = []
        self.talon = []
        self.discardPile = []
        self.maxTalon = 0
        self.maxHand = 0

        self.printGameplay = True
    
    def undefendedCards(self):
        return [pair[0] for pair in self.attackDefensePairs if pair[1] is None]

    def getAttackCards(self):
        return [pair[0] for pair in self.attackDefensePairs]
    
    def getDefenseCards(self):
        return [pair[1] for pair in self.attackDefensePairs if pair[1] is not None]
    
    def getTalonCount(self):
        return len(self.talon)
    
    def getDiscardCount(self):
        return len(self.discardPile)

    def __str__(self):
        output = []

        ##Trump Suit
        output.append(f"Trump Suit: {self.trumpSuit}")

        output.extend(printCardLists(self.defendingCards))

        ##Talon
        output.append("Talon:")
        output.extend(printCardLists(self.talon))

        ##Discard Pile
        output.append("Discard Pile:")
        output.extend(printCardLists(self.discardPile))

        ##Role
        output.append(f"Active Role: {self.activeRole}")

        return "\n".join(output)

class GameState:
    def __init__(self):
        self.trumpSuit = None
        self.attackingCards = []
        self.defendingCards = []
        self.playerHands = {}
        self.talon = []
        self.discardPile = []
        self.activeRole = None
       